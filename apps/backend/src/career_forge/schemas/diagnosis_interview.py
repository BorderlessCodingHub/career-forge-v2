"""Adaptive diagnosis interview contracts — CTRR rubric (HAC-42)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from career_forge.schemas.diagnosis import DiagnosisResponse

# --- CTRR constants (single source of truth) ---

RubricDimensionKey = Literal[
    "learning_stage",
    "project_scope",
    "background_context",
    "hands_on_evidence",
    "git",
    "client_server",
    "http_apis",
    "database",
]

CTRR_DIMENSION_KEYS: tuple[RubricDimensionKey, ...] = (
    "learning_stage",
    "project_scope",
    "background_context",
    "hands_on_evidence",
    "git",
    "client_server",
    "http_apis",
    "database",
)

CTRR_DIMENSION_LABELS: dict[RubricDimensionKey, str] = {
    "learning_stage": "Senioridade",
    "project_scope": "Escala",
    "background_context": "Contexto",
    "hands_on_evidence": "Experiência prática",
    "git": "Git",
    "client_server": "Cliente/servidor",
    "http_apis": "HTTP & APIs",
    "database": "Banco de dados",
}

SATURATION_CONFIDENCE_THRESHOLD = 0.75
MAX_INTERVIEW_ROUNDS = 5
MAX_QUESTIONS_PER_TURN = 2

DiagnosisSessionStatus = Literal["asking", "complete"]
YearsXpRange = Literal["0-1", "1-3", "3-5", "5+"]


class RubricDimension(BaseModel):
    """Judge belief for one CTRR dimension."""

    key: RubricDimensionKey
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)


class BeliefState(BaseModel):
    """Per-dimension confidence + evidence maintained by the Judge."""

    dimensions: dict[RubricDimensionKey, RubricDimension]

    @classmethod
    def empty(cls) -> BeliefState:
        return cls(
            dimensions={
                key: RubricDimension(
                    key=key,
                    label=CTRR_DIMENSION_LABELS[key],
                    confidence=0.0,
                    evidence=[],
                )
                for key in CTRR_DIMENSION_KEYS
            },
        )

    def unsaturated_keys(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> list[RubricDimensionKey]:
        return [key for key in CTRR_DIMENSION_KEYS if self.dimensions[key].confidence < threshold]

    def is_saturated(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> bool:
        return all(dim.confidence >= threshold for dim in self.dimensions.values())


class CvAttachment(BaseModel):
    """PDF CV payload from Screen 1."""

    filename: str = Field(min_length=1)
    mime_type: Literal["application/pdf"]
    content_base64: str = Field(min_length=1)
    extracted_text: str | None = Field(
        default=None,
        description="Plain text after PDF extract (no LLM)",
    )


class CvSignals(BaseModel):
    """Optional LLM-structured extract from CV text."""

    skills: list[str] = Field(default_factory=list)
    roles: list[str] = Field(default_factory=list)
    years_hint: str | None = None
    education: list[str] = Field(default_factory=list)
    evidence_snippets: list[str] = Field(default_factory=list)


class DiagnosisIntake(BaseModel):
    """Screen 1 payload — goal, motivation, optional CV."""

    user_id: str = Field(default="anonymous")
    goal_id: str = Field(description="Selected career goal slug")
    motivation: str = Field(min_length=1, max_length=280)
    years_xp: YearsXpRange | None = None
    cv: CvAttachment | None = None


class InterviewQuestion(BaseModel):
    """Interviewer output — one question targeting a rubric dimension."""

    id: str = Field(min_length=1)
    topic: str = Field(description="Sidebar label, e.g. Senioridade")
    rubric_key: RubricDimensionKey
    question: str = Field(min_length=1)
    example_of_answer: str = Field(min_length=1)


class InterviewAnswer(BaseModel):
    """User free-text answer for one question."""

    question_id: str = Field(min_length=1)
    text: str = Field(min_length=1)

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            msg = "answer text must be non-empty after stripping"
            raise ValueError(msg)
        return cleaned


class InterviewTurn(BaseModel):
    """Append-only transcript slice — questions asked and answers received."""

    questions: list[InterviewQuestion] = Field(max_length=MAX_QUESTIONS_PER_TURN)
    answers: list[InterviewAnswer] = Field(default_factory=list)


class RubricMapItem(BaseModel):
    """Sidebar mapping progress for one dimension."""

    rubric_key: RubricDimensionKey
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    saturated: bool


def build_rubric_map(
    belief: BeliefState,
    *,
    threshold: float = SATURATION_CONFIDENCE_THRESHOLD,
) -> list[RubricMapItem]:
    """Map belief state to frontend sidebar items (stable CTRR order)."""
    return [
        RubricMapItem(
            rubric_key=key,
            label=belief.dimensions[key].label,
            confidence=belief.dimensions[key].confidence,
            saturated=belief.dimensions[key].confidence >= threshold,
        )
        for key in CTRR_DIMENSION_KEYS
    ]


class DiagnosisSession(BaseModel):
    """Multi-turn diagnosis interview persisted between API turns."""

    session_id: str = Field(min_length=1)
    intake: DiagnosisIntake
    belief: BeliefState = Field(default_factory=BeliefState.empty)
    cv_signals: CvSignals | None = None
    transcript: list[InterviewTurn] = Field(default_factory=list)
    status: DiagnosisSessionStatus = "asking"
    round_count: int = Field(default=0, ge=0, le=MAX_INTERVIEW_ROUNDS)
    diagnosis: DiagnosisResponse | None = None

    def is_complete(self) -> bool:
        return self.status == "complete"

    def should_finalize(
        self,
        *,
        threshold: float = SATURATION_CONFIDENCE_THRESHOLD,
        max_rounds: int = MAX_INTERVIEW_ROUNDS,
    ) -> bool:
        return self.belief.is_saturated(threshold) or self.round_count >= max_rounds


class InterviewStartRequest(DiagnosisIntake):
    """POST /diagnosis/interview/start body."""


class InterviewTurnRequest(BaseModel):
    """POST /diagnosis/interview/{session_id}/turn body."""

    answers: list[InterviewAnswer] = Field(min_length=1, max_length=MAX_QUESTIONS_PER_TURN)


class InterviewTurnResponse(BaseModel):
    """Shared response shape for start + turn endpoints."""

    session_id: str
    status: DiagnosisSessionStatus
    questions: list[InterviewQuestion] = Field(default_factory=list, max_length=MAX_QUESTIONS_PER_TURN)
    mapping_progress: list[RubricMapItem] = Field(default_factory=list)
    diagnosis: DiagnosisResponse | None = None

    @field_validator("questions")
    @classmethod
    def validate_question_count(cls, value: list[InterviewQuestion]) -> list[InterviewQuestion]:
        if len(value) > MAX_QUESTIONS_PER_TURN:
            msg = f"at most {MAX_QUESTIONS_PER_TURN} questions per turn"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validate_complete_has_diagnosis(self) -> InterviewTurnResponse:
        if self.status == "complete" and self.diagnosis is None:
            msg = "complete status requires diagnosis"
            raise ValueError(msg)
        if self.status == "asking" and self.diagnosis is not None:
            msg = "asking status must not include diagnosis"
            raise ValueError(msg)
        return self
