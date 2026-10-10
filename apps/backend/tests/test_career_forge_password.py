"""CAR-129 — Career Forge account: password at signup, magic link after."""

from __future__ import annotations

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from urllib.parse import parse_qs, urlparse

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.config import settings
from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services.borderless_profile import ProfileRead, set_borderless_profile_client
from career_forge.services.borderless_signin import BorderlessIdentity, set_borderless_signin_client

_JWT_SECRET = "test-jwt-secret-car-23-long-enough-32b"
_PASSWORD = "career-forge-secret"


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


class _Mailbox:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self.fail = False

    def send_account_link(
        self,
        *,
        to_email: str,
        url: str,
        kind: str,
        hours: int,
        locale: str | None = None,
    ) -> None:
        if self.fail:
            raise RuntimeError("smtp down")
        self.sent.append((kind, to_email, url))


def _password_mode(monkeypatch: pytest.MonkeyPatch) -> _Mailbox:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    box = _Mailbox()
    monkeypatch.setattr(
        "career_forge.services.career_forge_password.get_mailer",
        lambda: box,
    )
    return box


def _token(url: str) -> str:
    return parse_qs(urlparse(url).query)["token"][0]


def _signup(
    raw_client: TestClient,
    box: _Mailbox,
    email: str,
    *,
    name: str = "Ada Lovelace",
    password: str = _PASSWORD,
) -> str:
    created = raw_client.post(
        "/auth/account/signup",
        json={"name": name, "email": email, "password": password},
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body["email"] == email
    assert "access_token" not in body
    kind, to_email, url = box.sent[-1]
    assert kind == "confirm"
    assert to_email == email
    assert "/account/confirm?token=" in url
    return url


def _confirm(raw_client: TestClient, url: str) -> dict:
    opened = raw_client.post("/auth/account/confirm", json={"token": _token(url)})
    assert opened.status_code == 200, opened.text
    return opened.json()


def test_signup_stores_a_pending_account_and_does_not_open_a_session(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-first@example.com"

    url = _signup(raw_client, box, email)
    everyday = raw_client.post(
        "/auth/otp/verify",
        json={"email": email, "code": "424242", "external_id": "user-everyday"},
    )
    assert everyday.status_code == 410

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.display_name == "Ada Lovelace"
        assert user.password_hash
        assert _PASSWORD not in user.password_hash
        assert user.email_confirmed_at is None
        assert user.membership_label == "external"
        assert user.membership_entitled is False
        assert user.borderless_user_id is None

    blocked = raw_client.post(
        "/diagnosis/interview/start",
        json={
            "user_id": "user-pending",
            "goal_id": "rag-engineer",
            "motivation": "I want to build production RAG systems with evals.",
            "years_xp": "0-1",
        },
    )
    assert blocked.status_code == 401
    assert url


def test_confirmation_opens_the_session_and_later_access_uses_the_password(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-later@example.com"
    url = _signup(raw_client, box, email)
    opened = _confirm(raw_client, url)
    assert opened["provider"] == EMAIL_PROVIDER
    claims = jwt.decode(opened["access_token"], _JWT_SECRET, algorithms=["HS256"])
    assert claims["provider"] == EMAIL_PROVIDER

    again = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": _PASSWORD},
    )
    assert again.status_code == 200, again.text
    assert again.json()["external_id"] == opened["external_id"]

    wrong = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "borderless-password"},
    )
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Invalid email or password"

    missing = raw_client.post(
        "/auth/account/signin",
        json={"email": "nobody-cf@example.com", "password": _PASSWORD},
    )
    assert missing.status_code == 401
    assert missing.json()["detail"] == "Invalid email or password"

    used = raw_client.post("/auth/account/confirm", json={"token": _token(url)})
    assert used.status_code == 400
    assert used.json()["detail"] == "This link has expired"


def test_sign_in_before_confirmation_stays_closed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-early@example.com"
    _signup(raw_client, box, email)

    early = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": _PASSWORD},
    )
    assert early.status_code == 403
    assert early.json()["detail"] == "Email is not confirmed"

    wrong = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "not-the-password"},
    )
    assert wrong.status_code == 401
    assert wrong.json()["detail"] == "Invalid email or password"


