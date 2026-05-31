"""Live Roadmap Forge — SSE events and graph patch (HAC-7)."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from career_forge.schemas.common import (
    Priority,
    SkillStatus,
    UserSkillNode,
    UserSkillNodePartial,
)
from career_forge.schemas.diagnosis import DiagnosisResponse


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


class SearchSource(BaseModel):
    title: str
    url: str
    snippet: str = ""


class ArtifactFoundEvent(BaseModel):
    type: Literal["artifact_found"] = "artifact_found"
    label: str
    detail: str
    sources: list[SearchSource] = Field(default_factory=list)


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


class GraphErrorEvent(BaseModel):
    type: Literal["error"] = "error"
    message: str


# Retrocompat alias — error event emitted by all graphs (renamed HAC-83).
ForgeErrorEvent = GraphErrorEvent


RoadmapForgeEvent = Annotated[
    Union[
        ReasoningDeltaEvent,
        ArtifactFoundEvent,
        NodeUpdatedEvent,
        StepCompleteEvent,
        GraphReadyEvent,
        GraphErrorEvent,
    ],
    Field(discriminator="type"),
]

_forge_event_adapter = TypeAdapter(RoadmapForgeEvent)


def parse_forge_event(data: dict[str, Any]) -> RoadmapForgeEvent:
    """Parse a single SSE payload dict into a typed forge event."""
    return _forge_event_adapter.validate_python(data)


class ForgeRunRequest(BaseModel):
    """Forge run request — profile-based (motor input) or explicit diagnosis."""

    user_id: str = Field(default="demo-ana")
    diagnosis: DiagnosisResponse | None = None
    input: dict[str, Any] = Field(default_factory=dict)


class ForgeRunResponse(BaseModel):
    """Forge run envelope returned by POST /forge (run id + collected output)."""

    run_id: str
    status: str
    events: list[dict[str, Any]]
    output: dict[str, Any] | None = None
