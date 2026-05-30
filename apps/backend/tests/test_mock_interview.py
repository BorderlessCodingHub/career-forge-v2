"""Unit tests — mock interview graph and HTTP API (HAC-14)."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.mock_interview import build_mock_interview_response
from career_forge.ai.graphs.validation import PASS_THRESHOLD
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode, ValidationStatus
from career_forge.schemas.mock_interview import MockInterviewRequest
from career_forge.schemas.validation import ValidationAnswer, ValidationResponse
from career_forge.services.mock_interview import (
    build_mock_interview_questions,
    evaluate_mcq_session,
)
from career_forge.services.mock_interview_session import (
    MockInterviewSessionRecord,
    reset_mock_interview_sessions,
    save_mock_interview_session,
)

GENERATED_NODE_ID = "gen-llm-apis"


def _generated_node() -> UserSkillNode:
    return UserSkillNode(
        node_id=GENERATED_NODE_ID,
        title="APIs para LLMs",
        status=SkillStatus.RECOMENDADO,
        mastery_score=0,
        priority=Priority.HIGH,
        tasks=[
            {
                "title": "Construir um wrapper de provider",
                "outcome": "Wrapper publicado com testes",
                "evidence_prompt": "Mostre como você estrutura chamadas a um provedor de LLM",
            },
            {
                "title": "Tratar rate limits",
                "outcome": "Retry com backoff exponencial",
                "evidence_prompt": "Explique sua estratégia de retry e backoff",
            },
            {
                "title": "Cache de respostas",
                "outcome": "Cache reduz custo de tokens",
                "evidence_prompt": "Como você decide o que cachear e por quanto tempo?",
            },
            {
                "title": "Streaming token a token",
                "outcome": "Stream SSE no cliente",
                "evidence_prompt": "Descreva como você faz streaming token a token via SSE",
            },
        ],
        references=[{"title": "OpenAI docs", "url": "https://platform.openai.com/docs"}],
    )

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


def _mcq_payload_from_questions(client, node_id: str, user_id: str = "demo-ana") -> dict:
    response = client.get(
        "/mock-interview/questions",
        params={"node_id": node_id, "user_id": user_id},
    )
    assert response.status_code == 200
    payload = response.json()
    return {
        "user_id": user_id,
        "node_id": node_id,
        "node_title": payload["node_title"],
        "session_id": payload["session_id"],
        "answers": [
            {"question_id": question["id"], "answer": "A"}
            for question in payload["questions"]
        ],
    }


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


class TestMockInterviewMcqDraft:
    """HAC-66 — subject commitment + per-question concept must reach the public payload."""

    def _draft(self):
        from career_forge.ai.tools.mock_interview_mcq import (
            McqOptionDraft,
            McqQuestionDraft,
            MockInterviewMcqDraft,
        )

        def question(concept: str, correct: str) -> McqQuestionDraft:
            return McqQuestionDraft(
                prompt=f"Pergunta técnica sobre {concept}?",
                label="conceito",
                phase="base",
                concept=concept,
                options=[
                    McqOptionDraft(letter="A", text="Alternativa A correta e técnica"),
                    McqOptionDraft(letter="B", text="Distrator plausível porém inferior"),
                    McqOptionDraft(letter="C", text="Distrator que confunde termos"),
                    McqOptionDraft(letter="D", text="Distrator que pula a evidência"),
                ],
                correct_option=correct,
            )

        return MockInterviewMcqDraft(
            subject="Python para AI/ML",
            questions=[
                question("list comprehension", "A"),
                question("dicionários", "B"),
                question("numpy arrays", "A"),
                question("funções", "C"),
                question("tratamento de erros", "D"),
            ],
        )

    def test_draft_to_public_carries_concept_and_answer_key(self) -> None:
        from career_forge.ai.tools.mock_interview_mcq import _draft_to_public

        public, answer_key, rubric = _draft_to_public(
            "py-min",
            "Python para AI/ML",
            "code",
            self._draft(),
        )

        assert public.format == "mcq"
        assert [q.concept for q in public.questions] == [
            "list comprehension",
            "dicionários",
            "numpy arrays",
            "funções",
            "tratamento de erros",
        ]
        assert rubric == [q.concept for q in public.questions]
        assert answer_key["py-min-mi-q1"] == "A"
        assert answer_key["py-min-mi-q2"] == "B"
        for question in public.questions:
            assert question.rubric_criterion == question.concept
            assert "correct_option" not in question.model_dump()

    def test_draft_requires_subject_and_concept(self) -> None:
        from pydantic import ValidationError

        from career_forge.ai.tools.mock_interview_mcq import McqQuestionDraft

        with pytest.raises(ValidationError):
            McqQuestionDraft(
                prompt="Pergunta sem conceito definido?",
                label="conceito",
                phase="base",
                options=[],
                correct_option="A",
            )


class TestMockInterviewMcq:
    def test_evaluate_mcq_perfect_score(self) -> None:
        reset_mock_interview_sessions()
        save_mock_interview_session(
            MockInterviewSessionRecord(
                session_id="sess-1",
                user_id="demo-ana",
                node_id="rest",
                node_title="APIs REST",
                rubric=["c1", "c2"],
                answer_key={"rest-mi-q1": "A", "rest-mi-q2": "B"},
                questions_public=[],
            ),
        )
        payload = MockInterviewRequest(
            user_id="demo-ana",
            node_id="rest",
            node_title="APIs REST",
            session_id="sess-1",
            answers=[
                ValidationAnswer(question_id="rest-mi-q1", answer="A"),
                ValidationAnswer(question_id="rest-mi-q2", answer="B"),
                ValidationAnswer(question_id="rest-mi-q3", answer="A"),
                ValidationAnswer(question_id="rest-mi-q4", answer="A"),
                ValidationAnswer(question_id="rest-mi-q5", answer="A"),
            ],
        )
        result, _ = evaluate_mcq_session(payload)
        assert result.score == 100
        assert result.status == ValidationStatus.APROVADO


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
    assert payload["format"] == "mcq"
    assert payload["session_id"]
    assert 5 <= len(payload["questions"]) <= 7
    first = payload["questions"][0]
    assert first["options"]
    assert len(first["options"]) == 4
    assert "correct_option" not in first


def test_get_mock_interview_questions_unknown_node(client) -> None:
    response = client.get("/mock-interview/questions", params={"node_id": "unknown-node"})
    assert response.status_code == 404


def test_post_mock_interview_api(client) -> None:
    body = _mcq_payload_from_questions(client, "rest")
    response = client.post("/mock-interview", json=body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "completed"
    assert payload["validation"]["score"] >= 0
    assert payload["node_id"] == "rest"
    assert payload["node_status"] in ("aprovado", "revisar")


def test_post_mock_interview_rejects_too_few_answers(client) -> None:
    body = SAMPLE_PAYLOAD.model_dump()
    body["answers"] = body["answers"][:3]
    response = client.post("/mock-interview", json=body)
    assert response.status_code == 422


def _sync_generated_node(client, user_id: str) -> None:
    response = client.post(
        "/roadmap/sync",
        json={"user_id": user_id, "nodes": [_generated_node().model_dump()]},
    )
    assert response.status_code == 200


def test_get_mock_interview_questions_generated_node(client) -> None:
    """HAC-64/65 — MCQ questions resolve from a persisted AI-generated StudyPlan node."""
    _sync_generated_node(client, "gen-mi-questions")

    response = client.get(
        "/mock-interview/questions",
        params={"node_id": GENERATED_NODE_ID, "user_id": "gen-mi-questions"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["node_id"] == GENERATED_NODE_ID
    assert payload["format"] == "mcq"
    assert payload["session_id"]
    assert 5 <= len(payload["questions"]) <= 7
    assert payload["questions"][0]["options"]


def test_post_mock_interview_generated_node_recalibrates(client) -> None:
    """HAC-64/65 — MCQ submit + recalibration works end-to-end for generated nodes."""
    _sync_generated_node(client, "gen-mi-submit")

    body = _mcq_payload_from_questions(client, GENERATED_NODE_ID, user_id="gen-mi-submit")
    response = client.post("/mock-interview", json=body)
    assert response.status_code == 200
    payload = response.json()
    assert payload["node_id"] == GENERATED_NODE_ID
    assert payload["node_status"] in ("aprovado", "revisar")
    assert payload["roadmap"] is not None
    generated = [n for n in payload["roadmap"]["nodes"] if n["node_id"] == GENERATED_NODE_ID]
    assert generated
    assert generated[0]["tasks"]
