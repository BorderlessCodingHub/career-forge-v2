"""Contextual mentor chat contracts — HAC-13."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MentorMessage(BaseModel):
    """Single turn in mentor conversation history."""

    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class MentorContextSnapshot(BaseModel):
    """Learner memory injected into mentor replies."""

    recent_gaps: list[str] = Field(default_factory=list)
    recent_strengths: list[str] = Field(default_factory=list)
    failed_nodes: list[str] = Field(default_factory=list)
    current_node_status: str | None = None
    current_node_mastery: int | None = None
    validation_count: int = 0
    last_validation_feedback: str | None = None


class MentorRequest(BaseModel):
    """Submit a contextual mentor question."""

    user_id: str = "demo-ana"
    message: str = Field(min_length=1)
    node_id: str | None = None
    node_title: str | None = None
    history: list[MentorMessage] = Field(default_factory=list)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "message cannot be empty"
            raise ValueError(msg)
        return stripped


class MentorResponse(BaseModel):
    """Structured mentor reply with evidence-aware context."""

    reply: str
    references: list[str] = Field(default_factory=list)
    context_snapshot: MentorContextSnapshot


class MentorRunResponse(BaseModel):
    """GraphExecutor collect result for mentor chat."""

    run_id: str
    status: str
    events: list[dict]
    mentor: MentorResponse
