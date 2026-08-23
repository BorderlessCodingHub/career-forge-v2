"""App-signed JWT helpers for anonymous + email AuthProviders."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import jwt

from career_forge.config import settings

ALGORITHM = "HS256"
ANON_PROVIDER = "anonymous"
EMAIL_PROVIDER = "email"
APP_PROVIDERS = frozenset({ANON_PROVIDER, EMAIL_PROVIDER})


def _secret() -> str:
    return settings.jwt_secret


def mint_anonymous_token(external_id: str, *, expires_days: int | None = None) -> str:
    """Issue a JWT with ``sub`` = external_id and ``provider=anonymous``."""
    return _mint_token(external_id, provider=ANON_PROVIDER, expires_days=expires_days)


def mint_email_token(external_id: str, *, expires_days: int | None = None) -> str:
    """Issue a JWT with ``sub`` = external_id and ``provider=email`` (CAR-44)."""
    return _mint_token(external_id, provider=EMAIL_PROVIDER, expires_days=expires_days)


def _mint_token(
    external_id: str,
    *,
    provider: str,
    expires_days: int | None = None,
) -> str:
    ttl_days = expires_days if expires_days is not None else settings.jwt_anon_ttl_days
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": external_id,
        "provider": provider,
        "jti": str(uuid4()),
        "iat": now,
        "exp": now + timedelta(days=ttl_days),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify signature + expiry. Raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(token, _secret(), algorithms=[ALGORITHM])
