from urllib.parse import parse_qs, urlparse

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

# Longer than RFC minimum to silence InsecureKeyLengthWarning in tests.
_TEST_JWT_SECRET = "test-jwt-secret-car-23-long-enough-32b"


@pytest.fixture(autouse=True)
def _diagnosis_test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ENV", "local")
    monkeypatch.setenv("DIAGNOSIS_SESSION_STORE", "memory")
    monkeypatch.setenv("GRAPH_RUN_STORE", "memory")
    monkeypatch.setenv("FORGE_STREAM_DELAY_SEC", "0")
    monkeypatch.setenv("JWT_SECRET", _TEST_JWT_SECRET)
    from career_forge.services.mock_interview_session import reset_mock_interview_sessions

    reset_mock_interview_sessions()
    set_graph_run_store(None)
    set_cost_guard(None)
    set_diagnosis_session_store(None)
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    set_diagnosis_session_service(
        DiagnosisSessionService(session_store=InMemoryDiagnosisSessionStore()),
    )
    from career_forge.config import settings
    from career_forge.services.otp import reset_otp_rate_limiter

    settings.jwt_secret = _TEST_JWT_SECRET
    reset_otp_rate_limiter()
    yield
    reset_mock_interview_sessions()
    reset_diagnosis_interview_llm()
    set_graph_run_store(None)
    set_cost_guard(None)
    set_diagnosis_session_store(None)
    reset_otp_rate_limiter()


@pytest.fixture
def raw_client():
    """Unauthenticated TestClient — for mint / 401 middleware tests."""
    with TestClient(app) as test_client:
        yield test_client


def _infer_external_id(url: str, kwargs: dict) -> str:
    json_body = kwargs.get("json")
    if isinstance(json_body, dict) and isinstance(json_body.get("user_id"), str):
        return json_body["user_id"]
    params = kwargs.get("params")
    if isinstance(params, dict) and isinstance(params.get("user_id"), str):
        return params["user_id"]
    query = parse_qs(urlparse(url).query)
    if "user_id" in query and query["user_id"]:
        return query["user_id"][0]
    content = kwargs.get("content")
    if isinstance(content, (bytes, bytearray)):
        try:
            import json

            parsed = json.loads(content.decode())
            if isinstance(parsed, dict) and isinstance(parsed.get("user_id"), str):
                return parsed["user_id"]
        except Exception:
            pass
    return "test-user-car23"


@pytest.fixture
def client(raw_client: TestClient):
    """Authenticated TestClient — Bearer ``sub`` matches body/query ``user_id`` when present.

    Patches ``send`` (not only ``request``) so ``client.stream(...)`` also gets Bearer —
    httpx ``stream()`` builds a request then calls ``send`` directly.
    """
    token_cache: dict[str, str] = {}
    original_send = raw_client.send

    def mint_token(external_id: str) -> str:
        cached = token_cache.get(external_id)
        if cached:
            return cached
        # Mint via original send to avoid recursion.
        mint_req = raw_client.build_request(
            "POST",
            "/auth/anon/mint",
            json={"external_id": external_id},
        )
        res = original_send(mint_req)
        assert res.status_code == 200, res.text
        token = res.json()["access_token"]
        token_cache[external_id] = token
        return token

    def send_with_auth(request, **kwargs):
        path = request.url.path
        public = (
            path.rstrip("/").endswith("/health")
            or path.endswith("/auth/anon/mint")
            or path.rstrip("/").endswith("/openapi.json")
        )
        if not public and "authorization" not in {k.lower() for k in request.headers.keys()}:
            external_id = "test-user-car23"
            body = request.content
            if body:
                try:
                    import json

                    parsed = json.loads(body.decode())
                    if isinstance(parsed, dict) and isinstance(parsed.get("user_id"), str):
                        external_id = parsed["user_id"]
                except Exception:
                    pass
            # httpx URL.params is the reliable query map (url.query string can be empty
            # depending on how the request was built).
            params = request.url.params
            user_from_query = params.get("user_id")
            if isinstance(user_from_query, str) and user_from_query:
                external_id = user_from_query
            token = mint_token(external_id)
            request.headers.update({"Authorization": f"Bearer {token}"})
        return original_send(request, **kwargs)

    raw_client.send = send_with_auth  # type: ignore[method-assign]
    yield raw_client


@pytest.fixture
def auth_external_id() -> str:
    return "test-user-car23"
