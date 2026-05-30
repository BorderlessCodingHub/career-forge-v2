"""Chapter Q&A tutor contracts — HAC-71.

Distinct from the mentor (trail-level memory): the tutor is grounded in a single
chapter's key_concepts + references and the learner's open knowledge gaps.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TutorMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1)


class TutorReference(BaseModel):
    title: str
    url: str | None = None


class TutorContext(BaseModel):
    """Chapter grounding injected into tutor replies."""

    node_id: str | None = None
    node_title: str | None = None
    key_concepts: list[str] = Field(default_factory=list)
    references: list[TutorReference] = Field(default_factory=list)
    open_gaps: list[str] = Field(default_factory=list)


class TutorRequest(BaseModel):
    user_id: str = "demo-ana"
    message: str = Field(min_length=1)
    node_id: str | None = None
    node_title: str | None = None
    history: list[TutorMessage] = Field(default_factory=list)

    @field_validator("message")
    @classmethod
    def strip_message(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            msg = "message cannot be empty"
            raise ValueError(msg)
        return stripped


class TutorResponse(BaseModel):
    reply: str
    references: list[str] = Field(default_factory=list)
    used_concepts: list[str] = Field(default_factory=list)
    context: TutorContext


class TutorRunResponse(BaseModel):
    run_id: str
    status: str
    events: list[dict] = Field(default_factory=list)
    tutor: TutorResponse
