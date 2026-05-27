"""Map LangChain astream_events v2 → typed client StreamEvent."""

from __future__ import annotations

from typing import Any, Callable

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    chain_end_output,
    chain_error_message,
    chain_stream_chunk,
)
from career_forge.schemas.forge import parse_forge_event
from career_forge.schemas.stream_events import (
    ForgeErrorEvent,
    GraphCompleteEvent,
    GraphProgressEvent,
    StreamEvent,
    parse_stream_event,
)

GraphNormalizer = Callable[[LangChainStreamEvent], StreamEvent | None]

_GRAPH_NORMALIZERS: dict[str, GraphNormalizer] = {}


def register_graph_normalizer(graph_name: str, normalizer: GraphNormalizer) -> None:
    _GRAPH_NORMALIZERS[graph_name] = normalizer


def normalize_langchain_event(
    lc_event: LangChainStreamEvent | dict[str, Any],
    graph_name: str,
) -> StreamEvent | None:
    """Map one LangChain v2 event to a client-facing StreamEvent, if relevant."""
    from career_forge.ai.streaming.langchain_events import parse_langchain_event

    event = parse_langchain_event(lc_event) if isinstance(lc_event, dict) else lc_event

    custom = _GRAPH_NORMALIZERS.get(graph_name)
    if custom is not None:
        return custom(event)

    return _default_normalizer(event, graph_name)


def _default_normalizer(
    lc_event: LangChainStreamEvent,
    graph_name: str,
) -> StreamEvent | None:
    event_type = lc_event["event"]

    if event_type == "on_chain_stream":
        return _client_event_from_chunk(chain_stream_chunk(lc_event), graph_name)

    if event_type == "on_chain_end":
        output = chain_end_output(lc_event)
        if output is not None:
            return GraphCompleteEvent(graph_name=graph_name, output=_as_dict(output))

    if event_type == "on_chain_error":
        return ForgeErrorEvent(message=chain_error_message(lc_event))

    return None


def _normalize_forge(lc_event: LangChainStreamEvent) -> StreamEvent | None:
    event_type = lc_event["event"]

    if event_type == "on_chain_stream":
        chunk = chain_stream_chunk(lc_event) or {}
        forge_payload = chunk.get("forge_event") if isinstance(chunk, dict) else chunk
        if isinstance(forge_payload, dict) and forge_payload.get("type"):
            return parse_forge_event(forge_payload)

    if event_type == "on_chain_error":
        return ForgeErrorEvent(message=chain_error_message(lc_event))

    return None


def _normalize_diagnosis_interview(lc_event: LangChainStreamEvent) -> StreamEvent | None:
    event_type = lc_event["event"]

    if event_type == "on_chain_stream":
        mapped = _client_event_from_chunk(chain_stream_chunk(lc_event), "diagnosis_interview")
        if mapped is not None:
            return mapped

    if event_type == "on_chain_end":
        output = chain_end_output(lc_event)
        if output is not None:
            return GraphCompleteEvent(
                graph_name="diagnosis_interview",
                output=_as_dict(output),
            )

    if event_type == "on_chain_error":
        return ForgeErrorEvent(message=chain_error_message(lc_event))

    return None


def _client_event_from_chunk(chunk: Any, graph_name: str) -> StreamEvent | None:
    if not isinstance(chunk, dict) or not chunk.get("type"):
        return None
    if chunk.get("type") == "_output":
        return None
    try:
        return parse_stream_event(chunk)
    except Exception:
        if chunk.get("type") == "progress":
            return GraphProgressEvent.model_validate(
                {**chunk, "graph_name": chunk.get("graph_name") or graph_name},
            )
        return None


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if hasattr(value, "model_dump"):
        return value.model_dump()
    msg = "graph output must be a dict or pydantic model"
    raise TypeError(msg)


register_graph_normalizer("roadmap_forge", _normalize_forge)
register_graph_normalizer("diagnosis_interview", _normalize_diagnosis_interview)
