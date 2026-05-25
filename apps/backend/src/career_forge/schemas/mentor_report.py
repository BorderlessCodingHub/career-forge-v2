"""Mentor report contracts — HAC-15."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from career_forge.schemas.common import ValidationStatus


class MentorReportValidationEntry(BaseModel):
    """Single validation attempt with mentor-facing evidence."""

    node_id: str
    node_title: str
    score: int = Field(ge=0, le=100)
    status: ValidationStatus
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    mentor_summary: str = Field(description="Collapsed narrative for Borderless mentors")
    recommended_intervention: str = Field(
        description="Actionable next step for the mentor to assign",
    )
    validated_at: datetime | None = None


class MentorReportResponse(BaseModel):
    """Aggregate learning evidence for Borderless mentors."""

    user_id: str
    display_name: str
    goal: str
    track_title: str
    profile_label: str
    validations: list[MentorReportValidationEntry] = Field(default_factory=list)
    learner_gaps: list[str] = Field(
        default_factory=list,
        description="Diagnosis-level gaps not yet addressed",
    )
