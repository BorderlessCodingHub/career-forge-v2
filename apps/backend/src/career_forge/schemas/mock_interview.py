"""Mock interview loop contracts (HAC-14, HAC-65 MCQ)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from career_forge.schemas.forge import GraphPatch
from career_forge.schemas.planning import PlanUpdateResponse
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.schemas.validation import ValidationAnswer, ValidationResponse

MCQ_LETTERS = frozenset({"A", "B", "C", "D"})


class MockInterviewOption(BaseModel):
    letter: Literal["A", "B", "C", "D"]
    text: str = Field(min_length=1)


class MockInterviewQuestion(BaseModel):
    """Single contextual mock interview question."""

    id: str
    index: int = Field(ge=1, le=7)
    label: str = Field(description="Phase tag: conceito, aplicação, gap, cenário")
    prompt: str
    hint: str | None = None
    rubric_criterion: str
    concept: str | None = Field(
        default=None,
        description="Technical concept this question probes (feeds the knowledge-gap ledger)",
    )
    phase: str = Field(description="base | gap_probe | scenario")
    options: list[MockInterviewOption] | None = None


class MockInterviewQuestionsResponse(BaseModel):
    """5–7 contextual questions for mock interview on a skill node."""

    node_id: str
    node_title: str
    node_icon: str = "code"
    session_id: str | None = None
    format: Literal["open", "mcq"] = "open"
    total_questions: int = Field(ge=5, le=7)
    questions: list[MockInterviewQuestion] = Field(min_length=5, max_length=7)


class MockInterviewRequest(BaseModel):
    """Submit mock interview answers for evaluation and trail recalibration."""

    user_id: str = "demo-ana"
    node_id: str
    node_title: str
    session_id: str | None = None
    rubric: list[str] = Field(default_factory=list)
    answers: list[ValidationAnswer] = Field(min_length=5, max_length=7)

    @field_validator("answers")
    @classmethod
    def validate_answer_count(cls, value: list[ValidationAnswer]) -> list[ValidationAnswer]:
        if len(value) < 5 or len(value) > 7:
            msg = "mock interview requires 5–7 answers"
            raise ValueError(msg)
        return value


class MockInterviewRunResponse(BaseModel):
    """GraphExecutor collect result + adaptive recalibration after mock interview."""

    run_id: str | None = None
    status: str
    events: list[dict] = Field(default_factory=list)
    validation: ValidationResponse
    node_id: str
    node_status: str
    mastery_score: int
    plan_update: PlanUpdateResponse | None = None
    graph_patch: GraphPatch | None = None
    roadmap: RoadmapResponse | None = None
