"""CAR-105 — learner OTP/pilot return 410 in Borderless password mode."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmail
from career_forge.db.session import SessionLocal
from career_forge.services import operator_otp as operator_otp_service
from career_forge.services.otp import reset_otp_rate_limiter


@pytest.fixture
def password_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    monkeypatch.setattr(settings, "identity_email_otp", False)
    reset_otp_rate_limiter()


def test_otp_request_410_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
) -> None:
    res = raw_client.post(
        "/auth/otp/request",
        json={"email": "otp-gone@example.com"},
    )
    assert res.status_code == 410, res.text


def test_otp_verify_410_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
) -> None:
    res = raw_client.post(
        "/auth/otp/verify",
        json={
            "email": "otp-gone@example.com",
            "code": "123456",
            "external_id": "user-otp-gone",
        },
    )
    assert res.status_code == 410, res.text


def test_otp_verify_410_without_external_id_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
) -> None:
    res = raw_client.post(
        "/auth/otp/verify",
        json={"email": "otp-gone@example.com", "code": "123456"},
    )
    assert res.status_code == 410, res.text


def test_pilot_enter_410_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
) -> None:
    with SessionLocal() as session:
        session.merge(BillingPilotEmail(email="listed-gone@example.com"))
        session.commit()
    res = raw_client.post(
        "/auth/pilot/enter",
        json={"email": "listed-gone@example.com"},
    )
    assert res.status_code == 410, res.text


def test_anon_mint_stays_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
) -> None:
    res = raw_client.post("/auth/anon/mint", json={})
    assert res.status_code == 200, res.text


def test_operator_otp_still_200_in_password_mode(
    raw_client: TestClient,
    password_mode: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "operator_allowlist",
        "ops@borderless.com:both",
    )
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "424242")
    requested = raw_client.post(
        "/operator/auth/otp/request",
        json={"email": "ops@borderless.com"},
    )
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": "ops@borderless.com", "code": "424242"},
    )
    assert verified.status_code == 200, verified.text
