"""Onboarding diagnosis contract (identity engine / HAC-8)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class DiagnosisProfile(BaseModel):
    """Structured profile badge shown on editable diagnosis."""

    label: str = Field(
        description='Display label, e.g. "Iniciante com base em JavaScript"',
    )
    track_id: str = Field(
        default="backend-beginner",
        description="Catalog track slug from roadmap.json",
    )
    persona_slug: str | None = Field(
        default=None,
        description="Internal persona key, e.g. iniciante_js",
    )


class DiagnosisResponse(BaseModel):
    """Structured AI diagnosis after onboarding chat."""

    profile: DiagnosisProfile
    strengths: list[str] = Field(min_length=1)
    gaps: list[str] = Field(min_length=1)
    starting_priorities: list[str] = Field(
        min_length=1,
        description="Ordered node ids or topic labels to tackle first",
    )
    estimated_mastery: dict[str, int] = Field(
        default_factory=dict,
        description="node_id → 0–100 estimated mastery before forge",
    )

    @field_validator("estimated_mastery")
    @classmethod
    def validate_mastery_scores(cls, v: dict[str, int]) -> dict[str, int]:
        for node_id, score in v.items():
            if not 0 <= score <= 100:
                raise ValueError(
                    f"estimated_mastery[{node_id!r}] must be 0–100, got {score}",
                )
        return v


class DiagnosisRequest(BaseModel):
    """Onboarding payload consumed by the diagnosis graph."""

    user_id: str = Field(default="demo-ana")
    goal_id: str = Field(default="backend", description="Selected career goal slug")
    motivation: str = Field(
        min_length=20,
        max_length=280,
        description="Why the learner chose this path",
    )
    answers: dict[str, str] = Field(
        min_length=1,
        description="question_id → free-text answer from pill rounds",
    )

    @field_validator("answers")
    @classmethod
    def validate_answers(cls, v: dict[str, str]) -> dict[str, str]:
        cleaned = {key: value.strip() for key, value in v.items() if value.strip()}
        if not cleaned:
            msg = "answers must include at least one non-empty response"
            raise ValueError(msg)
        return cleaned
