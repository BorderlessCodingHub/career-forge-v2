"""Graph runnable protocol and mock runnable for scaffold/tests."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Protocol, runtime_checkable

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
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


class MockGraphRunnable:
    """Simulates LangChain astream_events v2 until LangGraph is wired."""

    def __init__(
        self,
        graph_name: str,
        *,
        end_output: dict[str, Any] | None = None,
    ) -> None:
        self.graph_name = graph_name
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
