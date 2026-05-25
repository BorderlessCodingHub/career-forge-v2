"""Client-facing stream events — normalized from LangChain astream_events v2."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from career_forge.schemas.diagnosis_interview import RubricMapItem
from career_forge.schemas.forge import (
    ArtifactFoundEvent,
    ForgeErrorEvent,
    GraphReadyEvent,
    NodeUpdatedEvent,
    ReasoningDeltaEvent,
    StepCompleteEvent,
)

DiagnosisInterviewStatusPhase = Literal[
    "analyzing_intake",
    "analyzing_cv",
    "judging",
    "planning_questions",
    "processing_answers",
    "finalizing",
]


class InterviewStatusEvent(BaseModel):
    type: Literal["interview_status"] = "interview_status"
    phase: DiagnosisInterviewStatusPhase


class MappingDimensionEvent(BaseModel):
    type: Literal["mapping_dimension"] = "mapping_dimension"
    item: RubricMapItem
    index: int = Field(ge=0)
    total: int = Field(ge=1)


class GraphProgressEvent(BaseModel):
    """Generic progress chunk from non-forge deterministic graphs."""

    type: Literal["progress"] = "progress"
    graph_name: str | None = None
    step: str | None = None
    message: str | None = None


class GraphCompleteEvent(BaseModel):
    type: Literal["graph_complete"] = "graph_complete"
    graph_name: str
    output: dict[str, Any]


StreamEvent = Annotated[
    Union[
        ReasoningDeltaEvent,
        ArtifactFoundEvent,
        NodeUpdatedEvent,
        StepCompleteEvent,
        GraphReadyEvent,
        ForgeErrorEvent,
        InterviewStatusEvent,
        MappingDimensionEvent,
        GraphProgressEvent,
        GraphCompleteEvent,
    ],
    Field(discriminator="type"),
]

_stream_event_adapter = TypeAdapter(StreamEvent)


def parse_stream_event(data: dict[str, Any]) -> StreamEvent:
    """Validate a normalized client stream payload."""
    return _stream_event_adapter.validate_python(data)


def dump_stream_event(event: StreamEvent) -> dict[str, Any]:
    """Serialize a typed stream event for SSE/recording."""
    return event.model_dump()
