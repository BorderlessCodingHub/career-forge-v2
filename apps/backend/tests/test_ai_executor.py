"""Unit tests — GraphExecutor stream vs collect modes."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.diagnosis import DiagnosisRequest

_FORGE_DIAGNOSIS = build_diagnosis_response(
    DiagnosisRequest(
        goal_id="backend",
        motivation="APIs para space tech",
        answers={
            "level": "Já programo em JavaScript há alguns meses.",
            "git": "Subi um projeto no GitHub.",
        },
    ),
).model_dump()


@pytest.fixture
def executor() -> GraphExecutor:
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


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
    assert result.events[-1]["type"] == "graph_ready"
    assert result.run.output is not None


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
                "git": "Subi um projeto no GitHub.",
            },
        },
    )
    result = await executor.execute(run, stream=False)
    assert result.run.status == "completed"
    assert result.run.output is not None
    assert result.run.output["graph_name"] == "diagnosis"
    assert result.run.output["output"]["profile"]["track_id"] == "backend-beginner"
