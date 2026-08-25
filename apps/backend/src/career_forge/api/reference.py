"""Learner-facing Reference viewer support endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from career_forge.api.deps import require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.db.session import get_db
from career_forge.schemas.embed_allowlist import LearnerEmbedHostListResponse
from career_forge.services.embed_allowlist import learner_embed_hosts

router = APIRouter()


@router.get("/embed-hosts", response_model=LearnerEmbedHostListResponse)
def get_reference_embed_hosts(
    response: Response,
    db: Session = Depends(get_db),
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> LearnerEmbedHostListResponse:
    response.headers["Cache-Control"] = "no-store"
    return LearnerEmbedHostListResponse(hosts=list(learner_embed_hosts(db)))
