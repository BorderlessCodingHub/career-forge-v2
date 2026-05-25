"""Unit tests — roadmap forge graph and HTTP API."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.graphs.roadmap_forge import (
    build_accumulated_graph,
    build_forge_timeline,
)
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
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
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


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
    assert result.events[-1]["type"] == "graph_ready"
    assert len(result.events[-1]["graph"]) >= 6


def test_post_forge_api(client, diagnosis_dict: dict) -> None:
    response = client.post(
        "/forge",
        json={"user_id": "demo-ana", "diagnosis": diagnosis_dict},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "pending"
    assert payload["run_id"]
    assert payload["events"] == []
