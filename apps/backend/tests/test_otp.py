"""Email OTP IdP — request / verify / promote / conflict (CAR-44)."""

from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.services import otp as otp_service


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_otp_request_is_public(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "424242")
    res = raw_client.post(
        "/auth/otp/request",
        json={"email": "pilot@example.com"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["ok"] is True
    assert body["email"] == "pilot@example.com"
    assert body["expires_in"] == settings.otp_ttl_seconds
    assert "code" not in body


def test_otp_verify_promotes_anon_and_mints_email_jwt(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "111222")
    headers = _auth_headers(raw_client, "user-otp-promote")

    req = raw_client.post(
        "/auth/otp/request",
        json={"email": "new-pilot@example.com"},
        headers=headers,
    )
    assert req.status_code == 200

    verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": "new-pilot@example.com", "code": "111222"},
        headers=headers,
    )
    assert verify.status_code == 200
    body = verify.json()
    assert body["status"] == "promoted"
    assert body["provider"] == EMAIL_PROVIDER
    assert body["external_id"] == "user-otp-promote"
    assert body["access_token"]

    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret,
        algorithms=["HS256"],
    )
    assert payload["sub"] == "user-otp-promote"
    assert payload["provider"] == EMAIL_PROVIDER

    roadmap = raw_client.get(
        "/roadmap/",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert roadmap.status_code == 200

    with SessionLocal() as session:
        user = session.scalar(
            select(User).where(User.external_id == "user-otp-promote"),
        )
        assert user is not None
        assert user.email == "new-pilot@example.com"


def test_otp_verify_conflict_when_email_owned(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "333444")

    owner_headers = _auth_headers(raw_client, "user-otp-owner")
    raw_client.post(
        "/auth/otp/request",
        json={"email": "owned@example.com"},
        headers=owner_headers,
    )
    owner_verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": "owned@example.com", "code": "333444"},
        headers=owner_headers,
    )
    assert owner_verify.status_code == 200

    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "555666")
    anon_headers = _auth_headers(raw_client, "user-otp-anon")
    raw_client.post(
        "/auth/otp/request",
        json={"email": "owned@example.com"},
        headers=anon_headers,
    )
    conflict = raw_client.post(
        "/auth/otp/verify",
        json={"email": "owned@example.com", "code": "555666"},
        headers=anon_headers,
    )
    assert conflict.status_code == 409
    detail = conflict.json()["detail"]
    assert detail["code"] == "email_owned"
    existing = detail["existing"]
    assert existing["external_id"] == "user-otp-owner"
    assert existing["provider"] == EMAIL_PROVIDER
    assert existing["access_token"]

    payload = jwt.decode(
        existing["access_token"],
        settings.jwt_secret,
        algorithms=["HS256"],
    )
    assert payload["sub"] == "user-otp-owner"
    assert payload["provider"] == EMAIL_PROVIDER


def test_otp_verify_rejects_bad_code(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "777888")
    headers = _auth_headers(raw_client, "user-otp-badcode")
    raw_client.post(
        "/auth/otp/request",
        json={"email": "badcode@example.com"},
        headers=headers,
    )
    res = raw_client.post(
        "/auth/otp/verify",
        json={"email": "badcode@example.com", "code": "000000"},
        headers=headers,
    )
    assert res.status_code == 400


def test_otp_verify_requires_bearer(raw_client: TestClient) -> None:
    res = raw_client.post(
        "/auth/otp/verify",
        json={"email": "x@example.com", "code": "123456"},
    )
    assert res.status_code == 401


def test_otp_rate_limit_by_email(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "otp_rate_limit_per_email", 2)
    otp_service.reset_otp_rate_limiter()
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "999000")

    assert (
        raw_client.post(
            "/auth/otp/request",
            json={"email": "ratelimit@example.com"},
        ).status_code
        == 200
    )
    assert (
        raw_client.post(
            "/auth/otp/request",
            json={"email": "ratelimit@example.com"},
        ).status_code
        == 200
    )
    limited = raw_client.post(
        "/auth/otp/request",
        json={"email": "ratelimit@example.com"},
    )
    assert limited.status_code == 429
    otp_service.reset_otp_rate_limiter()
