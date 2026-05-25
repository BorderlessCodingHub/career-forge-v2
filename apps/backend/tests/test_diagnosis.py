"""Unit tests — diagnosis graph and HTTP API."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.diagnosis import DiagnosisRequest, DiagnosisResponse


SAMPLE_PAYLOAD = DiagnosisRequest(
    user_id="demo-ana",
    goal_id="backend",
    motivation=(
        "Quero trabalhar com APIs para space tech — sonho em escrever os sistemas "
        "que orquestram lançamentos de foguetes."
    ),
    answers={
        "level": "Já programo em JavaScript há alguns meses, mas ainda me sinto iniciante em backend.",
        "prior": "Fiz um curso online de JS e subi um projeto no GitHub.",
        "git": "Sim, subi um projeto no GitHub mas não domino branches.",
        "client_server": "Frontend é o que o usuário vê. Backend processa dados no servidor.",
        "http": "Acho que sim, mas nunca prestei atenção em métodos ou status codes.",
        "db": "Acho que uma tela com formulário… mas o backend salva no banco.",
    },
)


class TestDiagnosisEngine:
    def test_build_diagnosis_response_matches_contract(self) -> None:
        diagnosis = build_diagnosis_response(SAMPLE_PAYLOAD)
        assert isinstance(diagnosis, DiagnosisResponse)
        assert diagnosis.profile.track_id == "backend-beginner"
        assert diagnosis.strengths
        assert diagnosis.gaps
        assert diagnosis.starting_priorities
        assert "http" in diagnosis.estimated_mastery

    def test_space_tech_motivation_boosts_http(self) -> None:
        diagnosis = build_diagnosis_response(SAMPLE_PAYLOAD)
        baseline = build_diagnosis_response(
            SAMPLE_PAYLOAD.model_copy(
                update={
                    "motivation": "Quero aprender backend para construir APIs sólidas no dia a dia.",
                },
            ),
        )
        assert diagnosis.estimated_mastery["http"] >= baseline.estimated_mastery["http"]


@pytest.fixture
def executor() -> GraphExecutor:
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


@pytest.mark.asyncio
async def test_execute_collect_diagnosis_graph(executor: GraphExecutor) -> None:
    run = GraphRun(
        graph_name="diagnosis",
        user_id="test-user",
        input=SAMPLE_PAYLOAD.model_dump(),
    )
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)
    assert result.run.status == "completed"
    assert result.run.output is not None
    assert result.run.output["type"] == "graph_complete"
    assert result.run.output["graph_name"] == "diagnosis"
    diagnosis = DiagnosisResponse.model_validate(result.run.output["output"])
    assert diagnosis.profile.label


def test_post_diagnosis_api(client) -> None:
    response = client.post("/diagnosis", json=SAMPLE_PAYLOAD.model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["run_id"]
    assert payload["diagnosis"]["profile"]["track_id"] == "backend-beginner"
    assert payload["diagnosis"]["strengths"]


def test_post_diagnosis_rejects_empty_answers(client) -> None:
    body = SAMPLE_PAYLOAD.model_dump()
    body["answers"] = {"level": "   "}
    response = client.post("/diagnosis", json=body)
    assert response.status_code == 422
