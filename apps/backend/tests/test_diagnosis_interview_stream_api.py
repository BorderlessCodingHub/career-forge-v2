"""Integration tests — diagnosis interview SSE stream endpoints (HAC-44)."""

from __future__ import annotations

import json

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
def interview_stream_env() -> None:
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    service = DiagnosisSessionService(session_store=InMemoryDiagnosisSessionStore())
    set_diagnosis_session_service(service)
    yield
    reset_diagnosis_interview_llm()
    set_diagnosis_session_service(None)


def _parse_sse_events(body: str) -> list[dict]:
    events: list[dict] = []
    for block in body.split("\n\n"):
        if not block.strip():
            continue
        event_name = "message"
        data: str | None = None
        for line in block.split("\n"):
            if line.startswith("event: "):
                event_name = line[7:]
            elif line.startswith("data: "):
                data = line[6:]
        if data is None:
            continue
        payload = json.loads(data)
        assert payload.get("type", event_name) == event_name or payload.get("type")
        events.append(payload)
    return events


def test_start_stream_emits_status_mapping_and_complete(client) -> None:
    with client.stream("POST", "/diagnosis/interview/start/stream", json=START_BODY) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        body = response.read().decode("utf-8")

    events = _parse_sse_events(body)
    types = [event["type"] for event in events]

    assert "interview_status" in types
    assert "mapping_dimension" in types
    assert types.count("mapping_dimension") == len(PROFILE_DIMENSION_KEYS)
    assert events[-1]["type"] == "graph_complete"

    output = events[-1]["output"]
    assert output["status"] == "asking"
    assert output["session_id"]
    assert output["questions"]


def test_turn_stream_emits_progress_until_complete(client) -> None:
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
        with client.stream(
            "POST",
            f"/diagnosis/interview/{session_id}/turn/stream",
            json={"answers": answers},
        ) as response:
            assert response.status_code == 200
            body = response.read().decode("utf-8")

        events = _parse_sse_events(body)
        types = [event["type"] for event in events]

        assert "interview_status" in types
        assert "mapping_dimension" in types
        assert events[-1]["type"] == "graph_complete"

        payload = events[-1]["output"]
        rounds += 1

    assert payload["status"] == "complete"
    assert payload["diagnosis"] is not None


def test_start_stream_llm_error_emits_error_event(client) -> None:
    class FailingLlm(MockDiagnosisInterviewLlm):
        async def initialize_belief(self, *args, **kwargs):  # noqa: ANN002, ANN003
            raise DiagnosisInterviewLlmError("Falha simulada — tente novamente.")

    set_diagnosis_interview_llm(FailingLlm())

    with client.stream("POST", "/diagnosis/interview/start/stream", json=START_BODY) as response:
        assert response.status_code == 200
        body = response.read().decode("utf-8")

    events = _parse_sse_events(body)
    assert events[-1]["type"] == "error"
    assert "Falha simulada" in events[-1]["message"]
