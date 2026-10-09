"""CAR-128 — password mode reads membership from the Borderless profile."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.config import assert_borderless_token_key, settings
from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.services.borderless_profile import (
    BorderlessProfileClient,
    borderless_profile_url,
    set_borderless_profile_client,
)
from career_forge.services.borderless_signin import (
    BorderlessSigninClient,
    SigninHttpResponse,
    set_borderless_signin_client,
)
from tests.test_entitlement import _diagnosis_payload


def _signin_client(
    email: str,
    password: str,
    *,
    user_id: str,
    name: str,
    access_token: str | None,
):
    token_body: dict = {}
    if access_token is not None:
        token_body = {"token": {"accessToken": access_token}}

    def fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
        assert json.loads(payload)["email"] == email
        assert json.loads(payload)["password"] == password
        assert timeout == 2.5
        return SigninHttpResponse(
            status=200,
            headers={},
            body=json.dumps(
                {
                    "data": {
                        "user": {
                            "id": user_id,
                            "emailVerified": True,
                            "name": name,
                        },
                        **token_body,
                    }
                }
            ),
        )

    return BorderlessSigninClient(
        url="https://signin.example/auth/signin",
        timeout=2.5,
        fetch=fetch,
    )


class _ProfileScript:
    def __init__(self, status: int, membership: str | None) -> None:
        self.status = status
        self.membership = membership
        self.calls = 0

    def fetch(self, url: str, access_token: str, timeout: float) -> tuple[int, str]:
        assert url == "https://api.borderlesscoding.com/api/users/profile"
        assert access_token
        assert timeout == 5.0
        self.calls += 1
        if self.membership is None:
            body: dict = {"data": {"user": {}}}
        else:
            body = {"data": {"user": {"membership": self.membership}}}
        return self.status, json.dumps(body)


def _use_profile(script: _ProfileScript) -> None:
    set_borderless_profile_client(
        BorderlessProfileClient(
            url="https://api.borderlesscoding.com/api/users/profile",
            timeout=5.0,
            fetch=script.fetch,
        )
    )


def _post_signin(raw_client: TestClient, email: str, password: str) -> dict:
    response = raw_client.post(
        "/auth/signin",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()


def test_profile_url_uses_the_signin_origin() -> None:
    assert (
        borderless_profile_url("https://api.borderlesscoding.com/api/auth/signin")
        == "https://api.borderlesscoding.com/api/users/profile"
    )


def test_signin_records_base_membership_from_the_borderless_profile(
    raw_client: TestClient,
) -> None:
    email = "profile-base@example.com"
    password = "borderless-password"
    upstream_token = "borderless-access-token-base"
    script = _ProfileScript(200, "BASE")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-base-128",
            name="Grace Hopper",
            access_token=upstream_token,
        )
    )
    _use_profile(script)

    body = _post_signin(raw_client, email, password)

    assert body["access_token"] != upstream_token
    assert upstream_token not in json.dumps(body)
    claims = jwt.decode(body["access_token"], settings.jwt_secret, algorithms=["HS256"])
    assert claims["sub"] == body["external_id"]
    assert script.calls == 1

    me = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.status_code == 200
    assert me.json()["membership_label"] == "base"
    assert me.json()["membership_entitled"] is True

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.borderless_access_token
        assert upstream_token not in user.borderless_access_token


def test_signin_missing_membership_field_is_external(raw_client: TestClient) -> None:
    email = "profile-missing@example.com"
    script = _ProfileScript(200, None)
    set_borderless_signin_client(
        _signin_client(
            email,
            "pw",
            user_id="borderless-missing-128",
            name="Missing Field",
            access_token="borderless-access-token-missing",
        )
    )
    _use_profile(script)

    body = _post_signin(raw_client, email, "pw")
    me = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.json()["membership_label"] == "external"
    assert me.json()["membership_entitled"] is False


def test_signin_records_free_membership_as_external(raw_client: TestClient) -> None:
    email = "profile-free@example.com"
    script = _ProfileScript(200, "FREE")
    set_borderless_signin_client(
        _signin_client(
            email,
            "pw",
            user_id="borderless-free-128",
            name="Free Learner",
            access_token="borderless-access-token-free",
        )
    )
    _use_profile(script)

    body = _post_signin(raw_client, email, "pw")
    me = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.json()["membership_label"] == "external"
    assert me.json()["membership_entitled"] is False


def test_signin_still_opens_when_the_profile_read_fails(raw_client: TestClient) -> None:
    email = "profile-down@example.com"
    script = _ProfileScript(503, "BASE")
    set_borderless_signin_client(
        _signin_client(
            email,
            "pw",
            user_id="borderless-down-128",
            name="Down Learner",
            access_token="borderless-access-token-down",
        )
    )
    _use_profile(script)

    body = _post_signin(raw_client, email, "pw")
    me = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.json()["membership_label"] == "external"
    assert me.json()["membership_entitled"] is False


def test_signin_without_access_token_keeps_the_previous_label(
    raw_client: TestClient,
) -> None:
    email = "profile-keep@example.com"
    password = "pw"
    first = _ProfileScript(200, "PSP")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-keep-128",
            name="Keep Learner",
            access_token="borderless-access-token-keep",
        )
    )
    _use_profile(first)
    _post_signin(raw_client, email, password)

    with SessionLocal() as session:
        stored = session.scalar(select(User).where(User.email == email))
        assert stored is not None
        sealed = stored.borderless_access_token

    second = _ProfileScript(200, "FREE")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-keep-128",
            name="Keep Learner",
            access_token=None,
        )
    )
    _use_profile(second)
    body = _post_signin(raw_client, email, password)

    assert second.calls == 0
    me = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert me.json()["membership_label"] == "psp"
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.borderless_access_token == sealed


def test_failed_profile_read_keeps_base_and_retries_after_five_minutes(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    email = "profile-retry@example.com"
    password = "pw"
    clock = {"now": datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)}
    monkeypatch.setattr(
        "career_forge.services.borderless_profile._now",
        lambda: clock["now"],
    )
    script = _ProfileScript(200, "BASE")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-retry-128",
            name="Retry Learner",
            access_token="borderless-access-token-retry",
        )
    )
    _use_profile(script)
    body = _post_signin(raw_client, email, password)
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    user_id = body["external_id"]

    script.status = 503
    calls_after_signin = script.calls
    first = raw_client.post("/forge/runs", json=_diagnosis_payload(user_id), headers=headers)
    assert first.status_code == 202, first.text
    assert script.calls == calls_after_signin + 1

    second = raw_client.post("/forge/runs", json=_diagnosis_payload(user_id), headers=headers)
    assert second.status_code == 202, second.text
    assert script.calls == calls_after_signin + 1

    clock["now"] = clock["now"] + timedelta(minutes=5)
    script.status = 200
    script.membership = "FREE"
    third = raw_client.post("/forge/runs", json=_diagnosis_payload(user_id), headers=headers)
    assert third.status_code == 402, third.text
    assert script.calls == calls_after_signin + 2
    me = raw_client.get("/me/profile", headers=headers)
    assert me.json()["membership_label"] == "external"


def test_unauthorized_profile_keeps_the_label_until_the_next_password_signin(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    email = "profile-latch@example.com"
    password = "pw"
    clock = {"now": datetime(2026, 10, 9, 12, 0, tzinfo=timezone.utc)}
    monkeypatch.setattr(
        "career_forge.services.borderless_profile._now",
        lambda: clock["now"],
    )
    script = _ProfileScript(200, "BASE")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-latch-128",
            name="Latch Learner",
            access_token="borderless-access-token-latch",
        )
    )
    _use_profile(script)
    body = _post_signin(raw_client, email, password)
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    user_id = body["external_id"]

    script.status = 401
    calls_after_signin = script.calls
    first = raw_client.post("/forge/runs", json=_diagnosis_payload(user_id), headers=headers)
    assert first.status_code == 202, first.text
    assert script.calls == calls_after_signin + 1

    clock["now"] = clock["now"] + timedelta(minutes=10)
    second = raw_client.post("/forge/runs", json=_diagnosis_payload(user_id), headers=headers)
    assert second.status_code == 202, second.text
    assert script.calls == calls_after_signin + 1

    script.status = 200
    script.membership = "PSP"
    _post_signin(raw_client, email, password)
    assert script.calls == calls_after_signin + 2
    me = raw_client.get("/me/profile", headers=headers)
    assert me.json()["membership_label"] == "psp"


def test_operator_override_includes_when_the_profile_says_free(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    email = "profile-desk@example.com"
    password = "pw"
    script = _ProfileScript(200, "FREE")
    set_borderless_signin_client(
        _signin_client(
            email,
            password,
            user_id="borderless-desk-128",
            name="Desk Learner",
            access_token="borderless-access-token-desk",
        )
    )
    _use_profile(script)
    body = _post_signin(raw_client, email, password)
    headers = {"Authorization": f"Bearer {body['access_token']}"}
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.operator_membership_label = "psp"
        session.commit()

    calls_before = script.calls
    started = raw_client.post(
        "/forge/runs",
        json=_diagnosis_payload(body["external_id"]),
        headers=headers,
    )
    assert started.status_code == 202, started.text
    assert script.calls == calls_before + 1
    me = raw_client.get("/me/profile", headers=headers)
    assert me.json()["membership_label"] == "external"
    assert me.json()["membership_entitled"] is False
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.operator_membership_label == "psp"


def test_password_mode_refuses_to_boot_without_a_token_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    monkeypatch.setattr(settings, "borderless_token_encryption_key", " ")
    with pytest.raises(RuntimeError, match="BORDERLESS_TOKEN_ENCRYPTION_KEY"):
        assert_borderless_token_key()
