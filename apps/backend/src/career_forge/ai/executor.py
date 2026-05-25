"""GraphExecutor — unified astream_events v2 execution, stream vs collect."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from career_forge.ai.factory import AgentFactory, get_agent_factory
from career_forge.ai.graphs.base import GraphRunnable
from career_forge.ai.recording import (
    finalize_run,
    record_normalized_event,
    record_raw_event,
)
from career_forge.ai.run import GraphRun, GraphRunResult, GraphRunStore, get_graph_run_store
from career_forge.ai.streaming.events import normalize_langchain_event


class GraphExecutor:
    """Always consumes LangChain astream_events v2; one code path for stream/collect."""

    def __init__(
        self,
        factory: AgentFactory | None = None,
        store: GraphRunStore | None = None,
    ) -> None:
        self._factory = factory or get_agent_factory()
        self._store = store or get_graph_run_store()

    async def execute(
        self,
        run: GraphRun,
        *,
        stream: bool = False,
    ) -> GraphRunResult | AsyncIterator[dict[str, Any]]:
        if stream:
            return self._execute_stream(run)
        return await self._execute_collect(run)

    async def _execute_collect(self, run: GraphRun) -> GraphRunResult:
        runnable = self._factory.get(run.graph_name)
        run.status = "running"
        self._store.save(run)

        try:
            async for lc_event in self._astream_events_v2(runnable, run.input):
                record_raw_event(run, lc_event)
                normalized = normalize_langchain_event(lc_event, run.graph_name)
                if normalized is not None:
                    record_normalized_event(run, normalized)
            finalize_run(run)
        except Exception as exc:  # noqa: BLE001 — record run failure centrally
            finalize_run(run, error=str(exc))
            self._store.save(run)
            raise

        self._store.save(run)
        return GraphRunResult(run=run, events=list(run.normalized_events))

    def _execute_stream(self, run: GraphRun) -> AsyncIterator[dict[str, Any]]:
        runnable = self._factory.get(run.graph_name)
        run.status = "running"
        self._store.save(run)

        async def _generator() -> AsyncIterator[dict[str, Any]]:
            try:
                async for lc_event in self._astream_events_v2(runnable, run.input):
                    record_raw_event(run, lc_event)
                    normalized = normalize_langchain_event(lc_event, run.graph_name)
                    if normalized is not None:
                        record_normalized_event(run, normalized)
                        yield normalized
                finalize_run(run)
            except Exception as exc:  # noqa: BLE001
                finalize_run(run, error=str(exc))
                yield {"type": "error", "message": str(exc)}
                raise
            finally:
                self._store.save(run)

        return _generator()

    async def _astream_events_v2(
        self,
        runnable: GraphRunnable,
        input_data: dict[str, Any],
    ) -> AsyncIterator[dict[str, Any]]:
        async for event in runnable.astream_events(input_data, version="v2"):
            yield event


_default_executor = GraphExecutor()


def get_graph_executor() -> GraphExecutor:
    return _default_executor
