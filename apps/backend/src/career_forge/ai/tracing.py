"""LangSmith trace metadata for StructuredToolClient LLM calls (CAR-42)."""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Any
from uuid import uuid4

from langchain_core.runnables import RunnableConfig

from career_forge.ai.run import GraphRun
from career_forge.config import settings
from career_forge.services.cost_guard import resolve_exclude_reason

logger = logging.getLogger(__name__)

TRACE_INPUT_KEY = "_trace"

_OPTIONAL_INPUT_KEYS = ("goal_id", "node_id", "session_id")


def _resolve_billable(
    user_id: str,
    run_input: dict[str, Any] | None,
    *,
    billable: bool | None,
    exclude_reason: str | None,
) -> tuple[bool, str | None]:
    exclude = exclude_reason
    if exclude is None and run_input is not None:
        exclude = resolve_exclude_reason(user_id, run_input)
    resolved_billable = billable
    if resolved_billable is None:
        resolved_billable = exclude is None
    return resolved_billable, exclude


@dataclass(frozen=True)
class LlmTraceContext:
    """Portable trace metadata for LangSmith filtering and cost analytics."""

    user_id: str
    graph_name: str
    graph_run_id: str
    run_input: dict[str, Any] | None = None
    billable: bool | None = None
    exclude_reason: str | None = None
    operation: str | None = None

    def to_dict(self) -> dict[str, Any]:
        billable, exclude = _resolve_billable(
            self.user_id,
            self.run_input,
            billable=self.billable,
            exclude_reason=self.exclude_reason,
        )
        payload: dict[str, Any] = {
            "user_id": self.user_id,
            "graph_name": self.graph_name,
            "graph_run_id": self.graph_run_id,
            "billable": billable,
            "exclude_reason": exclude,
        }
        if self.operation:
            payload["operation"] = self.operation
        if self.run_input:
            for key in _OPTIONAL_INPUT_KEYS:
                value = self.run_input.get(key)
                if value is not None:
                    payload[key] = value
        return payload

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> LlmTraceContext:
        run_input: dict[str, Any] = {}
        embedded = raw.get("run_input")
        if isinstance(embedded, dict):
            run_input.update(embedded)
        for key in _OPTIONAL_INPUT_KEYS:
            if key in raw and raw[key] is not None:
                run_input[key] = raw[key]
        return cls(
            user_id=str(raw["user_id"]),
            graph_name=str(raw["graph_name"]),
            graph_run_id=str(raw["graph_run_id"]),
            run_input=run_input or None,
            billable=raw.get("billable"),
            exclude_reason=raw.get("exclude_reason"),
            operation=raw.get("operation"),
        )


def llm_trace_context_from_run(
    run: GraphRun,
    *,
    operation: str | None = None,
) -> LlmTraceContext:
    """Build trace context from a persisted GraphRun."""
    billable, exclude = _resolve_billable(
        run.user_id,
        run.input,
        billable=None,
        exclude_reason=None,
    )
    return LlmTraceContext(
        user_id=run.user_id,
        graph_name=run.graph_name,
        graph_run_id=run.id,
        run_input=run.input,
        billable=billable,
        exclude_reason=exclude,
        operation=operation,
    )


def llm_trace_context(
    *,
    user_id: str,
    graph_name: str,
    graph_run_id: str | None = None,
    run_input: dict[str, Any] | None = None,
    operation: str | None = None,
) -> LlmTraceContext:
    """Build trace context for API/background paths without a GraphRun entity."""
    billable, exclude = _resolve_billable(
        user_id,
        run_input,
        billable=None,
        exclude_reason=None,
    )
    return LlmTraceContext(
        user_id=user_id,
        graph_name=graph_name,
        graph_run_id=graph_run_id or str(uuid4()),
        run_input=run_input,
        billable=billable,
        exclude_reason=exclude,
        operation=operation,
    )


def attach_trace_to_run_input(run: GraphRun) -> dict[str, Any]:
    """Embed trace payload on GraphRun input for agent → tool threading."""
    ctx = llm_trace_context_from_run(run)
    return {**run.input, TRACE_INPUT_KEY: ctx.to_dict()}


def with_trace_input(run: GraphRun) -> GraphRun:
    """Return GraphRun with ``_trace`` attached to input."""
    return run.model_copy(update={"input": attach_trace_to_run_input(run)})


def parse_trace_from_input(input_data: dict[str, Any] | None) -> LlmTraceContext | None:
    """Read trace context previously attached via ``with_trace_input``."""
    if not input_data:
        return None
    raw = input_data.get(TRACE_INPUT_KEY)
    if raw is None:
        return None
    if not isinstance(raw, dict):
        logger.warning(
            "Invalid %s on graph input (expected dict, got %s)",
            TRACE_INPUT_KEY,
            type(raw).__name__,
        )
        return None
    try:
        return LlmTraceContext.from_dict(raw)
    except (KeyError, TypeError) as exc:
        logger.warning("Malformed %s on graph input: %s", TRACE_INPUT_KEY, exc)
        return None


def require_trace_from_input(
    input_data: dict[str, Any],
    *,
    graph_name: str,
) -> LlmTraceContext:
    """Parse embedded trace or synthesize one so StructuredToolClient always tags LangSmith."""
    parsed = parse_trace_from_input(input_data)
    if parsed is not None:
        return parsed
    user_id = str(input_data.get("user_id") or "unknown")
    logger.warning(
        "Missing %s for graph_name=%s — synthetic trace context (GraphRun link: CAR-43)",
        TRACE_INPUT_KEY,
        graph_name,
    )
    return llm_trace_context(
        user_id=user_id,
        graph_name=graph_name,
        run_input=input_data,
    )


def build_trace_config(
    ctx: GraphRun | LlmTraceContext,
    *,
    operation: str | None = None,
) -> RunnableConfig:
    """LangChain RunnableConfig for LangSmith metadata + tags."""
    if isinstance(ctx, GraphRun):
        trace = llm_trace_context_from_run(ctx, operation=operation)
    elif operation:
        trace = replace(ctx, operation=operation)
    else:
        trace = ctx

    environment = settings.env.strip().lower() or "production"
    billable, exclude = _resolve_billable(
        trace.user_id,
        trace.run_input,
        billable=trace.billable,
        exclude_reason=trace.exclude_reason,
    )
    metadata = {
        "user_id": trace.user_id,
        "graph_name": trace.graph_name,
        "graph_run_id": trace.graph_run_id,
        "environment": environment,
        "billable": billable,
        "exclude_reason": exclude,
    }
    if trace.operation:
        metadata["operation"] = trace.operation
    if trace.run_input:
        for key in _OPTIONAL_INPUT_KEYS:
            value = trace.run_input.get(key)
            if value is not None:
                metadata[key] = value

    tags = [
        f"graph:{trace.graph_name}",
        f"user:{trace.user_id}",
        f"env:{environment}",
    ]
    if trace.operation:
        tags.append(f"op:{trace.operation}")

    return RunnableConfig(
        run_name=trace.graph_name,
        metadata=metadata,
        tags=tags,
    )


def trace_config_for_invoke(
    trace: LlmTraceContext | None,
    *,
    operation: str | None = None,
) -> RunnableConfig | None:
    """Build LangSmith config when trace context is available."""
    if trace is None:
        return None
    return build_trace_config(trace, operation=operation)
