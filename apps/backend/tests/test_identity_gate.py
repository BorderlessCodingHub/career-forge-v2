"""Identity gate + paywall before diagnosis (CAR-57 / ADR-005)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.errors import PAYWALL_MESSAGE
from career_forge.services import otp as otp_service


def _anon_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _email_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def test_anon_jwt_rejected_on_product_loop(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "anon-blocked"
    headers = _anon_headers(raw_client, user)

    roadmap = raw_client.get("/roadmap/", headers=headers)
    assert roadmap.status_code == 403, roadmap.text
    assert roadmap.json()["detail"]["code"] == "email_identity_required"

    diagnosis = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": user,
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers=headers,
    )
    assert diagnosis.status_code == 403, diagnosis.text


def test_unpaid_external_diagnosis_start_returns_402(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "diag-paywall"
    headers = _email_headers(raw_client, user)

    res = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": user,
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers=headers,
    )
    assert res.status_code == 402, res.text
    detail = res.json()["detail"]
    assert detail["code"] == "paywall"
    assert detail["message"] == PAYWALL_MESSAGE


def test_base_member_diagnosis_start_allowed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "diag-base"
    headers = _email_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()

    res = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": user,
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers=headers,
    )
    assert res.status_code == 200, res.text


def test_otp_verify_without_bearer_uses_external_id(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "654321")
    external_id = "user-otp-no-bearer"
    req = raw_client.post(
        "/auth/otp/request",
        json={"email": "happy@example.com"},
    )
    assert req.status_code == 200

    verify = raw_client.post(
        "/auth/otp/verify",
        json={
            "email": "happy@example.com",
            "code": "654321",
            "external_id": external_id,
        },
    )
    assert verify.status_code == 200, verify.text
    body = verify.json()
    assert body["external_id"] == external_id
    assert body["provider"] == "email"


def test_otp_verify_still_promotes_anon_bearer(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "112233")
    external_id = "user-otp-promote-migrate"
    headers = _anon_headers(raw_client, external_id)
    raw_client.post("/auth/otp/request", json={"email": "migrate@example.com"})
    verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": "migrate@example.com", "code": "112233"},
        headers=headers,
    )
    assert verify.status_code == 200, verify.text
    assert verify.json()["provider"] == "email"
