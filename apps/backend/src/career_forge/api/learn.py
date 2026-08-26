"""Learner canonical skill content — in-app /learn (ADR-004)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from career_forge.api.deps import require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.db.session import get_db
from career_forge.schemas.canonical import CanonicalPage
from career_forge.services.canonical_content import require_published_canonical

router = APIRouter()


@router.get("/{skill_id}/content", response_model=CanonicalPage)
@router.get("/{skill_id}", response_model=CanonicalPage)
def get_canonical_skill_content(
    skill_id: str,
    response: Response,
    db: Session = Depends(get_db),
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> CanonicalPage:
    response.headers["Cache-Control"] = "no-store"
    return require_published_canonical(db, skill_id)
