"""Mastery validation interview result (HAC-10)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.schemas.common import ValidationStatus


class ValidationResponse(BaseModel):
    """Structured result after AI mastery interview."""

    score: int = Field(ge=0, le=100)
    status: ValidationStatus
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    next_action: str = Field(
        description="Actionable next step for the learner (PT-BR)",
    )
    mentor_summary: str = Field(
        description="Collapsed accordion copy for Borderless mentors",
    )
