"""CAR-100 — pilot enter without OTP + exclusive list when IDENTITY_EMAIL_OTP=false."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmail
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.errors import NOT_ALLOWED_CODE, NOT_ALLOWED_MESSAGE
from career_forge.services.otp import reset_otp_rate_limiter


def _email_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def _list_pilot(email: str) -> None:
    with SessionLocal() as session:
        session.merge(BillingPilotEmail(email=email.lower()))
        session.commit()


def test_identity_mode_default_requires_otp(raw_client: TestClient) -> None:
    res = raw_client.get("/auth/identity-mode")
    assert res.status_code == 200, res.text
    assert res.json() == {"email_otp_required": True}


def test_pilot_enter_404_when_otp_required(raw_client: TestClient) -> None:
    _list_pilot("listed@example.com")
    res = raw_client.post("/auth/pilot/enter", json={"email": "listed@example.com"})
    assert res.status_code == 404, res.text


def test_pilot_enter_creates_user_when_listed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    _list_pilot("first@example.com")
    res = raw_client.post(
        "/auth/pilot/enter",
        json={"email": "first@example.com", "external_id": "pilot-first"},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["provider"] == "email"
    assert body["external_id"] == "pilot-first"
    with SessionLocal() as session:
        row = ensure_user(session, "pilot-first")
        assert row.email == "first@example.com"


def test_pilot_enter_adopts_existing_owner(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    email = "owner@example.com"
    _list_pilot(email)
    with SessionLocal() as session:
        owner = ensure_user(session, "pilot-owner")
        owner.email = email
        session.commit()

    res = raw_client.post(
        "/auth/pilot/enter",
        json={"email": email, "external_id": "pilot-other-device"},
    )
    assert res.status_code == 200, res.text
    assert res.json()["external_id"] == "pilot-owner"


def test_pilot_enter_generic_403_when_not_listed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    res = raw_client.post("/auth/pilot/enter", json={"email": "stranger@example.com"})
    assert res.status_code == 403, res.text
    detail = res.json()["detail"]
    assert detail["code"] == NOT_ALLOWED_CODE
    assert detail["message"] == NOT_ALLOWED_MESSAGE


def test_pilot_enter_generic_403_for_malformed_email(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    res = raw_client.post("/auth/pilot/enter", json={"email": "not-an-email"})
    assert res.status_code == 403, res.text
    assert res.json()["detail"]["code"] == NOT_ALLOWED_CODE


def test_product_loop_requires_list_when_otp_off(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    user = "freeze-unlisted"
    headers = _email_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = "unlisted@example.com"
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()

    blocked = raw_client.get("/roadmap/", headers=headers)
    assert blocked.status_code == 403, blocked.text
    assert blocked.json()["detail"]["code"] == NOT_ALLOWED_CODE

    session_res = raw_client.get("/auth/session", headers=headers)
    assert session_res.status_code == 403


def test_product_loop_allows_listed_email_when_otp_off(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    user = "freeze-listed"
    email = "listed-loop@example.com"
    _list_pilot(email)
    headers = _email_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = email
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()

    ok = raw_client.get("/auth/session", headers=headers)
    assert ok.status_code == 204, ok.text


def test_pilot_enter_rate_limited(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_email_otp", False)
    monkeypatch.setattr(settings, "otp_rate_limit_per_email", 2)
    reset_otp_rate_limiter()
    _list_pilot("rate@example.com")
    assert (
        raw_client.post("/auth/pilot/enter", json={"email": "rate@example.com"}).status_code
        == 200
    )
    assert (
        raw_client.post("/auth/pilot/enter", json={"email": "rate@example.com"}).status_code
        == 200
    )
    limited = raw_client.post("/auth/pilot/enter", json={"email": "rate@example.com"})
    assert limited.status_code == 429, limited.text
    reset_otp_rate_limiter()
