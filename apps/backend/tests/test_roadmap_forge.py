"""Unit tests — roadmap forge graph and HTTP API."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.graphs.roadmap_forge import (
    RoadmapForgeGraphRunnable,
    build_accumulated_graph,
    build_forge_timeline,
)
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.ai.tools.openai_web_search import WebSearchResult, WebSearchSource
from career_forge.schemas.study_plan import StudyPlan, StudyPlanEvaluation
from career_forge.schemas.diagnosis import DiagnosisRequest

_SAMPLE = DiagnosisRequest(
    user_id="demo-ana",
    goal_id="backend",
    motivation="APIs para space tech",
    answers={
        "level": "Já programo em JavaScript há alguns meses.",
        "git": "Subi um projeto no GitHub.",
    },
)


@pytest.fixture
def diagnosis_dict() -> dict:
    return build_diagnosis_response(_SAMPLE).model_dump()


class TestRoadmapForgeEngine:
    def test_build_accumulated_graph_has_catalog_nodes(
        self, diagnosis_dict: dict,
    ) -> None:
        from career_forge.schemas.diagnosis import DiagnosisResponse

        diagnosis = DiagnosisResponse.model_validate(diagnosis_dict)
        graph = build_accumulated_graph(diagnosis)
        node_ids = {node.node_id for node in graph}
        assert "http" in node_ids
        assert "final" in node_ids

    def test_timeline_ends_with_graph_ready(self, diagnosis_dict: dict) -> None:
        from career_forge.schemas.diagnosis import DiagnosisResponse

        diagnosis = DiagnosisResponse.model_validate(diagnosis_dict)
        timeline = build_forge_timeline(diagnosis)
        assert timeline[-1]["type"] == "graph_ready"
        assert timeline[0]["type"] == "reasoning_delta"


@pytest.fixture
def executor() -> GraphExecutor:
    factory = AgentFactory()
    factory.register(
        "roadmap_forge",
        lambda: RoadmapForgeGraphRunnable(
            search_client=FakeSearchClient(),
            evaluator=FakeEvaluator(),
        ),
    )
    return GraphExecutor(factory=factory, store=InMemoryGraphRunStore())


class FakeSearchClient:
    async def search(self, prompt: str) -> WebSearchResult:
        return WebSearchResult(
            query="FastAPI official docs APIs",
            summary="Fontes oficiais para APIs modernas.",
            sources=[
                WebSearchSource(
                    title="FastAPI",
                    url="https://fastapi.tiangolo.com/",
                    snippet="FastAPI docs",
                ),
            ],
        )


class FakeEvaluator:
    async def evaluate(self, plan: StudyPlan) -> StudyPlanEvaluation:
        return StudyPlanEvaluation(
            verdict="ship",
            strengths=["sequência inicial clara"],
        )


@pytest.mark.asyncio
async def test_roadmap_forge_graph_collect(
    executor: GraphExecutor,
    diagnosis_dict: dict,
) -> None:
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id="test-user",
        input={"diagnosis": diagnosis_dict},
    )
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)
    assert result.run.status == "completed"
    assert any(
        event["type"] == "artifact_found" and event.get("sources")
        for event in result.events
    )
    assert any(
        event["type"] == "artifact_found"
        and event.get("label") == "Avaliador do plano: ship"
        for event in result.events
    )
    assert result.events[-1]["type"] == "graph_ready"
    assert len(result.events[-1]["graph"]) >= 6


def test_post_forge_api(client, diagnosis_dict: dict) -> None:
    response = client.post(
        "/forge",
        json={"user_id": "demo-ana", "diagnosis": diagnosis_dict},
    )
    assert response.status_code == 202
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["run_id"]
    assert payload["events"] == []