def test_repeating_signup_replaces_the_pending_account(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-repeat@example.com"
    first = _signup(raw_client, box, email, name="Ada Lovelace")
    second = _signup(
        raw_client,
        box,
        email,
        name="Grace Hopper",
        password="replacement-secret",
    )

    stale = raw_client.post("/auth/account/confirm", json={"token": _token(first)})
    assert stale.status_code == 400

    opened = _confirm(raw_client, second)
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.display_name == "Grace Hopper"
        assert user.external_id == opened["external_id"]

    old = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": _PASSWORD},
    )
    assert old.status_code == 401
    new = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "replacement-secret"},
    )
    assert new.status_code == 200


def test_resend_keeps_the_pending_name_and_password(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-resend@example.com"
    first = _signup(raw_client, box, email)
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        stored = user.password_hash

    resent = raw_client.post("/auth/account/resend", json={"email": email})
    assert resent.status_code == 200, resent.text
    assert resent.json()["email"] == email
    kind, to_email, second = box.sent[-1]
    assert kind == "confirm"
    assert to_email == email
    assert second != first

    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.password_hash == stored
        assert user.display_name == "Ada Lovelace"
        assert user.email_confirmed_at is None

    assert raw_client.post("/auth/account/confirm", json={"token": _token(first)}).status_code == 400
    opened = _confirm(raw_client, second)
    assert opened["provider"] == EMAIL_PROVIDER


def test_an_existing_account_is_refused_without_naming_the_door(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-exists@example.com"
    _confirm(raw_client, _signup(raw_client, box, email))
    before = len(box.sent)

    refused = raw_client.post(
        "/auth/account/signup",
        json={"name": "Ada Lovelace", "email": email, "password": "another-secret"},
    )
    assert refused.status_code == 409
    assert refused.json()["detail"] == "This email already has an account"
    assert len(box.sent) == before

    linked = "cf-linked@example.com"
    with SessionLocal() as session:
        user = ensure_user(session, "user-already-linked")
        user.email = linked
        user.borderless_user_id = "borderless-already-129"
        user.borderless_access_token = "sealed-already"
        session.commit()

    also = raw_client.post(
        "/auth/account/signup",
        json={"name": "Ada Lovelace", "email": linked, "password": _PASSWORD},
    )
    assert also.status_code == 409
    assert also.json()["detail"] == "This email already has an account"
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == linked))
        assert user is not None
        assert user.password_hash is None
        assert user.borderless_user_id == "borderless-already-129"


def test_forgot_password_mails_only_a_confirmed_career_forge_password(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    pending = "cf-forgot-pending@example.com"
    _signup(raw_client, box, pending)
    sent_after_signup = len(box.sent)

    quiet = raw_client.post("/auth/account/forgot", json={"email": pending})
    assert quiet.status_code == 200
    assert quiet.json() == {"ok": True}
    assert len(box.sent) == sent_after_signup

    unknown = raw_client.post(
        "/auth/account/forgot",
        json={"email": "nobody-forgot@example.com"},
    )
    assert unknown.status_code == 200
    assert unknown.json() == {"ok": True}
    assert len(box.sent) == sent_after_signup

    email = "cf-forgot@example.com"
    _confirm(raw_client, _signup(raw_client, box, email))
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        user.borderless_user_id = "borderless-reset-129"
        user.borderless_access_token = "sealed-borderless-token"
        session.commit()
        previous_hash = user.password_hash

    asked = raw_client.post("/auth/account/forgot", json={"email": email})
    assert asked.status_code == 200
    assert asked.json() == {"ok": True}
    kind, to_email, url = box.sent[-1]
    assert kind == "reset"
    assert to_email == email
    assert "/account/reset?token=" in url

    replaced = raw_client.post(
        "/auth/account/reset",
        json={"token": _token(url), "password": "replacement-secret"},
    )
    assert replaced.status_code == 200, replaced.text
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.password_hash != previous_hash
        assert user.borderless_user_id == "borderless-reset-129"
        assert user.borderless_access_token == "sealed-borderless-token"
        assert user.external_id == replaced.json()["external_id"]

    old = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": _PASSWORD},
    )
    assert old.status_code == 401
    new = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": "replacement-secret"},
    )
    assert new.status_code == 200
    again = raw_client.post(
        "/auth/account/reset",
        json={"token": _token(url), "password": "replacement-secret"},
    )
    assert again.status_code == 400


