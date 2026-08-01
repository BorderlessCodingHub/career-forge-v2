"""Public share / resume deep-link routes (CAR-27)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from career_forge.db.session import get_db
from career_forge.schemas.forge_access_tokens import ResumeConsumeResponse
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.services import forge_access_tokens as forge_access_tokens_service

router = APIRouter()


# Under /public/* so Next.js app routes /share and /resume can own the same
# path segments on same-origin Labs (rewrites lose to filesystem pages).
@router.get("/public/share/{token}", response_model=RoadmapResponse)
def get_shared_forge(
    token: str,
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    return forge_access_tokens_service.resolve_share(db, token)


@router.post("/public/resume/{token}", response_model=ResumeConsumeResponse)
def consume_resume_link(
    token: str,
    db: Session = Depends(get_db),
) -> ResumeConsumeResponse:
    result = forge_access_tokens_service.consume_resume(db, token)
    return ResumeConsumeResponse.model_validate(result)
