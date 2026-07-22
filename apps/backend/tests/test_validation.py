"""Unit tests — validation graph and HTTP API."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.validation import PASS_THRESHOLD, build_validation_response
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.validation import ValidationAnswer, ValidationRequest, ValidationResponse
from career_forge.services.validation import build_validation_questions

STRONG_REST_ANSWERS = [
    ValidationAnswer(
        question_id="rag-grounding-q1",
        answer=(
            "Para um recurso users eu usaria GET /users para listar, GET /users/:id para detalhe, "
            "POST /users para criar, PUT /users/:id para substituir, PATCH para atualizar parcial "
            "e DELETE /users/:id para remover."
        ),
    ),
    ValidationAnswer(
        question_id="rag-grounding-q2",
        answer=(
            "PUT é idempotente — repetir a mesma requisição não cria duplicatas. "
            "POST não é idempotente porque cada chamada pode criar um novo recurso."
        ),
    ),
    ValidationAnswer(
        question_id="rag-grounding-q3",
        answer=(
            "Erros JSON consistentes incluem status code 400 para validação, 404 quando o recurso "
            "não existe e 500 para falha interna, sempre com code, message e details."
        ),
    ),
]

WEAK_REST_ANSWERS = [
    ValidationAnswer(
        question_id="rag-grounding-q1",
        answer="REST é quando duas aplicações trocam dados. POST /users cria usuário.",
    ),
    ValidationAnswer(
        question_id="rag-grounding-q2",
        answer="Acho que POST e PUT são parecidos, não sei direito.",
    ),
    ValidationAnswer(
        question_id="rag-grounding-q3",
        answer="Retorna erro genérico quando dá ruim.",
    ),
]

SAMPLE_PAYLOAD = ValidationRequest(
    user_id="demo-ana",
    node_id="rag-grounding",
    node_title="Grounded generation",
    rubric=[
        "Lista endpoints CRUD para um recurso",
        "Explica idempotência de PUT vs POST",
        "Descreve estrutura de erro JSON consistente",
    ],
    answers=WEAK_REST_ANSWERS,
)


class TestValidationEngine:
    def test_build_validation_response_matches_contract(self) -> None:
        result = build_validation_response(SAMPLE_PAYLOAD)
        assert isinstance(result, ValidationResponse)
        assert 0 <= result.score <= 100
        assert result.status in (ValidationStatus.APROVADO, ValidationStatus.REVISAR)
        assert result.strengths
        assert result.gaps
        assert result.next_action
        assert "mentor" in result.mentor_summary.lower()

    def test_strong_answers_score_higher_than_weak(self) -> None:
        weak = build_validation_response(SAMPLE_PAYLOAD)
        strong = build_validation_response(
            SAMPLE_PAYLOAD.model_copy(update={"answers": STRONG_REST_ANSWERS}),
        )
        assert strong.score > weak.score

    def test_pass_threshold_sets_aprovado(self) -> None:
        strong = build_validation_response(
            SAMPLE_PAYLOAD.model_copy(update={"answers": STRONG_REST_ANSWERS}),
        )
        if strong.score >= PASS_THRESHOLD:
            assert strong.status == ValidationStatus.APROVADO


class TestValidationQuestions:
    def test_build_questions_from_rubric(self) -> None:
        payload = build_validation_questions("rag-retrieval")
        assert payload.node_id == "rag-retrieval"
        assert payload.node_title == "Vector retrieval"
        assert len(payload.questions) == 3
        assert payload.questions[0].prompt
        assert payload.questions[0].rubric_criterion


@pytest.fixture
def executor() -> GraphExecutor:
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


@pytest.mark.asyncio
async def test_execute_collect_validation_graph(executor: GraphExecutor) -> None:
    run = GraphRun(
        graph_name="validation",
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


def test_get_validation_questions_api(client) -> None:
    response = client.get("/validation/questions", params={"node_id": "rag-grounding"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["node_id"] == "rag-grounding"
    assert len(payload["questions"]) == 3


def test_get_validation_questions_unknown_node(client) -> None:
    response = client.get("/validation/questions", params={"node_id": "unknown-node"})
    assert response.status_code == 404


def test_post_validation_api(client) -> None:
    response = client.post("/validation", json=SAMPLE_PAYLOAD.model_dump())
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["run_id"]
    assert payload["validation"]["score"] >= 0
    assert payload["node_id"] == "rag-grounding"
    assert payload["node_status"] in ("aprovado", "revisar")


def test_post_validation_rejects_short_answers(client) -> None:
    body = SAMPLE_PAYLOAD.model_dump()
    body["answers"] = [{"question_id": "rag-grounding-q1", "answer": "   "}]
    response = client.post("/validation", json=body)
    assert response.status_code == 422
