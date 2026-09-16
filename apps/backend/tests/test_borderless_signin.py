"""CAR-104 — Borderless password credential check; Career Forge stays IdP."""

from __future__ import annotations

import json
import logging

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services.borderless_signin import (
    BorderlessIdentity,
    BorderlessSigninClient,
    InvalidBorderlessCredentialsError,
    SigninHttpResponse,
    reset_signin_rate_limiter,
    set_borderless_signin_client,
)


class _FakeSigninClient:
    def __init__(
        self,
        identity: BorderlessIdentity | None = None,
        error: Exception | None = None,
    ) -> None:
        self.identity = identity
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def authenticate(self, email: str, password: str) -> BorderlessIdentity:
        self.calls.append((email, password))
        if self.error is not None:
            raise self.error
        assert self.identity is not None
        return self.identity


@pytest.fixture(autouse=True)
def _reset_signin_state() -> None:
    set_borderless_signin_client(None)
    reset_signin_rate_limiter()
    yield
    set_borderless_signin_client(None)
    reset_signin_rate_limiter()


def _identity(
    *,
    user_id: str = "borderless-user-104",
    email_verified: bool = True,
    name: str = "Ada Lovelace",
) -> BorderlessIdentity:
    return BorderlessIdentity(
        user_id=user_id,
        email_verified=email_verified,
        name=name,
    )


