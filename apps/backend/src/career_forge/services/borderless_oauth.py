"""Borderless OAuth sign-in. Career Forge still mints the session JWT.

Spec: docs/product/BORDERLESS-OAUTH.md
"""

from __future__ import annotations

import base64
import hashlib
import json
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol
from urllib import error, parse, request

import jwt
from jwt.algorithms import RSAAlgorithm
from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import (
    BorderlessEmailUnverifiedError,
    BorderlessIdentityMismatchError,
    BorderlessOAuthFailedError,
    BorderlessSigninUnavailableError,
)
from career_forge.services.borderless_profile import (
    MEMBERSHIP_RETRY_AFTER,
    open_access_token,
    seal_access_token,
)
from career_forge.services.career_forge_password import claim_pending_signup

ISSUER = "https://api.borderlesscoding.com/api/auth"
REDIRECT_URI = "https://labs.borderlesscoding.com/career-forge/auth/borderless/callback"
SCOPES = "openid profile email offline_access"
_INCLUDED = frozenset({"base", "psp"})
_COOKIE_STATE = "cf_borderless_oauth_state"
_COOKIE_NONCE = "cf_borderless_oauth_nonce"
_COOKIE_VERIFIER = "cf_borderless_oauth_verifier"
_COOKIE_TTL_SECONDS = 600
_HTTP_TIMEOUT = 5.0


@dataclass(frozen=True)
class OAuthEndpoints:
    authorization_endpoint: str
    token_endpoint: str
    jwks_uri: str


class OAuthClient(Protocol):
    def discovery(self) -> OAuthEndpoints: ...

    def token(self, form: dict[str, str]) -> tuple[int, dict]: ...

    def jwks(self) -> dict: ...


def oauth_configured() -> bool:
    return bool(
        settings.borderless_oauth_client_id.strip()
        and settings.borderless_oauth_client_secret.strip()
        and settings.borderless_token_encryption_key.strip()
    )


def cookie_params() -> dict[str, object]:
    local = settings.env.lower() in {"local", "test"}
    return {
        "httponly": True,
        "secure": not local,
        "samesite": "lax",
        "path": "/" if local else "/career-forge",
        "max_age": _COOKIE_TTL_SECONDS,
    }


