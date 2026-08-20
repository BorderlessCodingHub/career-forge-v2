"""GraphExecutor — unified astream_events v2 execution, stream vs collect."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from career_forge.ai.factory import AgentFactory, get_agent_factory
from career_forge.ai.graphs.base import GraphRunnable
from career_forge.ai.langsmith_capture import (
    UsageCaptureBag,
    apply_langsmith_capture,
    attach_usage_callback,
    langsmith_parent_trace,
    usage_capture_context,
)
from career_forge.ai.recording import (
    finalize_run,
    record_normalized_event,
    record_raw_event,
)
from career_forge.ai.run import GraphRun, GraphRunResult, GraphRunStore, get_graph_run_store
from career_forge.ai.streaming.langchain_events import LangChainStreamEvent, parse_langchain_event
from career_forge.ai.streaming.normalize import normalize_langchain_event
from career_forge.ai.tracing import build_trace_config
from career_forge.schemas.forge import ForgeErrorEvent
from career_forge.schemas.stream_events import dump_stream_event
from career_forge.services.cost_guard import CostGuard, get_cost_guard


class GraphExecutor:
    """Always consumes LangChain astream_events v2; one code path for stream/collect."""

    def __init__(
        self,
        factory: AgentFactory | None = None,
        store: GraphRunStore | None = None,
        cost_guard: CostGuard | None = None,
    ) -> None:
        self._factory = factory or get_agent_factory()
        self._store = store or get_graph_run_store()
        self._cost_guard_override = cost_guard

    def _cost_guard(self) -> CostGuard:
        return self._cost_guard_override if self._cost_guard_override is not None else get_cost_guard()

    async def execute(
        self,
        run: GraphRun,
        *,
        stream: bool = False,
    ) -> GraphRunResult | AsyncIterator[dict[str, Any]]:
        self._cost_guard().check(run)
        if stream:
            return self._execute_stream(run)
        return await self._execute_collect(run)

    async def _execute_collect(self, run: GraphRun) -> GraphRunResult:
        runnable = self._factory.get(run.graph_name)
        run.status = "running"
        self._store.save(run)

        try:
            async for _ in self._iter_normalized_events(run, runnable):
                pass
            finalize_run(run)
            self._cost_guard().record(run)
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
                async for payload in self._iter_normalized_events(run, runnable):
                    yield payload
                finalize_run(run)
                self._cost_guard().record(run)
            except Exception as exc:  # noqa: BLE001
                finalize_run(run, error=str(exc))
                yield dump_stream_event(ForgeErrorEvent(message=str(exc)))
                raise
            finally:
                self._store.save(run)

        return _generator()

    async def _iter_normalized_events(
        self,
        run: GraphRun,
        runnable: GraphRunnable,
    ) -> AsyncIterator[dict[str, Any]]:
        config: dict[str, Any] = dict(build_trace_config(run))
        usage_bag = UsageCaptureBag()
        attach_usage_callback(config, usage_bag)
        parent_trace_id: str | None = None

        try:
            with usage_capture_context(usage_bag):
                with langsmith_parent_trace(run, config) as parent_trace_id:
                    async for lc_event in self._astream_events_v2(runnable, run.input, config):
                        record_raw_event(run, lc_event)
                        payload = self._normalize_to_payload(lc_event, run.graph_name)
                        if payload is not None:
                            record_normalized_event(run, payload)
                            yield payload
        finally:
            apply_langsmith_capture(
                run,
                usage_by_model=usage_bag.usage_by_model or None,
                langsmith_trace_id=parent_trace_id,
            )

    def _normalize_to_payload(
        self,
        lc_event: LangChainStreamEvent,
        graph_name: str,
    ) -> dict[str, Any] | None:
        normalized = normalize_langchain_event(lc_event, graph_name)
        if normalized is None:
            return None
        return dump_stream_event(normalized)

    async def _astream_events_v2(
        self,
        runnable: GraphRunnable,
        input_data: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> AsyncIterator[LangChainStreamEvent]:
        async for raw in runnable.astream_events(input_data, version="v2", config=config):
            yield parse_langchain_event(raw)


_default_executor = GraphExecutor()


def get_graph_executor() -> GraphExecutor:
    return _default_executor
