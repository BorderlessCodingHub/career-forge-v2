"""Short-lived forge SSE stream tickets (CAR-26 / ADR-003).

Browser EventSource cannot send Authorization. Clients mint a ticket with
Bearer, then open ``GET /forge/{run_id}/stream?ticket=``.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict

import jwt

from career_forge.config import settings

ALGORITHM = "HS256"
FORGE_STREAM_PURPOSE = "forge_stream"


class ForgeStreamTicketClaims(TypedDict):
    sub: str
    run_id: str


def _secret() -> str:
    return settings.jwt_secret


def stream_ticket_ttl_seconds() -> int:
    return settings.jwt_stream_ticket_ttl_seconds


def mint_forge_stream_ticket(external_id: str, run_id: str) -> str:
    """Issue a JWT bound to ``external_id`` + ``run_id`` with short TTL."""
    now = datetime.now(UTC)
    ttl = stream_ticket_ttl_seconds()
    payload: dict[str, Any] = {
        "sub": external_id,
        "run_id": run_id,
        "purpose": FORGE_STREAM_PURPOSE,
        "iat": now,
        "exp": now + timedelta(seconds=ttl),
    }
    return jwt.encode(payload, _secret(), algorithm=ALGORITHM)


def decode_forge_stream_ticket(token: str) -> ForgeStreamTicketClaims:
    """Verify signature, expiry, and purpose. Raises ``jwt.PyJWTError`` / ``ValueError``."""
    payload = jwt.decode(token, _secret(), algorithms=[ALGORITHM])
    if payload.get("purpose") != FORGE_STREAM_PURPOSE:
        raise ValueError("invalid stream ticket purpose")
    sub = payload.get("sub")
    run_id = payload.get("run_id")
    if not isinstance(sub, str) or not sub:
        raise ValueError("stream ticket missing sub")
    if not isinstance(run_id, str) or not run_id:
        raise ValueError("stream ticket missing run_id")
    return {"sub": sub, "run_id": run_id}
