"""LangChain astream_events v2 schema mirror + emit helpers.

Reference: langchain_core.runnables.schema (StreamEvent, EventData) and
langchain_core.runnables.base.Runnable.astream_events version=\"v2\" docs.
"""

from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict
from uuid import uuid4

# --- Standard v2 event names (LangChain docs table) ---

LangChainStandardEventName = Literal[
    "on_chat_model_start",
    "on_chat_model_stream",
    "on_chat_model_end",
    "on_llm_start",
    "on_llm_stream",
    "on_llm_end",
    "on_chain_start",
    "on_chain_stream",
    "on_chain_end",
    "on_tool_start",
    "on_tool_end",
    "on_retriever_start",
    "on_retriever_end",
    "on_prompt_start",
    "on_prompt_end",
    "on_custom_event",
]

# Emitted by Career Forge mock runnables when graph logic fails before chain end.
LangChainGraphErrorEventName = Literal["on_chain_error"]

LangChainStreamEventName = LangChainStandardEventName | LangChainGraphErrorEventName

LANGCHAIN_STANDARD_EVENT_NAMES: tuple[str, ...] = (
    "on_chat_model_start",
    "on_chat_model_stream",
    "on_chat_model_end",
    "on_llm_start",
    "on_llm_stream",
    "on_llm_end",
    "on_chain_start",
    "on_chain_stream",
    "on_chain_end",
    "on_tool_start",
    "on_tool_end",
    "on_retriever_start",
    "on_retriever_end",
    "on_prompt_start",
    "on_prompt_end",
    "on_custom_event",
)

LANGCHAIN_GRAPH_EVENT_NAMES: tuple[str, ...] = (
    *LANGCHAIN_STANDARD_EVENT_NAMES,
    "on_chain_error",
)


class LangChainEventData(TypedDict, total=False):
    """Payload attached to a LangChain stream event (mirrors EventData + error)."""

    input: Any
    output: Any
    chunk: Any
    error: Any


class LangChainStreamEvent(TypedDict):
    """Single event from Runnable.astream_events(..., version=\"v2\")."""

    event: LangChainStreamEventName
    name: str
    run_id: str
    data: LangChainEventData
    tags: NotRequired[list[str]]
    metadata: NotRequired[dict[str, Any]]
    parent_ids: NotRequired[list[str]]


def new_run_id() -> str:
    return str(uuid4())


def emit_langchain_event(
    event: LangChainStreamEventName,
    name: str,
    run_id: str,
    data: LangChainEventData | None = None,
    *,
    tags: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
    parent_ids: list[str] | None = None,
) -> LangChainStreamEvent:
    payload: LangChainStreamEvent = {
        "event": event,
        "name": name,
        "run_id": run_id,
        "data": data or {},
        "tags": tags or [],
        "metadata": metadata or {},
    }
    if parent_ids is not None:
        payload["parent_ids"] = parent_ids
    return payload


def emit_chain_start(
    name: str,
    run_id: str,
    *,
    input_data: Any | None = None,
) -> LangChainStreamEvent:
    data: LangChainEventData = {}
    if input_data is not None:
        data["input"] = input_data
    return emit_langchain_event("on_chain_start", name, run_id, data)


def emit_chain_stream(
    name: str,
    run_id: str,
    chunk: Any,
) -> LangChainStreamEvent:
    return emit_langchain_event("on_chain_stream", name, run_id, {"chunk": chunk})


def emit_chain_end(
    name: str,
    run_id: str,
    *,
    output: Any,
    input_data: Any | None = None,
) -> LangChainStreamEvent:
    data: LangChainEventData = {"output": output}
    if input_data is not None:
        data["input"] = input_data
    return emit_langchain_event("on_chain_end", name, run_id, data)


def emit_chain_error(
    name: str,
    run_id: str,
    error: str | BaseException,
) -> LangChainStreamEvent:
    message = str(error)
    return emit_langchain_event("on_chain_error", name, run_id, {"error": message})


def parse_langchain_event(raw: dict[str, Any]) -> LangChainStreamEvent:
    """Best-effort structural validation for executor ingress."""
    event = raw.get("event")
    if event not in LANGCHAIN_GRAPH_EVENT_NAMES:
        msg = f"unsupported LangChain stream event: {event!r}"
        raise ValueError(msg)
    name = raw.get("name")
    run_id = raw.get("run_id")
    if not isinstance(name, str) or not isinstance(run_id, str):
        msg = "LangChain stream event requires string name and run_id"
        raise ValueError(msg)
    data = raw.get("data")
    if data is not None and not isinstance(data, dict):
        msg = "LangChain stream event data must be a dict"
        raise ValueError(msg)
    return {
        "event": event,
        "name": name,
        "run_id": run_id,
        "data": data or {},
        "tags": list(raw.get("tags") or []),
        "metadata": dict(raw.get("metadata") or {}),
        **({"parent_ids": list(raw["parent_ids"])} if raw.get("parent_ids") else {}),
    }


def chain_stream_chunk(lc_event: LangChainStreamEvent) -> Any | None:
    return lc_event.get("data", {}).get("chunk")


def chain_end_output(lc_event: LangChainStreamEvent) -> Any | None:
    return lc_event.get("data", {}).get("output")


def chain_error_message(lc_event: LangChainStreamEvent) -> str:
    data = lc_event.get("data", {})
    return str(data.get("error") or lc_event.get("name") or "graph error")
