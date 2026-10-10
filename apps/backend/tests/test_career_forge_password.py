"""CAR-129 — Career Forge password, distinct from the Borderless password."""

from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.config import settings
from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services.borderless_profile import ProfileRead, set_borderless_profile_client
from career_forge.services.borderless_signin import BorderlessIdentity, set_borderless_signin_client
_JWT_SECRET = "test-jwt-secret-car-23-long-enough-32b"


class _RecordingProfile:
    def __init__(self, label: str) -> None:
        self.label = label
        self.calls = 0

    def read(self, access_token: str) -> ProfileRead:
        self.calls += 1
        return ProfileRead(kind="label", label=self.label)


class _FakeSignin:
    def __init__(self, identity: BorderlessIdentity) -> None:
        self.identity = identity

    def authenticate(self, email: str, password: str) -> BorderlessIdentity:
        return self.identity


def _password_mode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    monkeypatch.setattr(
        "career_forge.services.career_forge_password._generate_code",
        lambda: "424242",
    )


def _set_password(raw_client: TestClient, email: str, password: str) -> dict:
    requested = raw_client.post("/auth/account/code", json={"email": email})
    assert requested.status_code == 200, requested.text
    opened = raw_client.post(
        "/auth/account/password",
        json={"email": email, "code": "424242", "password": password},
    )
    assert opened.status_code == 200, opened.text
    return opened.json()


def test_first_access_sets_a_password_and_learner_otp_stays_closed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    email = "cf-first@example.com"
    password = "career-forge-secret"

    requested = raw_client.post("/auth/account/code", json={"email": email})
    assert requested.status_code == 200, requested.text

    everyday = raw_client.post(
        "/auth/otp/verify",
        json={"email": email, "code": "424242", "external_id": "user-everyday"},
    )
    assert everyday.status_code == 410

    opened = raw_client.post(
        "/auth/account/password",
        json={"email": email, "code": "424242", "password": password},
    )
    assert opened.status_code == 200, opened.text
    body = opened.json()
    assert body["provider"] == EMAIL_PROVIDER
    assert "password" not in body
    claims = jwt.decode(body["access_token"], _JWT_SECRET, algorithms=["HS256"])
    assert claims["provider"] == EMAIL_PROVIDER

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.password_hash
        assert password not in user.password_hash
        assert user.membership_label == "external"
        assert user.membership_entitled is False
        assert user.borderless_user_id is None
        assert user.external_id == body["external_id"]


def test_later_access_uses_the_stored_password(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    email = "cf-later@example.com"
    password = "career-forge-secret"
    first = _set_password(raw_client, email, password)

    again = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": password},
    )
    assert again.status_code == 200, again.text
    assert again.json()["external_id"] == first["external_id"]

    wrong = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "borderless-password"},
    )
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Invalid email or password"

    missing = raw_client.post(
        "/auth/account/signin",
        json={"email": "nobody-cf@example.com", "password": password},
    )
    assert missing.status_code == 401
    assert missing.json()["detail"] == "Invalid email or password"


def test_inbox_replaces_the_career_forge_password_only(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    email = "cf-reset@example.com"
    _set_password(raw_client, email, "career-forge-secret")
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.borderless_user_id = "borderless-reset-129"
        user.borderless_access_token = "sealed-borderless-token"
        session.commit()
        previous_hash = user.password_hash

    replaced = _set_password(raw_client, email, "replacement-secret")
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.password_hash != previous_hash
        assert user.borderless_user_id == "borderless-reset-129"
        assert user.borderless_access_token == "sealed-borderless-token"
        assert user.external_id == replaced["external_id"]

    old = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "career-forge-secret"},
    )
    assert old.status_code == 401
    new = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "replacement-secret"},
    )
    assert new.status_code == 200


def test_borderless_sign_in_is_the_same_account_and_reads_the_profile(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    email = "cf-same@example.com"
    password = "career-forge-secret"
    opened = _set_password(raw_client, email, password)
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        artifact = ForgeArtifact(
            user_id=user.id,
            graph_run_id="run-cf-129",
            title="Started forge",
            snapshot=[],
            is_active=True,
        )
        session.add(artifact)
        session.commit()
        started = session.scalar(select(func.count()).select_from(ForgeArtifact).where(ForgeArtifact.user_id == user.id))

    set_borderless_signin_client(
        _FakeSignin(
            BorderlessIdentity(
                user_id="borderless-same-129",
                name="Same Learner",
                email_verified=True,
                access_token="borderless-access-same",
            )
        )
    )
    profile = _RecordingProfile("base")
    set_borderless_profile_client(profile)
    borderless = raw_client.post(
        "/auth/signin",
        json={"email": email, "password": "borderless-password"},
    )
    assert borderless.status_code == 200, borderless.text
    assert borderless.json()["external_id"] == opened["external_id"]
    assert profile.calls == 1

    diagnosis = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": opened["external_id"],
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
        headers={"Authorization": f"Bearer {borderless.json()['access_token']}"},
    )
    assert diagnosis.status_code == 200, diagnosis.text

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.membership_label == "base"
        assert user.password_hash
        still = session.scalar(
            select(func.count()).select_from(ForgeArtifact).where(ForgeArtifact.user_id == user.id)
        )
        assert still == started == 1


def test_linked_account_can_add_a_career_forge_password_later(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    email = "cf-later-link@example.com"
    external_id = "user-already-linked"
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.email = email
        user.borderless_user_id = "borderless-already-129"
        user.borderless_access_token = "sealed-already"
        user.membership_label = "external"
        user.membership_entitled = False
        session.commit()

    opened = _set_password(raw_client, email, "added-later-secret")
    assert opened["external_id"] == external_id
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.borderless_user_id == "borderless-already-129"
        assert user.borderless_access_token == "sealed-already"
        assert user.membership_label == "external"


def test_short_password_is_refused(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _password_mode(monkeypatch)
    raw_client.post("/auth/account/code", json={"email": "cf-short@example.com"})
    refused = raw_client.post(
        "/auth/account/password",
        json={"email": "cf-short@example.com", "code": "424242", "password": "short"},
    )
    assert refused.status_code == 400


def test_account_password_is_gone_outside_password_mode(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "email_otp")
    refused = raw_client.post("/auth/account/code", json={"email": "cf-otp-mode@example.com"})
    assert refused.status_code == 410
