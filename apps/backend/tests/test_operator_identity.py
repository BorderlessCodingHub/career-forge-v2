"""Operator identity — OTP, operators table, session cookie (CAR-75)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.operator import Operator
from career_forge.db.session import SessionLocal
from career_forge.services import operator_otp as operator_otp_service


def _learner_email_headers(raw_client: TestClient, external_id: str = "learner-op-test") -> dict[str, str]:
    raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def _operator_otp_flow(
    raw_client: TestClient,
    *,
    email: str = "ops@borderless.com",
    code: str = "424242",
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: code)
    req = raw_client.post("/operator/auth/otp/request", json={"email": email})
    assert req.status_code == 200, req.text
    verify = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": code},
    )
    assert verify.status_code == 200, verify.text


@pytest.fixture
def operator_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        settings,
        "operator_allowlist",
        "ops@borderless.com:both,editor@borderless.com:editor,access@borderless.com:access",
    )


def test_operator_otp_request_rejects_non_allowlisted(
    raw_client: TestClient,
    operator_allowlist: None,
) -> None:
    res = raw_client.post("/operator/auth/otp/request", json={"email": "stranger@example.com"})
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "operator_not_allowlisted"


def test_operator_otp_request_upserts_operator_row(
    raw_client: TestClient,
    operator_allowlist: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "131313")
    res = raw_client.post("/operator/auth/otp/request", json={"email": "access@borderless.com"})
    assert res.status_code == 200, res.text

    with SessionLocal() as session:
        row = session.scalar(
            select(Operator).where(Operator.email == "access@borderless.com"),
        )
        assert row is not None
        assert row.desk_roles == "access"


def test_operator_session_cookie_and_me(
    raw_client: TestClient,
    operator_allowlist: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "242424")
    raw_client.post("/operator/auth/otp/request", json={"email": "ops@borderless.com"})
    verify = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": "ops@borderless.com", "code": "242424"},
    )
    assert verify.status_code == 200, verify.text
    assert verify.json()["provider"] == "operator"
    assert verify.json()["desk_roles"] == "both"

    cookie_name = settings.operator_cookie_name
    assert cookie_name in raw_client.cookies

    me = raw_client.get("/operator/me")
    assert me.status_code == 200, me.text
    body = me.json()
    assert body["email"] == "ops@borderless.com"
    assert body["desk_roles"] == "both"
    assert body["desks"] == ["access", "content"]


def test_learner_bearer_rejected_on_operator_api(
    raw_client: TestClient,
    operator_allowlist: None,
) -> None:
    headers = _learner_email_headers(raw_client)
    res = raw_client.get("/operator/me", headers=headers)
    assert res.status_code == 403
    assert res.json()["detail"]["code"] == "learner_session_forbidden"


def test_operator_routes_reject_missing_session(
    raw_client: TestClient,
    operator_allowlist: None,
) -> None:
    res = raw_client.get("/operator/me")
    assert res.status_code == 401


def test_same_email_can_be_learner_and_operator(
    raw_client: TestClient,
    operator_allowlist: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    email = "ops@borderless.com"
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "353535")

    raw_client.post("/operator/auth/otp/request", json={"email": email})
    raw_client.post("/operator/auth/otp/verify", json={"email": email, "code": "353535"})
    op_me = raw_client.get("/operator/me")
    assert op_me.status_code == 200

    with SessionLocal() as session:
        learner_count = session.scalar(
            select(Operator).where(Operator.email == email),
        )
        assert learner_count is not None

    learner_headers = _learner_email_headers(raw_client, "shared-email-user")
    learner_otp = raw_client.post(
        "/auth/otp/request",
        json={"email": email},
    )
    assert learner_otp.status_code == 200


def test_operator_sign_out_clears_session(
    raw_client: TestClient,
    operator_allowlist: None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "464646")
    raw_client.post("/operator/auth/otp/request", json={"email": "ops@borderless.com"})
    raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": "ops@borderless.com", "code": "464646"},
    )
    assert raw_client.get("/operator/me").status_code == 200

    sign_out = raw_client.post("/operator/auth/sign-out")
    assert sign_out.status_code == 204

    assert raw_client.get("/operator/me").status_code == 401
