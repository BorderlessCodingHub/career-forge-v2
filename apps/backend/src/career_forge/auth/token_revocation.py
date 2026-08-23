"""JWT jti denylist — sign-out revokes this device token only (CAR-69)."""

from __future__ import annotations

from datetime import UTC, datetime

import jwt
from sqlalchemy import delete
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import (
    ANON_PROVIDER,
    APP_PROVIDERS,
    EMAIL_PROVIDER,
    decode_token,
)
from career_forge.auth.principal import AuthPrincipal
from career_forge.db.models.revoked_token_jti import RevokedTokenJti


def _exp_from_payload(payload: dict) -> datetime:
    exp = payload.get("exp")
    if isinstance(exp, datetime):
        return exp if exp.tzinfo else exp.replace(tzinfo=UTC)
    if isinstance(exp, (int, float)):
        return datetime.fromtimestamp(exp, tz=UTC)
    raise ValueError("token missing exp")


def _principal_from_payload(payload: dict) -> AuthPrincipal:
    sub = payload.get("sub")
    provider = payload.get("provider")
    jti = payload.get("jti")
    if not isinstance(sub, str) or not sub.strip():
        raise ValueError("token missing sub")
    if not isinstance(jti, str) or not jti.strip():
        raise ValueError("token missing jti")
    if provider not in APP_PROVIDERS:
        raise ValueError(f"unsupported provider: {provider!r}")
    assert provider in (ANON_PROVIDER, EMAIL_PROVIDER)
    return AuthPrincipal(external_id=sub.strip(), provider=provider)


def cleanup_expired_revocations(db: Session) -> None:
    """Lazy purge — safe to call on every verify/sign-out."""
    now = datetime.now(UTC)
    db.execute(delete(RevokedTokenJti).where(RevokedTokenJti.exp < now))


def is_jti_revoked(db: Session, jti: str) -> bool:
    return db.get(RevokedTokenJti, jti) is not None


def revoke_jti(db: Session, jti: str, exp: datetime) -> None:
    if db.get(RevokedTokenJti, jti) is None:
        db.add(RevokedTokenJti(jti=jti, exp=exp))


def verify_access_token(db: Session, token: str) -> AuthPrincipal:
    """Decode → require jti → denylist check → lazy cleanup."""
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise ValueError("invalid or expired token") from exc

    principal = _principal_from_payload(payload)
    cleanup_expired_revocations(db)
    jti = payload["jti"].strip()
    if is_jti_revoked(db, jti):
        raise ValueError("token revoked")
    return principal


def revoke_token(db: Session, token: str) -> None:
    """Insert current token jti into denylist."""
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise ValueError("invalid or expired token") from exc

    jti = payload.get("jti")
    if not isinstance(jti, str) or not jti.strip():
        raise ValueError("token missing jti")

    cleanup_expired_revocations(db)
    revoke_jti(db, jti.strip(), _exp_from_payload(payload))
