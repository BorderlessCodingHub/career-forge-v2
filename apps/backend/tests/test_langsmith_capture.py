"""Unit tests — CAR-43 LangSmith capture helpers."""

from __future__ import annotations

from career_forge.ai.langsmith_capture import (
    apply_langsmith_capture,
    attach_usage_callback,
    is_langsmith_tracing_enabled,
    UsageCaptureBag,
)
from career_forge.ai.run import GraphRun


def test_is_langsmith_tracing_enabled_reads_env_flags() -> None:
    assert is_langsmith_tracing_enabled({"LANGCHAIN_TRACING_V2": "true"}) is True
    assert is_langsmith_tracing_enabled({"LANGSMITH_TRACING": "1"}) is True
    assert is_langsmith_tracing_enabled({"LANGCHAIN_TRACING_V2": "false"}) is False
    assert is_langsmith_tracing_enabled({}) is False


def test_apply_langsmith_capture_sets_cost_from_usage() -> None:
    run = GraphRun(graph_name="tutor", user_id="u1", input={})
    usage = {
        "gpt-4.1-nano": {
            "input_tokens": 1_000_000,
            "output_tokens": 0,
        }
    }
    apply_langsmith_capture(
        run,
        usage_by_model=usage,
        langsmith_trace_id="trace-1",
    )
    assert run.langsmith_trace_id == "trace-1"
    assert run.token_usage == usage
    # gpt-4.1-nano input $0.10 / 1M → $0.10
    assert run.actual_cost_usd == 0.10


def test_attach_usage_callback_adds_handler() -> None:
    bag = UsageCaptureBag()
    config: dict = {"metadata": {"user_id": "u1"}}
    attach_usage_callback(config, bag)
    assert bag.handler is not None
    assert bag.handler in config["callbacks"]
