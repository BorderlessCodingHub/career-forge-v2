import pytest
from fastapi.testclient import TestClient

from career_forge.ai.llm.diagnosis_interview import (
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.ai.run import set_graph_run_store
from career_forge.main import app
from career_forge.services.cost_guard import set_cost_guard
from career_forge.services.diagnosis_session import (
    InMemoryDiagnosisSessionStore,
    set_diagnosis_session_service,
    set_diagnosis_session_store,
    DiagnosisSessionService,
)
from tests.mocks.diagnosis_interview_llm import MockDiagnosisInterviewLlm

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def _diagnosis_test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "local")
    monkeypatch.setenv("DIAGNOSIS_SESSION_STORE", "memory")
    monkeypatch.setenv("GRAPH_RUN_STORE", "memory")
    monkeypatch.setenv("FORGE_STREAM_DELAY_SEC", "0")
    from career_forge.services.mock_interview_session import reset_mock_interview_sessions

    reset_mock_interview_sessions()
    set_graph_run_store(None)
    set_cost_guard(None)
    set_diagnosis_session_store(None)
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    set_diagnosis_session_service(
        DiagnosisSessionService(session_store=InMemoryDiagnosisSessionStore()),
    )
    yield
    reset_mock_interview_sessions()
    reset_diagnosis_interview_llm()
    set_graph_run_store(None)
    set_cost_guard(None)
    set_diagnosis_session_store(None)

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