def test_borderless_sign_in_claims_a_pending_account_and_keeps_a_confirmed_password(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    pending_email = "cf-claim@example.com"
    pending_url = _signup(raw_client, box, pending_email, name="Ada Lovelace")
    set_borderless_signin_client(
        _FakeSignin(
            BorderlessIdentity(
                user_id="borderless-claim-129",
                name="Other Name",
                email_verified=True,
                access_token="borderless-access-claim",
            )
        )
    )
    claimed = raw_client.post(
        "/auth/signin",
        json={"email": pending_email, "password": "borderless-password"},
    )
    assert claimed.status_code == 200, claimed.text
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == pending_email))
        assert user is not None
        assert user.display_name == "Ada Lovelace"
        assert user.password_hash is None
        assert user.email_confirmed_at is not None
        assert user.external_id == claimed.json()["external_id"]
    assert (
        raw_client.post("/auth/account/confirm", json={"token": _token(pending_url)}).status_code
        == 400
    )
    closed = raw_client.post(
        "/auth/account/signin",
        json={"email": pending_email, "password": _PASSWORD},
    )
    assert closed.status_code == 401

    email = "cf-same@example.com"
    opened = _confirm(raw_client, _signup(raw_client, box, email, name="Existing Name"))
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
        started = session.scalar(
            select(func.count()).select_from(ForgeArtifact).where(ForgeArtifact.user_id == user.id)
        )

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
        assert user.display_name == "Existing Name"
        assert user.membership_label == "base"
        assert user.password_hash
        still = session.scalar(
            select(func.count()).select_from(ForgeArtifact).where(ForgeArtifact.user_id == user.id)
        )
        assert still == started == 1
    kept = raw_client.post(
        "/auth/account/signin",
        json={"email": email, "password": _PASSWORD},
    )
    assert kept.status_code == 200


def test_short_password_blank_name_and_a_failed_send_leave_the_rules_intact(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    short = raw_client.post(
        "/auth/account/signup",
        json={"name": "Ada Lovelace", "email": "cf-short@example.com", "password": "short"},
    )
    assert short.status_code == 400
    blank = raw_client.post(
        "/auth/account/signup",
        json={"name": "   ", "email": "cf-blank@example.com", "password": _PASSWORD},
    )
    assert blank.status_code == 422

    box.fail = True
    failed = raw_client.post(
        "/auth/account/signup",
        json={"name": "Ada Lovelace", "email": "cf-mail@example.com", "password": _PASSWORD},
    )
    assert failed.status_code == 503
    assert failed.json()["detail"] == "Could not send the email"
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == "cf-mail@example.com"))
        assert user is not None
        assert user.email_confirmed_at is None
        assert user.password_hash

    box.fail = False
    resent = raw_client.post("/auth/account/resend", json={"email": "cf-mail@example.com"})
    assert resent.status_code == 200, resent.text
    _confirm(raw_client, box.sent[-1][2])


def test_account_routes_are_gone_outside_password_mode(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "email_otp")
    refused = raw_client.post(
        "/auth/account/signup",
        json={"name": "Ada Lovelace", "email": "cf-otp-mode@example.com", "password": _PASSWORD},
    )
    assert refused.status_code == 410


def test_a_failed_reset_email_still_answers_the_same_sentence(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-forgot-down@example.com"
    _confirm(raw_client, _signup(raw_client, box, email))
    box.fail = True
    asked = raw_client.post("/auth/account/forgot", json={"email": email})
    assert asked.status_code == 200
    assert asked.json() == {"ok": True}

    box.fail = False
    again = raw_client.post("/auth/account/forgot", json={"email": email})
    assert again.status_code == 200
    assert again.json() == {"ok": True}
    kind, to_email, _url = box.sent[-1]
    assert kind == "reset"
    assert to_email == email


def test_name_length_is_measured_after_trim(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    box = _password_mode(monkeypatch)
    email = "cf-name-trim@example.com"
    created = raw_client.post(
        "/auth/account/signup",
        json={"name": " " + ("A" * 120), "email": email, "password": _PASSWORD},
    )
    assert created.status_code == 200, created.text
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.email == email))
        assert user is not None
        assert user.display_name == "A" * 120

    too_long = raw_client.post(
        "/auth/account/signup",
        json={
            "name": " " + ("B" * 121),
            "email": "cf-name-long@example.com",
            "password": _PASSWORD,
        },
    )
    assert too_long.status_code == 422
    assert box.sent


def test_an_expired_confirmation_link_is_refused(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from datetime import timedelta

    box = _password_mode(monkeypatch)
    monkeypatch.setattr(
        "career_forge.services.career_forge_password.LINK_TTL",
        timedelta(seconds=-1),
    )
    url = _signup(raw_client, box, "cf-expired@example.com")
    expired = raw_client.post("/auth/account/confirm", json={"token": _token(url)})
    assert expired.status_code == 400
    assert expired.json()["detail"] == "This link has expired"
