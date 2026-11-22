"""The old skill-lesson address no longer presents a lesson (ADR-010)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from career_forge.api.deps import require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.schemas.canonical import CanonicalPage
from career_forge.services.canonical_content import read_skill_lesson

router = APIRouter()


@router.get("/{skill_id}/content", response_model=CanonicalPage)
@router.get("/{skill_id}", response_model=CanonicalPage)
def get_skill_lesson(
    skill_id: str,
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> CanonicalPage:
    return read_skill_lesson(skill_id)
