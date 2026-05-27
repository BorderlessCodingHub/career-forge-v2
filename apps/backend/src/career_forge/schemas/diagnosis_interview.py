"""Adaptive diagnosis interview contracts — universal profile rubric (ADR-002)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from career_forge.schemas.diagnosis import DiagnosisResponse

# --- Universal profile dimensions (single source of truth) ---

RubricDimensionKey = Literal[
    "motivation_goal",
    "background_transfer",
    "learning_velocity",
    "hands_on_proof",
    "constraints",
]

PROFILE_DIMENSION_KEYS: tuple[RubricDimensionKey, ...] = (
    "motivation_goal",
    "background_transfer",
    "learning_velocity",
    "hands_on_proof",
    "constraints",
)

PROFILE_DIMENSION_LABELS: dict[RubricDimensionKey, str] = {
    "motivation_goal": "Objetivo",
    "background_transfer": "De onde você vem",
    "learning_velocity": "Ritmo de aprendizado",
    "hands_on_proof": "Prova prática",
    "constraints": "Contexto real",
}

PROFILE_DIMENSION_DESCRIPTIONS: dict[RubricDimensionKey, str] = {
    "motivation_goal": "Por que esse caminho e alinhamento com sua meta",
    "background_transfer": "Área anterior e hábitos que você traz para tech",
    "learning_velocity": "Quanto pratica, com que frequência e consistência",
    "hands_on_proof": "Maior coisa que construiu, tentou ou entregou",
    "constraints": "Tempo/semana, idioma, budget, como estuda hoje",
}

SATURATION_CONFIDENCE_THRESHOLD = 0.75
MAX_INTERVIEW_ROUNDS = 2
MAX_QUESTIONS_PER_TURN = 2

DiagnosisSessionStatus = Literal["asking", "complete"]
RubricDimensionStatus = Literal["pending", "mapped", "needs_clarification"]
YearsXpRange = Literal["0-1", "1-3", "3-5", "5+"]


class RubricDimension(BaseModel):
    """Judge belief for one profile dimension."""

    key: RubricDimensionKey
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    status: RubricDimensionStatus = "pending"
    note: str = Field(
        default="",
        description="Succinct PT-BR summary of what was inferred (intake, CV, or answers).",
    )


class BeliefState(BaseModel):
    """Per-dimension confidence + evidence maintained by the Judge."""

    dimensions: dict[RubricDimensionKey, RubricDimension]

    @classmethod
    def empty(cls) -> BeliefState:
        return cls(
            dimensions={
                key: RubricDimension(
                    key=key,
                    label=PROFILE_DIMENSION_LABELS[key],
                    confidence=0.0,
                    evidence=[],
                    status="pending",
                    note="",
                )
                for key in PROFILE_DIMENSION_KEYS
            },
        )

    def unsaturated_keys(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> list[RubricDimensionKey]:
        return [key for key in PROFILE_DIMENSION_KEYS if self.dimensions[key].confidence < threshold]

    def interviewable_keys(self) -> list[RubricDimensionKey]:
        """Dimensions the Interviewer may still ask about."""
        return [
            key
            for key in PROFILE_DIMENSION_KEYS
            if self.dimensions[key].status in ("pending", "needs_clarification")
        ]

    def is_saturated(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> bool:
        return all(dim.confidence >= threshold for dim in self.dimensions.values())

    def is_interview_complete(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> bool:
        """True when every dimension is mapped with sufficient confidence."""
        return all(
            dim.status == "mapped" and dim.confidence >= threshold
            for dim in self.dimensions.values()
        )

    def profile_completeness(self, threshold: float = SATURATION_CONFIDENCE_THRESHOLD) -> float:
        if not self.dimensions:
            return 0.0
        mapped = sum(
            1
            for dim in self.dimensions.values()
            if dim.status == "mapped" and dim.confidence >= threshold
        )
        return mapped / len(PROFILE_DIMENSION_KEYS)


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
    """Interviewer output — one question (may cover multiple dimensions)."""

    id: str = Field(min_length=1)
    topic: str = Field(description="Sidebar label, e.g. Prova prática")
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
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    saturated: bool
    status: RubricDimensionStatus
    note: str = ""


def build_rubric_map(
    belief: BeliefState,
    *,
    threshold: float = SATURATION_CONFIDENCE_THRESHOLD,
) -> list[RubricMapItem]:
    """Map belief state to frontend sidebar items (stable profile order)."""
    return [
        RubricMapItem(
            rubric_key=key,
            label=dim.label,
            description=PROFILE_DIMENSION_DESCRIPTIONS[key],
            confidence=dim.confidence,
            saturated=dim.status == "mapped" and dim.confidence >= threshold,
            status=dim.status,
            note=dim.note,
        )
        for key in PROFILE_DIMENSION_KEYS
        for dim in (belief.dimensions[key],)
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
        max_rounds: int = MAX_INTERVIEW_ROUNDS,
    ) -> bool:
        return self.round_count >= max_rounds


class InterviewStartRequest(DiagnosisIntake):
    """POST /diagnosis/interview/start body."""


class InterviewTurnRequest(BaseModel):
    """POST /diagnosis/interview/{session_id}/turn body."""

    answers: list[InterviewAnswer] = Field(min_length=1, max_length=MAX_QUESTIONS_PER_TURN)


class InterviewTurnResponse(BaseModel):
    """Shared response shape for start + turn endpoints."""

    session_id: str
    status: DiagnosisSessionStatus
    round_count: int = Field(default=0, ge=0, le=MAX_INTERVIEW_ROUNDS)
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
