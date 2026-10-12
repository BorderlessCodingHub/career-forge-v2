"""Unit tests — GraphExecutor stream vs collect modes."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.graphs.roadmap_forge import RoadmapForgeGraphRunnable
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.ai.tools.openai_web_search import WebSearchResult, WebSearchSource
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanEvaluation,
    StudyPlanNode,
    StudyPlanTask,
)

_FORGE_DIAGNOSIS = build_diagnosis_response(
    DiagnosisRequest(
        goal_id="backend",
        motivation="APIs para space tech",
        answers={
            "level": "Já programo em JavaScript há alguns meses.",
            "rag-chunking": "Subi um projeto no GitHub.",
        },
    ),
).model_dump()


@pytest.fixture
def executor() -> GraphExecutor:
    factory = AgentFactory()
    factory.register(
        "roadmap_forge",
        lambda: RoadmapForgeGraphRunnable(
            search_client=FakeSearchClient(),
            planner=FakePlanner(),
            evaluator=FakeEvaluator(),
        ),
    )
    return GraphExecutor(factory=factory, store=InMemoryGraphRunStore())


class FakeSearchClient:
    async def search(self, prompt: str) -> WebSearchResult:
        return WebSearchResult(
            query="MDN official docs HTTP",
            summary="Fontes oficiais para HTTP e APIs.",
            sources=[
                WebSearchSource(
                    title="MDN HTTP",
                    url="https://developer.mozilla.org/docs/Web/HTTP",
                    snippet="HTTP docs",
                ),
            ],
        )


class FakeEvaluator:
    async def evaluate(self, plan: StudyPlan, trace=None) -> StudyPlanEvaluation:
        return StudyPlanEvaluation(
            verdict="ship",
            strengths=["plano testável"],
        )


class FakePlanner:
    async def create_plan(
        self,
        *,
        context,
        research_events: list[dict],
        trace=None,
    ) -> StudyPlan:
        return _fake_plan()

    async def revise_plan(
        self,
        *,
        context,
        research_events: list[dict],
        plan: StudyPlan,
        evaluation: StudyPlanEvaluation,
        trace=None,
    ) -> StudyPlan:
        return _fake_plan(strategy="Plano revisado")


def _fake_plan(strategy: str = "Plano inicial") -> StudyPlan:
    return StudyPlan(
        goal="backend",
        learner_context_summary="summary",
        strategy=strategy,
        nodes=[
            StudyPlanNode(
                node_id="python-ai",
                title="Python para IA",
                why_now="Base para projetos AI/ML.",
                tasks=[
                    StudyPlanTask(
                        title="Ler docs",
                        outcome="Criar primeiro notebook.",
                        evidence_prompt="Responder entrevista curta.",
                    ),
                ],
            ),
        ],
    )


@pytest.mark.asyncio
async def test_execute_collect_records_events(executor: GraphExecutor) -> None:
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id="test-user",
        input={"diagnosis": _FORGE_DIAGNOSIS},
    )
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)
    assert result.run.status == "completed"
    assert result.run.raw_events
    assert result.events
    assert result.events[0]["type"] == "reasoning_delta"
    assert any(
        event["type"] == "artifact_found" and event.get("sources")
        for event in result.events
    )
    assert result.events[-1]["type"] == "graph_ready"
    assert result.run.output is not None


@pytest.mark.asyncio
async def test_execute_collect_applies_langsmith_capture(
    executor: GraphExecutor,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LANGCHAIN_TRACING_V2", "true")

    from contextlib import contextmanager

    @contextmanager
    def fake_parent(_run, _config):
        yield "parent-trace-id"

    monkeypatch.setattr(
        "career_forge.ai.executor.langsmith_parent_trace",
        fake_parent,
    )
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id="test-user",
        input={"diagnosis": _FORGE_DIAGNOSIS},
    )
    result = await executor.execute(run, stream=False)
    assert result.run.langsmith_trace_id == "parent-trace-id"


@pytest.mark.asyncio
async def test_execute_stream_yields_normalized_events(
    executor: GraphExecutor,
) -> None:
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id="test-user",
        input={"diagnosis": _FORGE_DIAGNOSIS},
    )
    event_iter = await executor.execute(run, stream=True)
    assert not isinstance(event_iter, GraphRunResult)

    collected = [event async for event in event_iter]
    assert collected
    assert collected[0]["type"] == "reasoning_delta"
    assert collected[-1]["type"] == "graph_ready"

    stored = executor._store.get(run.id)
    assert stored is not None
    assert stored.status == "completed"
    assert len(stored.normalized_events) == len(collected)


@pytest.mark.asyncio
async def test_execute_collect_diagnosis_graph(executor: GraphExecutor) -> None:
    run = GraphRun(
        graph_name="diagnosis",
        user_id="test-user",
        input={
            "goal_id": "backend",
            "motivation": "Quero trabalhar com APIs para space tech no futuro.",
            "answers": {
                "level": "Já programo em JavaScript há alguns meses.",
                "rag-chunking": "Subi um projeto no GitHub.",
            },
        },
    )
    result = await executor.execute(run, stream=False)
    assert result.run.status == "completed"
    assert result.run.output is not None
    assert result.run.output["graph_name"] == "diagnosis"
    assert result.run.output["output"]["profile"]["track_id"] == "rag-engineer-beginner"


_PROVIDER_KEY = "b" * 64
_PROVIDER_DUMP = (
    "Error code: 402 - {'error': {'message': "
    '"This request requires more credits. '
    "Visit https://openrouter.ai/workspaces/default/keys/"
    f"{_PROVIDER_KEY}\", 'code': 402, 'user_id': 'user_example'}}"
)


class _RaisingRunnable:
    graph_name = "roadmap_forge"

    def astream_events(self, input_data, *, version="v2", config=None):
        del input_data, version, config

        async def _events():
            for _ in ():
                yield {}
            raise RuntimeError(_PROVIDER_DUMP)

        return _events()


@pytest.mark.asyncio
async def test_stream_failure_hides_the_provider_dump(caplog: pytest.LogCaptureFixture) -> None:
    from career_forge.ai.llm.errors import PUBLIC_STREAM_ERROR

    factory = AgentFactory()
    factory.register("roadmap_forge", _RaisingRunnable)
    executor = GraphExecutor(factory=factory, store=InMemoryGraphRunStore())
    run = GraphRun(graph_name="roadmap_forge", user_id="learner-1", input={})

    event_iter = await executor.execute(run, stream=True)
    collected: list[dict] = []
    with caplog.at_level("ERROR", logger="career_forge.ai.executor"):
        with pytest.raises(RuntimeError):
            async for event in event_iter:
                collected.append(event)

    assert collected == [{"type": "error", "message": PUBLIC_STREAM_ERROR}]
    assert run.status == "failed"
    assert run.error is not None
    assert "402" in run.error
    assert "[redacted-key-url]" in run.error
    assert "openrouter.ai" not in run.error
    assert _PROVIDER_KEY not in run.error
    assert "openrouter.ai" not in caplog.text
    assert _PROVIDER_KEY not in caplog.text
