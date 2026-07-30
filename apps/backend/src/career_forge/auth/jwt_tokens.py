"""App-signed JWT helpers for the anonymous AuthProvider."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from career_forge.config import settings

ALGORITHM = "HS256"
ANON_PROVIDER = "anonymous"


def _secret() -> str:
    return settings.jwt_secret


def mint_anonymous_token(external_id: str, *, expires_days: int | None = None) -> str:
    """Issue a JWT with ``sub`` = external_id and ``provider=anonymous``."""
    ttl_days = expires_days if expires_days is not None else settings.jwt_anon_ttl_days
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": external_id,
        "provider": ANON_PROVIDER,
        "iat": now,
        "exp": now + timedelta(days=ttl_days),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify signature + expiry. Raises ``jwt.PyJWTError`` on failure."""
    return jwt.decode(token, _secret(), algorithms=[ALGORITHM])
