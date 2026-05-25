"""Mastery validation interview contracts (HAC-10)."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.forge import GraphPatch
from career_forge.schemas.planning import PlanUpdateResponse
from career_forge.schemas.roadmap import RoadmapResponse


class ValidationQuestion(BaseModel):
    """Single interview question derived from node rubric."""

    id: str
    index: int = Field(ge=1, le=3)
    label: str = Field(description="Short tag, e.g. conceito + aplicação")
    prompt: str
    hint: str | None = None
    rubric_criterion: str


class ValidationQuestionsResponse(BaseModel):
    """Questions for a mastery interview on a skill node."""

    node_id: str
    node_title: str
    node_icon: str = "code"
    questions: list[ValidationQuestion] = Field(min_length=3, max_length=3)


class ValidationAnswer(BaseModel):
    """Learner answer tied to a generated question."""

    question_id: str
    answer: str = Field(min_length=1)

    @field_validator("answer")
    @classmethod
    def strip_answer(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "answer cannot be empty"
            raise ValueError(msg)
        return stripped


class ValidationRequest(BaseModel):
    """Submit mastery interview answers for evaluation."""

    user_id: str = "demo-ana"
    node_id: str
    node_title: str
    rubric: list[str] = Field(default_factory=list)
    answers: list[ValidationAnswer] = Field(min_length=3, max_length=3)


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


class ValidationRunResponse(BaseModel):
    """GraphExecutor collect result + persisted validation."""

    run_id: str
    status: str
    events: list[dict]
    validation: ValidationResponse
    node_id: str
    node_status: str
    mastery_score: int
    plan_update: PlanUpdateResponse | None = None
    graph_patch: GraphPatch | None = None
    roadmap: RoadmapResponse | None = None
