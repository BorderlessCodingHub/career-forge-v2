"""Integration tests — diagnosis interview API (HAC-44)."""

from __future__ import annotations

import pytest

from career_forge.ai.llm.diagnosis_interview import (
    DiagnosisInterviewLlmError,
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.schemas.diagnosis_interview import MAX_INTERVIEW_ROUNDS, PROFILE_DIMENSION_KEYS
from career_forge.services.diagnosis_session import (
    DiagnosisSessionService,
    InMemoryDiagnosisSessionStore,
    set_diagnosis_session_service,
)
from tests.mocks.diagnosis_interview_llm import MockDiagnosisInterviewLlm


START_BODY = {
    "user_id": "test-user",
    "goal_id": "fullstack",
    "motivation": "Quero migrar de carreira para tecnologia e construir APIs.",
    "years_xp": "0-1",
}


@pytest.fixture(autouse=True)
def interview_test_env(monkeypatch: pytest.MonkeyPatch) -> None:
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
    assert payload["round_count"] == 1
    assert 1 <= len(payload["questions"]) <= 2
    assert len(payload["mapping_progress"]) == len(PROFILE_DIMENSION_KEYS)


def test_get_interview_session_resumes_open_turn(client) -> None:
    start = client.post("/diagnosis/interview/start", json=START_BODY)
    session_id = start.json()["session_id"]

    resume = client.get(f"/diagnosis/interview/{session_id}")
    assert resume.status_code == 200
    payload = resume.json()
    assert payload["session_id"] == session_id
    assert payload["status"] == "asking"
    assert payload["round_count"] == 1
    assert len(payload["questions"]) >= 1
    assert len(payload["mapping_progress"]) == len(PROFILE_DIMENSION_KEYS)


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
                "text": (
                    "Montei um app na faculdade com GitHub, estudo 6h por semana "
                    "e uso tutoriais em inglês."
                ),
            }
            for question in payload["questions"]
        ]
        turn = client.post(
            f"/diagnosis/interview/{session_id}/turn",
            json={"answers": answers},
        )
        assert turn.status_code == 200, turn.text
        payload = turn.json()
        rounds += 1

    assert payload["status"] == "complete"
    assert payload["diagnosis"] is not None
    assert payload["diagnosis"]["profile"]["track_id"] == "fullstack-beginner"


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
