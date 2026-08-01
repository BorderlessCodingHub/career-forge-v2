"""Forge SSE stream ticket (CAR-26) — mint + ?ticket= validation."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import jwt
import pytest
from fastapi.testclient import TestClient

from career_forge.ai.run import GraphRun, GraphRunResult
from career_forge.auth.stream_tickets import (
    FORGE_STREAM_PURPOSE,
    decode_forge_stream_ticket,
    mint_forge_stream_ticket,
)
from career_forge.config import settings
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.ai.graphs.diagnosis import build_diagnosis_response


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _diagnosis_payload() -> dict[str, Any]:
    return build_diagnosis_response(
        DiagnosisRequest(
            user_id="stream-ticket-user",
            goal_id="rag-engineer",
            motivation="I want to ship grounded RAG systems in production.",
            answers={"level": "beginner"},
        ),
    ).model_dump(mode="json")


def _enqueue_forge(raw_client: TestClient, external_id: str) -> str:
    headers = _auth_headers(raw_client, external_id)
    res = raw_client.post(
        "/forge/runs",
        headers=headers,
        json={"user_id": external_id, "diagnosis": _diagnosis_payload()},
    )
    assert res.status_code == 202, res.text
    return res.json()["run_id"]


def test_mint_stream_ticket_unit() -> None:
    token = mint_forge_stream_ticket("user-a", "run-123")
    claims = decode_forge_stream_ticket(token)
    assert claims == {"sub": "user-a", "run_id": "run-123"}
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    assert payload["purpose"] == FORGE_STREAM_PURPOSE


def test_mint_requires_bearer(raw_client: TestClient) -> None:
    res = raw_client.post("/forge/missing-run/stream-ticket")
    assert res.status_code == 401


def test_mint_for_other_users_run_forbidden(raw_client: TestClient) -> None:
    run_id = _enqueue_forge(raw_client, "stream-ticket-owner")
    thief = _auth_headers(raw_client, "stream-ticket-thief")
    res = raw_client.post(f"/forge/{run_id}/stream-ticket", headers=thief)
    assert res.status_code == 403


def test_mint_missing_run_404(raw_client: TestClient) -> None:
    headers = _auth_headers(raw_client, "stream-ticket-missing")
    res = raw_client.post("/forge/does-not-exist/stream-ticket", headers=headers)
    assert res.status_code == 404


def test_stream_without_ticket_rejected(raw_client: TestClient) -> None:
    run_id = _enqueue_forge(raw_client, "stream-ticket-no-ticket")
    res = raw_client.get(f"/forge/{run_id}/stream")
    assert res.status_code == 401
    assert "ticket" in res.json()["detail"].lower()


def test_stream_with_wrong_run_id_in_ticket_rejected(raw_client: TestClient) -> None:
    run_id = _enqueue_forge(raw_client, "stream-ticket-wrong-run")
    headers = _auth_headers(raw_client, "stream-ticket-wrong-run")
    mint = raw_client.post(f"/forge/{run_id}/stream-ticket", headers=headers)
    assert mint.status_code == 200
    ticket = mint.json()["ticket"]

    other_run = _enqueue_forge(raw_client, "stream-ticket-wrong-run")
    res = raw_client.get(f"/forge/{other_run}/stream", params={"ticket": ticket})
    assert res.status_code == 401


def test_stream_with_valid_ticket_starts_sse(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class _FakeExecutor:
        async def execute(
            self,
            run: GraphRun,
            *,
            stream: bool = False,
        ) -> GraphRunResult | AsyncIterator[dict[str, Any]]:
            assert stream is True

            async def _events() -> AsyncIterator[dict[str, Any]]:
                yield {"type": "reasoning_delta", "text": "ok", "step": "research"}
                yield {"type": "graph_ready", "graph": []}

            return _events()

    monkeypatch.setattr(
        "career_forge.api.forge.get_graph_executor",
        lambda: _FakeExecutor(),
    )
    # Avoid DB writes from persist_graph_ready during stream close.
    monkeypatch.setattr(
        "career_forge.api.forge.persist_graph_ready",
        lambda *args, **kwargs: None,
    )

    external_id = "stream-ticket-ok"
    run_id = _enqueue_forge(raw_client, external_id)
    headers = _auth_headers(raw_client, external_id)
    mint = raw_client.post(f"/forge/{run_id}/stream-ticket", headers=headers)
    assert mint.status_code == 200
    body = mint.json()
    assert body["ticket"]
    assert body["expires_in"] == settings.jwt_stream_ticket_ttl_seconds

    with raw_client.stream(
        "GET",
        f"/forge/{run_id}/stream",
        params={"ticket": body["ticket"]},
    ) as response:
        assert response.status_code == 200
        assert "text/event-stream" in response.headers["content-type"]
        chunks = "".join(response.iter_text())
    assert "reasoning_delta" in chunks
    assert "graph_ready" in chunks