def authorization_request() -> tuple[str, dict[str, str]]:
    """Return the authorize URL and the cookie values that must travel with it."""
    if not oauth_configured():
        raise BorderlessOAuthFailedError()
    endpoints = get_borderless_oauth_client().discovery()
    state = secrets.token_urlsafe(32)
    nonce = secrets.token_urlsafe(32)
    verifier = secrets.token_urlsafe(64)
    challenge = _code_challenge(verifier)
    query = parse.urlencode(
        {
            "response_type": "code",
            "client_id": settings.borderless_oauth_client_id.strip(),
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
            "nonce": nonce,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    url = f"{endpoints.authorization_endpoint}?{query}"
    return url, {
        _COOKIE_STATE: state,
        _COOKIE_NONCE: nonce,
        _COOKIE_VERIFIER: verifier,
    }


def complete_authorization(
    session: Session,
    *,
    code: str,
    state: str,
    cookie_state: str | None,
    cookie_nonce: str | None,
    cookie_verifier: str | None,
) -> dict[str, str | int]:
    if not oauth_configured():
        raise BorderlessOAuthFailedError()
    if not _same(cookie_state, state) or not cookie_nonce or not cookie_verifier:
        raise BorderlessOAuthFailedError()
    status, payload = get_borderless_oauth_client().token(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": cookie_verifier,
        }
    )
    if status != 200:
        raise BorderlessOAuthFailedError()
    id_token = payload.get("id_token")
    refresh_token = payload.get("refresh_token")
    if not isinstance(id_token, str) or not isinstance(refresh_token, str):
        raise BorderlessOAuthFailedError()
    claims = verify_id_token(id_token, nonce=cookie_nonce)
    user = _bind_user(session, claims)
    user.borderless_refresh_token = seal_access_token(refresh_token.strip())
    user.borderless_access_token = None
    user.borderless_access_unrenewable = False
    user.membership_read_failed_at = None
    _apply_membership(user, claims)
    claim_pending_signup(session, user)
    session.commit()
    assert user.external_id
    return _token_payload(user.external_id)


def sync_oauth_membership(user: User, *, force: bool = False) -> None:
    """Refresh membership from a new id token. Keeps the last label on failure."""
    if not user.borderless_refresh_token or not oauth_configured():
        return
    now = datetime.now(timezone.utc)
    if not force:
        if user.borderless_access_unrenewable:
            return
        failed_at = user.membership_read_failed_at
        if failed_at is not None:
            if failed_at.tzinfo is None:
                failed_at = failed_at.replace(tzinfo=timezone.utc)
            if now - failed_at < MEMBERSHIP_RETRY_AFTER:
                return
    refresh_token = open_access_token(user.borderless_refresh_token)
    if refresh_token is None:
        user.borderless_access_unrenewable = True
        user.membership_read_failed_at = None
        return
    try:
        status, payload = get_borderless_oauth_client().token(
            {"grant_type": "refresh_token", "refresh_token": refresh_token}
        )
    except BorderlessSigninUnavailableError:
        user.membership_read_failed_at = now
        return
    error = payload.get("error") if isinstance(payload, dict) else None
    if error == "invalid_grant":
        user.borderless_access_unrenewable = True
        user.membership_read_failed_at = None
        return
    if status != 200:
        user.membership_read_failed_at = now
        return
    id_token = payload.get("id_token")
    if not isinstance(id_token, str):
        user.membership_read_failed_at = now
        return
    try:
        claims = verify_id_token(id_token, nonce=None)
    except BorderlessOAuthFailedError:
        user.membership_read_failed_at = now
        return
    rotated = payload.get("refresh_token")
    if not isinstance(rotated, str) or not rotated.strip():
        user.membership_read_failed_at = now
        return
    user.borderless_refresh_token = seal_access_token(rotated.strip())
    _apply_membership(user, claims)
    user.borderless_access_unrenewable = False
    user.membership_read_failed_at = None


def verify_id_token(id_token: str, *, nonce: str | None) -> dict:
    try:
        header = jwt.get_unverified_header(id_token)
    except jwt.PyJWTError as exc:
        raise BorderlessOAuthFailedError() from exc
    key = _jwk_for(header.get("kid"), get_borderless_oauth_client().jwks())
    try:
        claims = jwt.decode(
            id_token,
            key,
            algorithms=["RS256"],
            audience=settings.borderless_oauth_client_id.strip(),
            issuer=ISSUER,
        )
    except jwt.PyJWTError as exc:
        raise BorderlessOAuthFailedError() from exc
    if nonce is not None and claims.get("nonce") != nonce:
        raise BorderlessOAuthFailedError()
    if not isinstance(claims, dict):
        raise BorderlessOAuthFailedError()
    return claims


def _jwk_for(kid: object, document: dict):
    keys = document.get("keys") if isinstance(document, dict) else None
    if not isinstance(keys, list):
        raise BorderlessOAuthFailedError()
    for jwk in keys:
        if not isinstance(jwk, dict):
            continue
        if kid is None or jwk.get("kid") == kid:
            return RSAAlgorithm.from_jwk(json.dumps(jwk))
    raise BorderlessOAuthFailedError()


def _apply_membership(user: User, claims: dict) -> None:
    raw = claims.get("borderless_membership")
    key = raw.strip().lower() if isinstance(raw, str) else ""
    if key in _INCLUDED:
        user.membership_label = key
        user.membership_entitled = True
        return
    user.membership_label = "external"
    user.membership_entitled = False


def _bind_user(session: Session, claims: dict) -> User:
    if claims.get("email_verified") is not True:
        raise BorderlessEmailUnverifiedError()
    sub = claims.get("sub")
    email = _email(claims.get("email"))
    if not isinstance(sub, str) or not sub.strip() or email is None:
        raise BorderlessOAuthFailedError()
    sub = sub.strip()
    name = claims.get("name")
    display = name.strip() if isinstance(name, str) and name.strip() else None
    user = session.scalar(select(User).where(User.borderless_user_id == sub))
    is_new = False
    if user is None:
        by_email = session.scalar(select(User).where(User.email == email))
        if by_email is not None:
            if by_email.borderless_user_id and by_email.borderless_user_id != sub:
                raise BorderlessIdentityMismatchError()
            by_email.borderless_user_id = sub
            user = by_email
        else:
            is_new = True
            user = ensure_user(
                session,
                f"user-{uuid.uuid4()}",
                display_name=display,
            )
            user.email = email
            user.borderless_user_id = sub
    elif email != (user.email or "").lower():
        other = session.scalar(select(User).where(User.email == email))
        if other is None:
            user.email = email
    if user.external_id is None:
        user.external_id = f"user-{uuid.uuid4()}"
    if display and (is_new or _is_placeholder_name(user)):
        user.display_name = display[:120]
    return user


def _is_placeholder_name(user: User) -> bool:
    if not user.external_id:
        return False
    return user.display_name == user.external_id.replace("-", " ").title()


def _email(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    email = value.strip().lower()
    return email or None


def _same(left: str | None, right: str | None) -> bool:
    if not left or not right or len(left) != len(right):
        return False
    return secrets.compare_digest(left, right)


def _code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode()


def _token_payload(external_id: str) -> dict[str, str | int]:
    return {
        "access_token": get_auth_provider().mint_email(external_id),
        "token_type": "bearer",
        "external_id": external_id,
        "provider": EMAIL_PROVIDER,
        "expires_in": settings.jwt_anon_ttl_days * 24 * 3600,
    }


class HttpOAuthClient:
    def __init__(self) -> None:
        self._endpoints: OAuthEndpoints | None = None

    def discovery(self) -> OAuthEndpoints:
        if self._endpoints is None:
            url = f"{ISSUER}/.well-known/openid-configuration"
            document = _get_json(url)
            try:
                self._endpoints = OAuthEndpoints(
                    authorization_endpoint=str(document["authorization_endpoint"]),
                    token_endpoint=str(document["token_endpoint"]),
                    jwks_uri=str(document["jwks_uri"]),
                )
            except KeyError as exc:
                raise BorderlessSigninUnavailableError() from exc
        return self._endpoints

    def token(self, form: dict[str, str]) -> tuple[int, dict]:
        endpoints = self.discovery()
        body = parse.urlencode(form).encode()
        req = request.Request(
            endpoints.token_endpoint,
            data=body,
            method="POST",
            headers={
                "Authorization": _basic_auth(),
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        try:
            with request.urlopen(req, timeout=_HTTP_TIMEOUT) as response:
                raw = response.read().decode()
                status = response.status
        except error.HTTPError as exc:
            raw = exc.read().decode()
            status = exc.code
        except (error.URLError, TimeoutError) as exc:
            raise BorderlessSigninUnavailableError() from exc
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError as exc:
            raise BorderlessSigninUnavailableError() from exc
        if not isinstance(payload, dict):
            raise BorderlessSigninUnavailableError()
        return status, payload

    def jwks(self) -> dict:
        return _get_json(self.discovery().jwks_uri)


def _basic_auth() -> str:
    client_id = parse.quote(settings.borderless_oauth_client_id.strip(), safe="")
    secret = parse.quote(settings.borderless_oauth_client_secret.strip(), safe="")
    token = base64.b64encode(f"{client_id}:{secret}".encode()).decode()
    return f"Basic {token}"


def _get_json(url: str) -> dict:
    req = request.Request(url, headers={"Accept": "application/json"})
    try:
        with request.urlopen(req, timeout=_HTTP_TIMEOUT) as response:
            payload = json.loads(response.read().decode())
    except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise BorderlessSigninUnavailableError() from exc
    if not isinstance(payload, dict):
        raise BorderlessSigninUnavailableError()
    return payload


_oauth_client: OAuthClient | None = None


def get_borderless_oauth_client() -> OAuthClient:
    global _oauth_client
    if _oauth_client is None:
        _oauth_client = HttpOAuthClient()
    return _oauth_client


def set_borderless_oauth_client(client: OAuthClient | None) -> None:
    global _oauth_client
    _oauth_client = client
