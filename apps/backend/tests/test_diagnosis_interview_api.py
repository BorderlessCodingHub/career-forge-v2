"""Integration tests — diagnosis interview API (HAC-44)."""

from __future__ import annotations

import pytest

from career_forge.ai.llm.diagnosis_interview import (
    DiagnosisInterviewLlmError,
    MockDiagnosisInterviewLlm,
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.schemas.diagnosis_interview import MAX_INTERVIEW_ROUNDS
from career_forge.services.diagnosis_session import (
    DiagnosisSessionService,
    InMemoryDiagnosisSessionStore,
    set_diagnosis_session_service,
)


START_BODY = {
    "user_id": "test-user",
    "goal_id": "backend",
    "motivation": "Quero migrar de carreira para tecnologia e construir APIs.",
    "years_xp": "0-1",
}


@pytest.fixture(autouse=True)
def interview_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DIAGNOSIS_LLM_MODE", "mock")
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    service = DiagnosisSessionService(session_store=InMemoryDiagnosisSessionStore())
    set_diagnosis_session_service(service)
    yield
    reset_diagnosis_interview_llm()
    set_diagnosis_session_service(None)


def test_post_interview_start_returns_questions(client) -> None:
    response = client.post("/diagnosis/interview/start", json=START_BODY)
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "asking"
    assert payload["session_id"]
    assert 1 <= len(payload["questions"]) <= 2
    assert len(payload["mapping_progress"]) == 8


def test_interview_turn_until_complete(client) -> None:
    start = client.post("/diagnosis/interview/start", json=START_BODY)
    assert start.status_code == 200
    session_id = start.json()["session_id"]
    payload = start.json()

    rounds = 0
    while payload["status"] == "asking" and rounds < MAX_INTERVIEW_ROUNDS + 1:
        answers = [
            {
                "question_id": question["id"],
                "text": "Resposta detalhada com contexto sobre minha jornada de aprendizado.",
            }
            for question in payload["questions"]
        ]
        turn = client.post(
            f"/diagnosis/interview/{session_id}/turn",
            json={"answers": answers},
        )
        assert turn.status_code == 200
        payload = turn.json()
        rounds += 1

    assert payload["status"] == "complete"
    assert payload["diagnosis"] is not None
    assert payload["diagnosis"]["profile"]["track_id"] == "backend-beginner"


def test_turn_unknown_session_404(client) -> None:
    response = client.post(
        "/diagnosis/interview/00000000-0000-0000-0000-000000000099/turn",
        json={
            "answers": [
                {"question_id": "q1", "text": "Resposta válida com texto suficiente."},
            ],
        },
    )
    assert response.status_code == 404


def test_llm_failure_returns_503(client, monkeypatch: pytest.MonkeyPatch) -> None:
    class FailingLlm(MockDiagnosisInterviewLlm):
        async def initialize_belief(self, *args, **kwargs):  # noqa: ANN002, ANN003
            raise DiagnosisInterviewLlmError("Falha simulada — tente novamente.")

    set_diagnosis_interview_llm(FailingLlm())
    response = client.post("/diagnosis/interview/start", json=START_BODY)
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail.get("retry") is True