def test_signin_mints_cf_jwt_discards_borderless_token_without_membership_lookup(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    email = "signin-happy@example.com"
    password = "never-log-this-password"
    upstream_token = "never-return-this-borderless-token"
    seen_payloads: list[dict[str, str]] = []
    membership_lookups: list[str] = []

    def fetch(
        url: str,
        payload: bytes,
        timeout: float,
    ) -> SigninHttpResponse:
        assert url == "https://signin.example/auth/signin"
        assert timeout == 2.5
        seen_payloads.append(json.loads(payload))
        return SigninHttpResponse(
            status=200,
            headers={},
            body=json.dumps(
                {
                    "data": {
                        "user": {
                            "id": "borderless-happy-104",
                            "emailVerified": True,
                            "name": "Ada Lovelace",
                            "username": "ignored",
                            "careerStage": "ignored",
                        },
                        "token": {"accessToken": upstream_token},
                    }
                }
            ),
        )

    set_borderless_signin_client(
        BorderlessSigninClient(
            url="https://signin.example/auth/signin",
            timeout=2.5,
            fetch=fetch,
        )
    )

    class _SpyMembership:
        def lookup(self, lookup_email: str):
            membership_lookups.append(lookup_email)
            raise AssertionError("password sign-in must not call membership HTTP")

    monkeypatch.setattr(
        "career_forge.services.membership.get_membership_client",
        lambda: _SpyMembership(),
    )

    with caplog.at_level(logging.DEBUG):
        response = raw_client.post(
            "/auth/signin",
            json={"email": f"  {email.upper()} ", "password": password},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["provider"] == "email"
    assert body["external_id"].startswith("user-")
    assert body["access_token"] != upstream_token
    assert upstream_token not in response.text
    assert upstream_token not in caplog.text
    assert password not in caplog.text
    assert seen_payloads == [{"email": email, "password": password}]
    assert membership_lookups == []

    claims = jwt.decode(body["access_token"], settings.jwt_secret, algorithms=["HS256"])
    assert claims["sub"] == body["external_id"]
    assert claims["provider"] == "email"

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.borderless_user_id == "borderless-happy-104"
        assert user.display_name == "Ada Lovelace"
        assert user.membership_label == "external"
        assert user.membership_entitled is False


def test_signin_refuses_unverified_borderless_email(raw_client: TestClient) -> None:
    email = "signin-unverified@example.com"
    fake = _FakeSigninClient(_identity(email_verified=False))
    set_borderless_signin_client(fake)

    response = raw_client.post(
        "/auth/signin",
        json={"email": email, "password": "correct-password"},
    )

    assert response.status_code == 403
    assert "verified" in response.json()["detail"].lower()
    with SessionLocal() as session:
        assert session.scalar(select(User).where(User.email == email)) is None


def test_signin_maps_borderless_401_to_generic_copy(raw_client: TestClient) -> None:
    fake = _FakeSigninClient(error=InvalidBorderlessCredentialsError())
    set_borderless_signin_client(fake)

    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-invalid@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_borderless_client_maps_http_401_without_retry(
    raw_client: TestClient,
) -> None:
    attempts = 0

    def fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
        nonlocal attempts
        attempts += 1
        return SigninHttpResponse(
            status=401,
            headers={},
            body="sensitive upstream response",
        )

    set_borderless_signin_client(
        BorderlessSigninClient(
            url="https://signin.example/auth/signin",
            timeout=2.5,
            fetch=fetch,
        )
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-http-401@example.com", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
    assert attempts == 1
    assert "sensitive upstream response" not in response.text


def test_signin_reuses_existing_email_external_id(raw_client: TestClient) -> None:
    email = "signin-reuse@example.com"
    with SessionLocal() as session:
        user = ensure_user(session, "user-existing-104", display_name="Existing Name")
        user.email = email
        user.borderless_user_id = "borderless-existing-104"
        session.commit()

    set_borderless_signin_client(
        _FakeSigninClient(_identity(user_id="borderless-existing-104", name="New Name"))
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": email, "password": "correct-password"},
    )

    assert response.status_code == 200
    assert response.json()["external_id"] == "user-existing-104"
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.display_name == "Existing Name"


def test_signin_refuses_borderless_user_id_mismatch(raw_client: TestClient) -> None:
    email = "signin-mismatch@example.com"
    with SessionLocal() as session:
        user = ensure_user(session, "user-mismatch-104")
        user.email = email
        user.borderless_user_id = "borderless-original-104"
        session.commit()

    set_borderless_signin_client(
        _FakeSigninClient(_identity(user_id="borderless-attacker-104"))
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": email, "password": "correct-password"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Borderless account identity mismatch"
    assert "access_token" not in response.text


def test_signin_rate_limits_before_second_borderless_call(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "otp_rate_limit_per_email", 1)
    monkeypatch.setattr(settings, "otp_rate_limit_per_ip", 20)
    fake = _FakeSigninClient(error=InvalidBorderlessCredentialsError())
    set_borderless_signin_client(fake)
    payload = {"email": "signin-limited@example.com", "password": "wrong"}

    assert raw_client.post("/auth/signin", json=payload).status_code == 401
    response = raw_client.post("/auth/signin", json=payload)

    assert response.status_code == 429
    assert len(fake.calls) == 1


def test_signin_rate_limits_by_ip_before_borderless_call(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "otp_rate_limit_per_email", 20)
    monkeypatch.setattr(settings, "otp_rate_limit_per_ip", 1)
    fake = _FakeSigninClient(error=InvalidBorderlessCredentialsError())
    set_borderless_signin_client(fake)

    first = raw_client.post(
        "/auth/signin",
        json={"email": "signin-ip-first@example.com", "password": "wrong"},
    )
    second = raw_client.post(
        "/auth/signin",
        json={"email": "signin-ip-second@example.com", "password": "wrong"},
    )

    assert first.status_code == 401
    assert second.status_code == 429
    assert len(fake.calls) == 1


def test_borderless_client_retries_timeout_once_then_returns_503(
    raw_client: TestClient,
) -> None:
    attempts = 0

    def fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
        nonlocal attempts
        attempts += 1
        raise TimeoutError("upstream timed out")

    set_borderless_signin_client(
        BorderlessSigninClient(
            url="https://signin.example/auth/signin",
            timeout=2.5,
            fetch=fetch,
        )
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-timeout@example.com", "password": "secret"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Borderless signin temporarily unavailable"
    assert attempts == 2


def test_borderless_client_retries_5xx_once_then_succeeds(
    raw_client: TestClient,
) -> None:
    attempts = 0

    def fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return SigninHttpResponse(status=502, headers={}, body="upstream detail")
        return SigninHttpResponse(
            status=200,
            headers={},
            body=json.dumps(
                {
                    "data": {
                        "user": {
                            "id": "borderless-retry-104",
                            "emailVerified": True,
                            "name": "Retry User",
                        }
                    }
                }
            ),
        )

    set_borderless_signin_client(
        BorderlessSigninClient(
            url="https://signin.example/auth/signin",
            timeout=2.5,
            fetch=fetch,
        )
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-retry@example.com", "password": "secret"},
    )

    assert response.status_code == 200
    assert attempts == 2
    assert "upstream detail" not in response.text


def test_signin_passes_through_borderless_429_retry_after(
    raw_client: TestClient,
) -> None:
    def fetch(url: str, payload: bytes, timeout: float) -> SigninHttpResponse:
        return SigninHttpResponse(
            status=429,
            headers={"Retry-After": "45"},
            body="sensitive upstream response",
        )

    set_borderless_signin_client(
        BorderlessSigninClient(
            url="https://signin.example/auth/signin",
            timeout=2.5,
            fetch=fetch,
        )
    )
    response = raw_client.post(
        "/auth/signin",
        json={"email": "signin-upstream-limit@example.com", "password": "secret"},
    )

    assert response.status_code == 429
    assert response.headers["retry-after"] == "45"
    assert "sensitive upstream response" not in response.text
