"""Borderless password credential check; Career Forge remains the JWT issuer."""

from __future__ import annotations

import json
import time
import uuid
from collections import defaultdict
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Protocol, TypedDict
from urllib import error, request

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
    BorderlessRateLimitedError,
    BorderlessSigninUnavailableError,
    InvalidBorderlessCredentialsError,
    RateLimitedError,
)
from career_forge.services.membership import MembershipClient, apply_membership_label


@dataclass(frozen=True)
class BorderlessIdentity:
    user_id: str
    email_verified: bool
    name: str | None


@dataclass(frozen=True)
class SigninHttpResponse:
    status: int
    headers: Mapping[str, str]
    body: str


class SigninClient(Protocol):
    def authenticate(self, email: str, password: str) -> BorderlessIdentity: ...


class SigninTokenPayload(TypedDict):
    access_token: str
    token_type: str
    external_id: str
    provider: str
    expires_in: int


SigninFetch = Callable[[str, bytes, float], SigninHttpResponse]


def _default_fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
    req = request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return SigninHttpResponse(
                status=response.status,
                headers=dict(response.headers.items()),
                body=response.read().decode("utf-8"),
            )
    except error.HTTPError as exc:
        return SigninHttpResponse(
            status=exc.code,
            headers=dict(exc.headers.items()) if exc.headers else {},
            body=exc.read().decode("utf-8", errors="replace"),
        )


class BorderlessSigninClient:
    """POST credentials to Borderless and expose identity fields only."""

    def __init__(
        self,
        *,
        url: str,
        timeout: float = 2.5,
        fetch: SigninFetch | None = None,
    ) -> None:
        self._url = url
        self._timeout = timeout
        self._fetch = fetch or _default_fetch

    def authenticate(self, email: str, password: str) -> BorderlessIdentity:
        payload = json.dumps(
            {"email": email, "password": password},
            separators=(",", ":"),
        ).encode("utf-8")

        for attempt in range(2):
            try:
                response = self._fetch(self._url, payload, self._timeout)
            except Exception as exc:
                if attempt == 0:
                    continue
                raise BorderlessSigninUnavailableError() from exc

            if response.status == 401:
                raise InvalidBorderlessCredentialsError()
            if response.status == 429:
                retry_after = next(
                    (
                        value
                        for key, value in response.headers.items()
                        if key.lower() == "retry-after"
                    ),
                    None,
                )
                raise BorderlessRateLimitedError(retry_after=retry_after)
            if 500 <= response.status:
                if attempt == 0:
                    continue
                raise BorderlessSigninUnavailableError()
            if response.status != 200:
                raise BorderlessSigninUnavailableError()
            return self._parse_identity(response.body)

        raise BorderlessSigninUnavailableError()

    @staticmethod
    def _parse_identity(raw: str) -> BorderlessIdentity:
        try:
            payload = json.loads(raw)
            user = payload["data"]["user"]
            user_id = user["id"]
            email_verified = user["emailVerified"]
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise BorderlessSigninUnavailableError() from exc

        if not isinstance(user_id, str) or not user_id.strip():
            raise BorderlessSigninUnavailableError()
        if not isinstance(email_verified, bool):
            raise BorderlessSigninUnavailableError()
        name_raw = user.get("name")
        name = name_raw.strip() if isinstance(name_raw, str) and name_raw.strip() else None
        return BorderlessIdentity(
            user_id=user_id.strip(),
            email_verified=email_verified,
            name=name,
        )


_signin_client: SigninClient | None = None
_rate_buckets: dict[str, list[float]] = defaultdict(list)


def get_borderless_signin_client() -> SigninClient:
    global _signin_client
    if _signin_client is None:
        _signin_client = BorderlessSigninClient(
            url=settings.borderless_signin_url,
            timeout=settings.borderless_signin_timeout_seconds,
        )
    return _signin_client


def set_borderless_signin_client(client: SigninClient | None) -> None:
    global _signin_client
    _signin_client = client


def reset_signin_rate_limiter() -> None:
    _rate_buckets.clear()


def _check_rate_limit(*, email: str, client_ip: str) -> None:
    now = time.monotonic()
    window = float(settings.otp_rate_limit_window_seconds)

    def _hit(key: str, limit: int) -> None:
        cutoff = now - window
        kept = [timestamp for timestamp in _rate_buckets[key] if timestamp >= cutoff]
        _rate_buckets[key] = kept
        if len(kept) >= limit:
            raise RateLimitedError("too many signin attempts — try again later")
        kept.append(now)

    _hit(f"email:{email}", settings.otp_rate_limit_per_email)
    _hit(f"ip:{client_ip}", settings.otp_rate_limit_per_ip)


def _token_payload(external_id: str) -> SigninTokenPayload:
    return {
        "access_token": get_auth_provider().mint_email(external_id),
        "token_type": "bearer",
        "external_id": external_id,
        "provider": EMAIL_PROVIDER,
        "expires_in": settings.jwt_anon_ttl_days * 24 * 3600,
    }


def _is_placeholder_name(user: User) -> bool:
    if not user.external_id:
        return False
    return user.display_name == user.external_id.replace("-", " ").title()


def signin(
    session: Session,
    *,
    email: str,
    password: str,
    client_ip: str,
    membership: MembershipClient | None = None,
) -> SigninTokenPayload:
    """Check Borderless credentials, bind identity, and mint a CF email JWT."""
    _check_rate_limit(email=email, client_ip=client_ip)
    identity = get_borderless_signin_client().authenticate(email, password)
    if not identity.email_verified:
        raise BorderlessEmailUnverifiedError()

    user = session.scalar(select(User).where(User.email == email))
    is_new = user is None
    if user is None:
        external_id = f"user-{uuid.uuid4()}"
        user = ensure_user(session, external_id, display_name=identity.name)
        user.email = email
    elif not user.external_id:
        user.external_id = f"user-{uuid.uuid4()}"

    if user.borderless_user_id and user.borderless_user_id != identity.user_id:
        raise BorderlessIdentityMismatchError()

    user.borderless_user_id = identity.user_id
    if identity.name and (is_new or _is_placeholder_name(user)):
        user.display_name = identity.name
    apply_membership_label(user, email, membership)
    session.commit()
    return _token_payload(user.external_id)
