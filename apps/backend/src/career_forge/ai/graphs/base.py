"""Graph builder protocol and mock runnable for scaffold/tests."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)

FIXTURES_DIR = (
    Path(__file__).resolve().parents[2] / "fixtures"
)


@runtime_checkable
class GraphRunnable(Protocol):
    """Minimal runnable surface consumed by GraphExecutor."""

    graph_name: str

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]: ...


@runtime_checkable
class BaseGraphBuilder(Protocol):
    """Register builders that produce configured graph runnables."""

    def build(self) -> GraphRunnable: ...


class MockGraphRunnable:
    """Simulates LangChain astream_events v2 until LangGraph is wired."""

    def __init__(
        self,
        graph_name: str,
        *,
        stream_fixture: str | None = None,
        end_output: dict[str, Any] | None = None,
    ) -> None:
        self.graph_name = graph_name
        self._stream_fixture = stream_fixture
        self._end_output = end_output or {
            "type": "graph_complete",
            "graph_name": graph_name,
            "status": "mock",
        }

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        run_id = new_run_id()
        yield emit_chain_start(self.graph_name, run_id)

        if self._stream_fixture:
            events = _load_fixture_list(self._stream_fixture)
            for payload in events:
                yield emit_chain_stream(
                    "emit_forge_event",
                    run_id,
                    {"forge_event": payload},
                )
            if events and events[-1].get("type") == "graph_ready":
                self._end_output = events[-1]
        else:
            yield emit_chain_stream(
                self.graph_name,
                run_id,
                {"type": "progress", "graph_name": self.graph_name},
            )

        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=self._end_output,
            input_data=input_data,
        )


def _load_fixture_list(name: str) -> list[dict[str, Any]]:
    path = FIXTURES_DIR / name
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        msg = f"Expected list fixture at {path}"
        raise TypeError(msg)
    return payload
