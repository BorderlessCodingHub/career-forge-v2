"""Auth HTTP routes — anonymous JWT mint (CAR-23)."""

from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import ANON_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import get_db

router = APIRouter()

_EXTERNAL_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class AnonMintRequest(BaseModel):
    """Optional ``external_id`` migrates an existing localStorage anon id into a JWT."""

    external_id: str | None = Field(default=None, max_length=64)


class AnonMintResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    external_id: str
    provider: str = ANON_PROVIDER
    expires_in: int


def _normalize_external_id(raw: str | None) -> str:
    if raw is None or not raw.strip():
        return f"user-{uuid.uuid4().hex[:8]}"
    candidate = raw.strip()
    if not _EXTERNAL_ID_RE.match(candidate):
        return f"user-{uuid.uuid4().hex[:8]}"
    return candidate


@router.post("/anon/mint", response_model=AnonMintResponse)
def mint_anonymous_token(
    body: AnonMintRequest,
    db: Session = Depends(get_db),
) -> AnonMintResponse:
    """Mint an anonymous Bearer JWT and ensure ``users.external_id`` exists."""
    external_id = _normalize_external_id(body.external_id)
    ensure_user(db, external_id)
    db.commit()
    token = get_auth_provider().mint_anonymous(external_id)
    return AnonMintResponse(
        access_token=token,
        external_id=external_id,
        expires_in=settings.jwt_anon_ttl_days * 24 * 3600,
    )
