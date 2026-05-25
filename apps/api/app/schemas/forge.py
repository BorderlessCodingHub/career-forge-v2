"""Live Roadmap Forge — SSE events, graph patch, LangGraph state."""

from __future__ import annotations

from typing import Annotated, Any, Literal, TypedDict, Union

from pydantic import BaseModel, Field, TypeAdapter

from app.schemas.common import (
    Artifact,
    ForgeRunStatus,
    Priority,
    ReasoningEntry,
    SkillNode,
    SkillStatus,
    UserSkillNode,
    UserSkillNodePartial,
)
from app.schemas.diagnosis import DiagnosisResponse


class NodePatch(BaseModel):
    """Single node update proposed by the LLM (applied by accumulate_graph)."""

    node_id: str
    status: SkillStatus
    mastery_estimated: int = Field(ge=0, le=100)
    priority: Priority
    rationale: str = ""


class GraphPatch(BaseModel):
    """LLM proposal for node updates — code validates and merges."""

    patches: list[NodePatch] = Field(default_factory=list)
    continue_research: bool = False
    summary: str = ""


class ReasoningDeltaEvent(BaseModel):
    type: Literal["reasoning_delta"] = "reasoning_delta"
    text: str
    step: str


class ArtifactFoundEvent(BaseModel):
    type: Literal["artifact_found"] = "artifact_found"
    label: str
    detail: str


class NodeUpdatedEvent(BaseModel):
    type: Literal["node_updated"] = "node_updated"
    node: UserSkillNodePartial


class StepCompleteEvent(BaseModel):
    type: Literal["step_complete"] = "step_complete"
    step: str
    iteration: int = Field(ge=0)


class GraphReadyEvent(BaseModel):
    type: Literal["graph_ready"] = "graph_ready"
    graph: list[UserSkillNode]


class ForgeErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


RoadmapForgeEvent = Annotated[
    Union[
        ReasoningDeltaEvent,
        ArtifactFoundEvent,
        NodeUpdatedEvent,
        StepCompleteEvent,
        GraphReadyEvent,
        ForgeErrorEvent,
    ],
    Field(discriminator="type"),
]

_forge_event_adapter = TypeAdapter(RoadmapForgeEvent)


def parse_forge_event(data: dict[str, Any]) -> RoadmapForgeEvent:
    """Parse a single SSE payload dict into a typed forge event."""
    return _forge_event_adapter.validate_python(data)


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


def append_reasoning(state: SkillGraphState, entry: ReasoningEntry) -> None:
    state["reasoning_log"].append(entry.model_dump())


def append_artifact(state: SkillGraphState, artifact: Artifact) -> None:
    state["artifacts"].append(artifact.model_dump())
