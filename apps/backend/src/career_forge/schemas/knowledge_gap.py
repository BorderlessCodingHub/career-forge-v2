"""Knowledge gap contracts — adaptive memory ledger (HAC-67)."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Severity = Literal["low", "medium", "high"]


class WrongAnswerItem(BaseModel):
    """One missed MCQ question captured at submit (session still alive)."""

    question_id: str
    concept: str
    prompt: str = ""
    chosen: str = ""
    chosen_text: str = ""
    correct: str = ""
    correct_text: str = ""


class KnowledgeGapDraft(BaseModel):
    """Classifier output — a single structured gap."""

    concept: str = Field(min_length=2, max_length=160)
    severity: Severity = "medium"
    evidence: str = Field(default="", max_length=600)
    suggested_remediation: str = Field(default="", max_length=600)


class KnowledgeGapClassification(BaseModel):
    """Batched classifier result for all wrong answers in one attempt."""

    gaps: list[KnowledgeGapDraft] = Field(default_factory=list)


class KnowledgeGapItem(BaseModel):
    """Read model surfaced to mentor / roadmap / next mock."""

    concept: str
    severity: Severity
    status: Literal["open", "resolved"]
    suggested_remediation: str | None = None
    skill_node_id: str
    updated_at: datetime | None = None
