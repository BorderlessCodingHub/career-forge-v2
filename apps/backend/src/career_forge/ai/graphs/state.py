"""LangGraph accumulated graph state (SkillGraphState TypedDict)."""

from __future__ import annotations

from typing import Any, TypedDict

from career_forge.schemas.common import ForgeRunStatus, SkillNode
from career_forge.schemas.diagnosis import DiagnosisResponse


class SkillGraphState(TypedDict):
    """Accumulated graph state for LangGraph roadmap_forge_graph."""

    user_id: str
    profile: dict[str, Any]
    base_catalog: list[dict[str, Any]]
    accumulated_graph: list[dict[str, Any]]
    reasoning_log: list[dict[str, Any]]
    artifacts: list[dict[str, Any]]
    iteration: int
    max_iterations: int
    status: ForgeRunStatus


def new_skill_graph_state(
    *,
    user_id: str,
    profile: DiagnosisResponse,
    base_catalog: list[SkillNode],
    max_iterations: int = 3,
) -> SkillGraphState:
    """Factory for initial LangGraph state (serialized dicts)."""
    return SkillGraphState(
        user_id=user_id,
        profile=profile.model_dump(),
        base_catalog=[n.model_dump() for n in base_catalog],
        accumulated_graph=[],
        reasoning_log=[],
        artifacts=[],
        iteration=0,
        max_iterations=max_iterations,
        status="running",
    )
