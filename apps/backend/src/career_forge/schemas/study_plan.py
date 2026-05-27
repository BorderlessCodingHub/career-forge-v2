"""Structured study plan contracts for AI-generated roadmaps (HAC-54/55)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class StudyResource(BaseModel):
    """Reference used to justify or teach one plan item."""

    title: str = Field(min_length=1)
    url: str = Field(min_length=1)
    snippet: str = ""
    source_type: Literal["official_docs", "tutorial", "reference", "example"] = "official_docs"

    @field_validator("url")
    @classmethod
    def validate_http_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            msg = "url must start with http:// or https://"
            raise ValueError(msg)
        return value


class StudyPlanTask(BaseModel):
    """Concrete learning action inside a study node."""

    title: str = Field(min_length=1)
    outcome: str = Field(min_length=1)
    evidence_prompt: str = Field(
        min_length=1,
        description="What the learner must produce to prove this task.",
    )


class StudyPlanNode(BaseModel):
    """AI-proposed roadmap node before it is merged into UserSkillNode."""

    node_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    why_now: str = Field(min_length=1)
    prerequisites: list[str] = Field(default_factory=list)
    tasks: list[StudyPlanTask] = Field(min_length=1)
    resources: list[StudyResource] = Field(default_factory=list)


class StudyPlan(BaseModel):
    """Planner output that an evaluator can critique before graph_ready."""

    goal: str = Field(min_length=1)
    learner_context_summary: str = Field(min_length=1)
    strategy: str = Field(min_length=1)
    nodes: list[StudyPlanNode] = Field(min_length=1)


class StudyPlanEvaluation(BaseModel):
    """Evaluator pass over a draft study plan."""

    verdict: Literal["ship", "revise"]
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    required_changes: list[str] = Field(default_factory=list)
