"""Shared enums and skill-graph primitives."""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field


class SkillStatus(StrEnum):
    """User skill node status — canonical CHECKPOINT enum."""

    BLOQUEADO = "bloqueado"
    RECOMENDADO = "recomendado"
    EM_ESTUDO = "em_estudo"
    VALIDAR = "validar"
    APROVADO = "aprovado"
    REVISAR = "revisar"


class Priority(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ValidationStatus(StrEnum):
    """Outcome of a mastery validation run."""

    APROVADO = "aprovado"
    REVISAR = "revisar"


ForgeRunStatus = Literal["running", "done", "error"]


class SkillNode(BaseModel):
    """Static catalog node from roadmap.json."""

    id: str
    title: str
    category: str
    description: str = ""
    icon: str = "code"
    side: Literal["left", "right"] = "left"
    sort_order: int = 0
    prerequisites: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    rubric: list[str] = Field(default_factory=list)


class UserSkillNode(BaseModel):
    """Dynamic per-user skill state (accumulated_graph item)."""

    node_id: str
    title: str | None = None
    status: SkillStatus
    mastery_score: int = Field(ge=0, le=100, description="0–100 mastery %")
    priority: Priority | None = None
    rationale: str | None = None
    prerequisites: list[str] = Field(default_factory=list)
    key_concepts: list[str] = Field(default_factory=list)
    tasks: list[dict[str, str]] = Field(default_factory=list)
    references: list[dict[str, str]] = Field(default_factory=list)


class UserSkillNodePartial(BaseModel):
    """Partial update emitted on SSE node_updated."""

    node_id: str
    title: str | None = None
    status: SkillStatus | None = None
    mastery_score: int | None = Field(default=None, ge=0, le=100)
    priority: Priority | None = None
    rationale: str | None = None
    prerequisites: list[str] | None = None
    tasks: list[dict[str, str]] | None = None
    references: list[dict[str, str]] | None = None


class ReasoningEntry(BaseModel):
    """Single timeline line in forge reasoning_log."""

    step: str
    text: str
    iteration: int = 0


class Artifact(BaseModel):
    """Research / decision artifact surfaced during forge."""

    label: str
    detail: str
    node_id: str | None = None
