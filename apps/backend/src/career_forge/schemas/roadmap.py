"""Roadmap API contracts — HAC-9."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode


class RoadmapTrack(BaseModel):
    id: str
    title: str
    description: str = ""


class RoadmapCategory(BaseModel):
    id: str
    label: str


class RoadmapNode(BaseModel):
    """Catalog + user state merged for artifact canvas."""

    node_id: str
    title: str
    category: str
    description: str = ""
    icon: str = "code"
    side: Literal["left", "right"] = "left"
    sort_order: int = 0
    prerequisites: list[str] = Field(default_factory=list)
    outcomes: list[str] = Field(default_factory=list)
    rubric: list[str] = Field(default_factory=list)
    status: SkillStatus
    mastery_score: int = Field(ge=0, le=100, default=0)
    priority: Priority | None = None
    rationale: str | None = None
    tasks: list[dict[str, str | bool]] = Field(default_factory=list)
    references: list[dict[str, str | bool]] = Field(default_factory=list)
    checklist_completed: int = Field(ge=0, default=0)
    checklist_total: int = Field(ge=0, default=0)


class ChecklistToggleRequest(BaseModel):
    """Toggle lightweight study progress for a task or reference item."""

    user_id: str = Field(default="demo-ana")
    item_type: Literal["task", "reference"]
    item_id: str = Field(min_length=1)
    done: bool


class RoadmapResponse(BaseModel):
    track: RoadmapTrack
    categories: list[RoadmapCategory]
    nodes: list[RoadmapNode]


class RoadmapSyncRequest(BaseModel):
    user_id: str = Field(default="demo-ana")
    nodes: list[UserSkillNode]
