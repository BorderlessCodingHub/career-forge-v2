"""Pydantic schemas bound to LangChain structured output for diagnosis interview."""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_KEYS,
    PROFILE_DIMENSION_LABELS,
    MAX_QUESTIONS_PER_TURN,
    SATURATION_CONFIDENCE_THRESHOLD,
    BeliefState,
    InterviewQuestion,
    RubricDimension,
    RubricDimensionKey,
    RubricDimensionStatus,
)


def infer_dimension_status(
    confidence: float,
    raw_status: RubricDimensionStatus | None,
) -> RubricDimensionStatus:
    if raw_status in ("pending", "mapped", "needs_clarification"):
        status = raw_status
    elif confidence >= SATURATION_CONFIDENCE_THRESHOLD:
        status = "mapped"
    elif confidence >= 0.35:
        status = "needs_clarification"
    else:
        status = "pending"

    if status == "mapped" and confidence < SATURATION_CONFIDENCE_THRESHOLD:
        return "needs_clarification"
    return status


def normalize_rubric_dimension(key: RubricDimensionKey, dim: RubricDimension) -> RubricDimension:
    confidence = min(1.0, max(0.0, dim.confidence))
    status = infer_dimension_status(confidence, dim.status)
    note = dim.note.strip()
    if not note and dim.evidence:
        note = dim.evidence[0][:120]
    return RubricDimension(
        key=key,
        label=dim.label.strip() or PROFILE_DIMENSION_LABELS[key],
        confidence=confidence,
        evidence=[item.strip() for item in dim.evidence if item.strip()][:5],
        status=status,
        note=note,
    )


class JudgeBeliefOutput(BaseModel):
    """Structured Judge output — one field per profile dimension for strict JSON schema."""

    motivation_goal: RubricDimension
    background_transfer: RubricDimension
    learning_velocity: RubricDimension
    hands_on_proof: RubricDimension
    constraints: RubricDimension

    def to_belief_state(self) -> BeliefState:
        return BeliefState(
            dimensions={
                key: normalize_rubric_dimension(
                    key,
                    getattr(self, key).model_copy(
                        update={
                            "key": key,
                            "label": getattr(self, key).label or PROFILE_DIMENSION_LABELS[key],
                        },
                    ),
                )
                for key in PROFILE_DIMENSION_KEYS
            },
        )


class InterviewerOutput(BaseModel):
    """Structured Interviewer output."""

    questions: list[InterviewQuestion] = Field(default_factory=list, max_length=MAX_QUESTIONS_PER_TURN)


class EstimatedMasteryEntry(BaseModel):
    """OpenAI strict JSON schema friendly alternative to dict[str, int]."""

    node_id: str = Field(min_length=1)
    score: int = Field(ge=0, le=100)


class FinalizeDiagnosisOutput(BaseModel):
    """Structured finalize output — converted to DiagnosisResponse after LLM call."""

    profile: DiagnosisProfile
    strengths: list[str] = Field(min_length=1)
    gaps: list[str] = Field(min_length=1)
    starting_priorities: list[str] = Field(min_length=1)
    estimated_mastery: list[EstimatedMasteryEntry] = Field(min_length=1)

    def to_diagnosis_response(self) -> DiagnosisResponse:
        return DiagnosisResponse(
            profile=self.profile,
            strengths=self.strengths,
            gaps=self.gaps,
            starting_priorities=self.starting_priorities,
            estimated_mastery={entry.node_id: entry.score for entry in self.estimated_mastery},
        )
