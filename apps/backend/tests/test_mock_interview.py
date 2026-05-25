"""Unit tests — mock interview graph and HTTP API (HAC-14)."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.mock_interview import build_mock_interview_response
from career_forge.ai.graphs.validation import PASS_THRESHOLD
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.mock_interview import MockInterviewRequest
from career_forge.schemas.validation import ValidationAnswer, ValidationResponse
from career_forge.services.mock_interview import build_mock_interview_questions

STRONG_REST_ANSWERS = [
    ValidationAnswer(
        question_id="rest-mi-q1",
        answer=(
            "Para um recurso users eu usaria GET /users para listar, GET /users/:id para detalhe, "
            "POST /users para criar, PUT /users/:id para substituir, PATCH para atualizar parcial "
            "e DELETE /users/:id para remover."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q2",
        answer=(
            "PUT é idempotente — repetir a mesma requisição não cria duplicatas. "
            "POST não é idempotente porque cada chamada pode criar um novo recurso."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q3",
        answer=(
            "Erros JSON consistentes incluem status code 400 para validação, 404 quando o recurso "
            "não existe e 500 para falha interna, sempre com code, message e details."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q4",
        answer=(
            "Para corrigir endpoints CRUD incompletos, eu listaria GET/POST/PUT/PATCH/DELETE "
            "para cada recurso e documentaria o contrato JSON de cada rota."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q5",
        answer=(
            "Na próxima tentativa eu praticaria idempotência PUT vs POST com exemplos curl "
            "e compararia o comportamento de repetir a mesma requisição."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q6",
        answer=(
            "Para projetar rotas REST para tarefas, eu criaria GET /tasks, POST /tasks, "
            "GET /tasks/:id, PUT /tasks/:id, DELETE /tasks/:id com JSON serializado."
        ),
    ),
    ValidationAnswer(
        question_id="rest-mi-q7",
        answer=(
            "Se um colega travou em validar payload, eu mostraria schema JSON com campos "
            "obrigatórios e retorno 400 com message e details consistentes."
        ),
    ),
]

WEAK_REST_ANSWERS = [
    ValidationAnswer(question_id=f"rest-mi-q{i}", answer="Acho que REST troca dados. Não sei direito.")
    for i in range(1, 8)
]

SAMPLE_PAYLOAD = MockInterviewRequest(
    user_id="demo-ana",
    node_id="rest",
    node_title="APIs REST",
    rubric=[
        "Lista endpoints CRUD para um recurso",
        "Explica idempotência de PUT vs POST",
        "Descreve estrutura de erro JSON consistente",
        "Endpoints CRUD incompletos ou genéricos",
        "Idempotência de PUT vs POST não explicada",
        "Projetar rotas REST para um recurso",
        "Validar payload de entrada",
    ],
    answers=WEAK_REST_ANSWERS,
)


class TestMockInterviewEngine:
    def test_build_response_matches_contract(self) -> None:
        result = build_mock_interview_response(SAMPLE_PAYLOAD)
        assert isinstance(result, ValidationResponse)
        assert 0 <= result.score <= 100
        assert result.status in (ValidationStatus.APROVADO, ValidationStatus.REVISAR)
        assert result.strengths
        assert result.gaps
        assert "mock interview" in result.mentor_summary.lower()

    def test_strong_answers_score_higher_than_weak(self) -> None:
        weak = build_mock_interview_response(SAMPLE_PAYLOAD)
        strong = build_mock_interview_response(
            SAMPLE_PAYLOAD.model_copy(update={"answers": STRONG_REST_ANSWERS}),
        )
        assert strong.score > weak.score

    def test_richer_gaps_than_three_question_baseline(self) -> None:
        weak = build_mock_interview_response(SAMPLE_PAYLOAD)
        assert len(weak.gaps) >= 2

    def test_pass_threshold_sets_aprovado(self) -> None:
        strong = build_mock_interview_response(
            SAMPLE_PAYLOAD.model_copy(update={"answers": STRONG_REST_ANSWERS}),
        )
        if strong.score >= PASS_THRESHOLD:
            assert strong.status == ValidationStatus.APROVADO


class TestMockInterviewQuestions:
    def test_build_questions_returns_five_to_seven(self) -> None:
        payload = build_mock_interview_questions("rest")
        assert payload.node_id == "rest"
        assert payload.node_title == "APIs REST"
        assert 5 <= len(payload.questions) <= 7
        assert payload.total_questions == len(payload.questions)

    def test_questions_have_phases(self) -> None:
        payload = build_mock_interview_questions("http")
        phases = {question.phase for question in payload.questions}
        assert "base" in phases
        assert "gap_probe" in phases
        assert "scenario" in phases


@pytest.fixture
def executor() -> GraphExecutor:
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


@pytest.mark.asyncio
async def test_execute_collect_mock_interview_graph(executor: GraphExecutor) -> None:
    run = GraphRun(
        graph_name="mock_interview",
        user_id="test-user",
        input=SAMPLE_PAYLOAD.model_dump(),
    )
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)
    assert result.run.status == "completed"
    assert result.run.output is not None
    assert result.run.output["type"] == "graph_complete"
    validation = ValidationResponse.model_validate(result.run.output["output"])
    assert validation.score >= 0


def test_get_mock_interview_questions_api(client) -> None:
    response = client.get("/mock-interview/questions", params={"node_id": "rest"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["node_id"] == "rest"
    assert 5 <= len(payload["questions"]) <= 7


def test_get_mock_interview_questions_unknown_node(client) -> None:
    response = client.get("/mock-interview/questions", params={"node_id": "unknown-node"})
    assert response.status_code == 404


def test_post_mock_interview_api(client) -> None:
    response = client.post("/mock-interview", json=SAMPLE_PAYLOAD.model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["run_id"]
    assert payload["validation"]["score"] >= 0
    assert payload["node_id"] == "rest"
    assert payload["node_status"] in ("aprovado", "revisar")


def test_post_mock_interview_rejects_too_few_answers(client) -> None:
    body = SAMPLE_PAYLOAD.model_dump()
    body["answers"] = body["answers"][:3]
    response = client.post("/mock-interview", json=body)
    assert response.status_code == 422
