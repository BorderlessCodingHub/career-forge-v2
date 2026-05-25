import pytest
from fastapi.testclient import TestClient

from career_forge.main import app
from career_forge.services.diagnosis_session import (
    InMemoryDiagnosisSessionStore,
    set_diagnosis_session_service,
    DiagnosisSessionService,
)

pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(autouse=True)
def _diagnosis_test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DIAGNOSIS_LLM_MODE", "mock")
    monkeypatch.setenv("DIAGNOSIS_SESSION_STORE", "memory")
    set_diagnosis_session_service(
        DiagnosisSessionService(session_store=InMemoryDiagnosisSessionStore()),
    )


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
