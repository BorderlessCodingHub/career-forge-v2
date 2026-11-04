"""Learner product notes — POST /me/feedback and the access-desk queue (LABS01-170).

Seams: the learner submit route and the operator list/replied routes.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
import sentry_sdk
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select

from career_forge.config import settings
from career_forge.main import app
from career_forge.db.models.learner_feedback import LearnerFeedbackNote
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services import operator_otp as operator_otp_service
from career_forge.services.mailer import feedback_notice_letter


@pytest.fixture(autouse=True)
def _clear_notes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "feedback_notify_email", "")
    yield
    with SessionLocal() as session:
        session.execute(delete(LearnerFeedbackNote))
        session.commit()


def _learner(external_id: str, email: str | None) -> uuid.UUID:
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.email = email
        session.commit()
        return user.id


def _count_for(user_id: uuid.UUID) -> int:
    with SessionLocal() as session:
        return int(
            session.scalar(
                select(func.count())
                .select_from(LearnerFeedbackNote)
                .where(LearnerFeedbackNote.user_id == user_id)
            )
            or 0
        )


def _post(
    client: TestClient,
    external_id: str,
    *,
    message: str = "The forge timeline is the part I trust.",
    email: str = "spoofed@example.com",
    path: str = "/roadmap",
    cookie: str | None = "cf_locale=pt-BR",
) -> object:
    headers = {"Cookie": cookie} if cookie is not None else {}
    return client.post(
        "/me/feedback",
        params={"user_id": external_id},
        headers=headers,
        json={"message": message, "email": email, "path": path},
    )


def test_notice_letter_names_the_desk_and_carries_no_learner() -> None:
    subject, text = feedback_notice_letter()
    combined = f"{subject}\n{text}"
    assert "access desk" in combined.lower()
    assert "@" not in combined


def test_submit_stores_the_account_email_and_ignores_the_body(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    account_email = f"{external_id}@example.com"
    user_id = _learner(external_id, account_email)
    sent: list[str] = []

    class _Mailer:
        def send_feedback_notice(self, *, to_email: str) -> None:
            sent.append(to_email)

    monkeypatch.setattr(settings, "feedback_notify_email", "desk@example.com")
    monkeypatch.setattr(
        "career_forge.services.learner_feedback.get_mailer",
        lambda: _Mailer(),
    )
    captured: list[object] = []
    monkeypatch.setattr(
        sentry_sdk,
        "capture_message",
        lambda *args, **kwargs: captured.append(args),
    )
    monkeypatch.setattr(
        sentry_sdk,
        "capture_event",
        lambda *args, **kwargs: captured.append(args),
    )
    response = _post(
        client,
        external_id,
        path="/roadmap" + ("x" * 400),
    )
    assert response.status_code == 200, response.text
    assert response.json() == {"accepted": True}
    assert "forge timeline" not in response.text
    with SessionLocal() as session:
        row = session.scalar(
            select(LearnerFeedbackNote).where(LearnerFeedbackNote.user_id == user_id)
        )
        assert row is not None
        assert row.email == account_email
        assert row.message == "The forge timeline is the part I trust."
        assert row.locale == "pt-BR"
        assert row.path is not None
        assert row.path.startswith("/roadmap")
        assert len(row.path) == 200
        assert row.replied_at is None
        assert row.created_at is not None
    assert sent == ["desk@example.com"]
    assert captured == []


def test_empty_message_is_rejected(client: TestClient) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    user_id = _learner(external_id, f"{external_id}@example.com")
    response = _post(client, external_id, message="  \n\t ")
    assert response.status_code == 400, response.text
    assert _count_for(user_id) == 0


def test_sixth_note_inside_24_hours_is_rejected_and_an_older_one_does_not_count(
    client: TestClient,
) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    account_email = f"{external_id}@example.com"
    user_id = _learner(external_id, account_email)
    old = datetime.now(timezone.utc) - timedelta(hours=25)
    with SessionLocal() as session:
        session.add(
            LearnerFeedbackNote(
                user_id=user_id,
                email=account_email,
                message="yesterday",
                created_at=old,
            )
        )
        session.commit()

    for index in range(5):
        response = _post(client, external_id, message=f"note {index}")
        assert response.status_code == 200, response.text

    rejected = _post(client, external_id, message="note 5 stays")
    assert rejected.status_code == 429, rejected.text
    assert _count_for(user_id) == 6


def test_missing_account_email_and_signed_out_do_not_store(
    client: TestClient,
) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    user_id = _learner(external_id, None)
    missing = _post(client, external_id, message="no address")
    assert missing.status_code == 400, missing.text
    assert _count_for(user_id) == 0

    with TestClient(app) as anonymous_client:
        anonymous = anonymous_client.post(
            "/me/feedback",
            json={"message": "from the outside", "email": "anyone@example.com"},
        )
    assert anonymous.status_code == 401


def test_empty_notify_address_and_a_failed_notice_still_accept(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    user_id = _learner(external_id, f"{external_id}@example.com")
    calls: list[str] = []

    class _Mailer:
        def send_feedback_notice(self, *, to_email: str) -> None:
            calls.append(to_email)

    monkeypatch.setattr(
        "career_forge.services.learner_feedback.get_mailer",
        lambda: _Mailer(),
    )
    monkeypatch.setattr(settings, "feedback_notify_email", "")
    quiet = _post(client, external_id, message="stored without a notice")
    assert quiet.status_code == 200, quiet.text
    assert calls == []

    monkeypatch.setattr(settings, "feedback_notify_email", "desk@example.com")

    class _Boom:
        def send_feedback_notice(self, *, to_email: str) -> None:
            raise RuntimeError("smtp down")

    monkeypatch.setattr(
        "career_forge.services.learner_feedback.get_mailer",
        lambda: _Boom(),
    )
    failed = _post(client, external_id, message="stored after a failed notice")
    assert failed.status_code == 200, failed.text
    assert _count_for(user_id) == 2


def _login(raw_client: TestClient, monkeypatch: pytest.MonkeyPatch, email: str) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "616161")
    requested = raw_client.post("/operator/auth/otp/request", json={"email": email})
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": "616161"},
    )
    assert verified.status_code == 200, verified.text


def test_access_operator_lists_newest_first_and_toggles_replied(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_id = f"feedback-{uuid.uuid4().hex}"
    account_email = f"{external_id}@example.com"
    user_id = _learner(external_id, account_email)
    assert _post(client, external_id, message="older note", path="/forge").status_code == 200
    assert _post(client, external_id, message="newer note", path="/roadmap").status_code == 200
    stamped = datetime.now(timezone.utc)
    with SessionLocal() as session:
        older = session.scalar(
            select(LearnerFeedbackNote).where(LearnerFeedbackNote.message == "older note")
        )
        newer = session.scalar(
            select(LearnerFeedbackNote).where(LearnerFeedbackNote.message == "newer note")
        )
        assert older is not None and newer is not None
        older.created_at = stamped - timedelta(seconds=10)
        newer.created_at = stamped
        session.add_all(
            [
                LearnerFeedbackNote(
                    user_id=user_id,
                    email=account_email,
                    message=f"filler {index}",
                    path="/onboarding",
                    created_at=stamped - timedelta(minutes=index + 1),
                )
                for index in range(99)
            ]
        )
        session.commit()

    monkeypatch.setattr(
        settings,
        "operator_allowlist",
        "notes-access@borderless.com:access,notes-editor@borderless.com:editor,notes-both@borderless.com:both",
    )
    with TestClient(app) as raw_client:
        _login(raw_client, monkeypatch, "notes-access@borderless.com")
        listed = raw_client.get("/operator/access/feedback-notes")
        assert listed.status_code == 200, listed.text
        notes = listed.json()["notes"]
        assert len(notes) == 100
        assert notes[0]["message"] == "newer note"
        assert notes[0]["email"] == account_email
        assert notes[0]["path"] == "/roadmap"
        assert notes[0]["replied_at"] is None
        assert "user_id" not in notes[0]
        assert all(item["message"] != "filler 98" for item in notes)

        note_id = notes[0]["id"]
        marked = raw_client.patch(
            f"/operator/access/feedback-notes/{note_id}",
            json={"replied": True},
        )
        assert marked.status_code == 200, marked.text
        assert marked.json()["replied_at"] is not None

        cleared = raw_client.patch(
            f"/operator/access/feedback-notes/{note_id}",
            json={"replied": False},
        )
        assert cleared.status_code == 200, cleared.text
        assert cleared.json()["replied_at"] is None

        raw_client.post("/operator/auth/sign-out")
        _login(raw_client, monkeypatch, "notes-both@borderless.com")
        both = raw_client.get("/operator/access/feedback-notes")
        assert both.status_code == 200, both.text

        raw_client.post("/operator/auth/sign-out")
        _login(raw_client, monkeypatch, "notes-editor@borderless.com")
        hidden = raw_client.get("/operator/access/feedback-notes")
        assert hidden.status_code == 403, hidden.text
        blocked = raw_client.patch(
            f"/operator/access/feedback-notes/{note_id}",
            json={"replied": True},
        )
        assert blocked.status_code == 403, blocked.text
