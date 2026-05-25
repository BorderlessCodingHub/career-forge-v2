"""Normalize LangChain astream_events v2 payloads → domain SSE schemas."""

from __future__ import annotations

from typing import Any

from career_forge.schemas.forge import parse_forge_event


def normalize_langchain_event(
    lc_event: dict[str, Any],
    graph_name: str,
) -> dict[str, Any] | None:
    """Map a single astream_events v2 dict to a client-facing event dict."""
    event_type = lc_event.get("event")
    data = lc_event.get("data") or {}

    if graph_name == "roadmap_forge":
        return _normalize_forge_event(lc_event, event_type, data)

    if graph_name == "diagnosis_interview":
        return _normalize_diagnosis_interview_event(lc_event, event_type, data)

    if event_type == "on_chain_end":
        output = data.get("output")
        if output is not None:
            return {
                "type": "graph_complete",
                "graph_name": graph_name,
                "output": output,
            }

    if event_type == "on_chain_stream":
        chunk = data.get("chunk")
        if isinstance(chunk, dict) and chunk.get("type"):
            return chunk

    return None


def _normalize_diagnosis_interview_event(
    lc_event: dict[str, Any],
    event_type: str | None,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    if event_type == "on_chain_stream":
        chunk = data.get("chunk")
        if isinstance(chunk, dict) and chunk.get("type"):
            return chunk

    if event_type == "on_chain_end":
        output = data.get("output")
        if output is not None:
            return {
                "type": "graph_complete",
                "graph_name": "diagnosis_interview",
                "output": output,
            }

    if event_type == "on_chain_error":
        return {
            "type": "error",
            "message": str(data.get("error") or lc_event.get("name") or "graph error"),
        }

    return None


def _normalize_forge_event(
    lc_event: dict[str, Any],
    event_type: str | None,
    data: dict[str, Any],
) -> dict[str, Any] | None:
    if event_type == "on_chain_stream":
        chunk = data.get("chunk") or {}
        forge_payload = chunk.get("forge_event") or chunk
        if isinstance(forge_payload, dict) and forge_payload.get("type"):
            parsed = parse_forge_event(forge_payload)
            return parsed.model_dump()

    if event_type == "on_chain_end":
        output = data.get("output")
        if isinstance(output, dict) and output.get("type") == "graph_ready":
            parsed = parse_forge_event(output)
            return parsed.model_dump()

    if event_type == "on_chain_error":
        return {
            "type": "error",
            "message": str(data.get("error") or lc_event.get("name") or "graph error"),
        }

    return None
