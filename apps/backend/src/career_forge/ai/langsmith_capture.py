"""CAR-43 — attach LangSmith trace id + real token cost onto GraphRun."""

from __future__ import annotations

import os
from collections.abc import Iterator, Mapping, MutableMapping
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from career_forge.ai.run import GraphRun
from career_forge.services.cost_gate_report import cost_usd_from_usage


def is_langsmith_tracing_enabled(env: Mapping[str, str] | None = None) -> bool:
    """True when LangChain/LangSmith tracing env flags are on."""
    source = env if env is not None else os.environ
    for key in ("LANGCHAIN_TRACING_V2", "LANGSMITH_TRACING"):
        raw = str(source.get(key, "")).strip().lower()
        if raw in {"1", "true", "yes", "on"}:
            return True
    return False


def apply_langsmith_capture(
    run: GraphRun,
    *,
    usage_by_model: dict[str, dict[str, Any]] | None = None,
    langsmith_trace_id: str | None = None,
) -> None:
    """Persist capture fields on ``run`` (caller still saves via GraphRunStore)."""
    if langsmith_trace_id:
        run.langsmith_trace_id = str(langsmith_trace_id)
    if usage_by_model:
        cleaned = {str(model): dict(usage) for model, usage in usage_by_model.items()}
        run.token_usage = cleaned
        run.actual_cost_usd = float(cost_usd_from_usage(cleaned))


class UsageCaptureBag:
    """Mutable bag filled by :func:`usage_capture_context`."""

    def __init__(self) -> None:
        self.usage_by_model: dict[str, dict[str, Any]] = {}
        self.handler: Any | None = None


def attach_usage_callback(
    config: MutableMapping[str, Any],
    bag: UsageCaptureBag,
) -> MutableMapping[str, Any]:
    """Attach UsageMetadataCallbackHandler to RunnableConfig callbacks."""
    try:
        from langchain_core.callbacks.usage import UsageMetadataCallbackHandler
    except ImportError:
        return config

    handler = UsageMetadataCallbackHandler()
    bag.handler = handler
    callbacks = list(config.get("callbacks") or [])
    callbacks.append(handler)
    config["callbacks"] = callbacks
    return config


@contextmanager
def usage_capture_context(bag: UsageCaptureBag) -> Iterator[UsageCaptureBag]:
    """Capture LangChain usage_metadata for nested StructuredToolClient calls."""
    try:
        from langchain_core.callbacks.usage import get_usage_metadata_callback
    except ImportError:
        yield bag
        _merge_handler_usage(bag)
        return

    with get_usage_metadata_callback() as callback:
        yield bag
        bag.usage_by_model = {
            str(k): dict(v) for k, v in dict(callback.usage_metadata).items()
        }
    _merge_handler_usage(bag)


def _merge_handler_usage(bag: UsageCaptureBag) -> None:
    handler = bag.handler
    if handler is None:
        return
    extra = getattr(handler, "usage_metadata", None) or {}
    for model, usage in dict(extra).items():
        bag.usage_by_model.setdefault(str(model), dict(usage))


@contextmanager
def langsmith_parent_trace(
    run: GraphRun,
    config: Mapping[str, Any],
) -> Iterator[str | None]:
    """Open a LangSmith parent run when tracing is enabled; yield its id."""
    if not is_langsmith_tracing_enabled():
        yield None
        return

    try:
        from langsmith import trace as ls_trace
    except ImportError:
        yield None
        return

    metadata = dict(config.get("metadata") or {})
    tags = list(config.get("tags") or [])
    run_name = str(config.get("run_name") or run.graph_name)
    with ls_trace(
        name=run_name,
        run_type="chain",
        inputs=dict(run.input),
        metadata=metadata,
        tags=tags,
    ) as traced:
        yield _coerce_trace_id(traced)


def _coerce_trace_id(traced: Any) -> str | None:
    for attr in ("id", "trace_id"):
        value = getattr(traced, attr, None)
        if value is None:
            continue
        if isinstance(value, UUID):
            return str(value)
        return str(value)
    return None
