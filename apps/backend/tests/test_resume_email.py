"""Send forge resume link by email (CAR-47)."""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.config import settings
from career_forge.db.models.forge_access_token import ROLE_RESUME, ForgeAccessToken
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services import otp as otp_service
from career_forge.services.forge_persistence import persist_graph_ready


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def _promote_email(
    raw_client: TestClient,
    *,
    external_id: str,
    email: str,
    code: str,
) -> dict[str, str]:
    headers = _auth_headers(raw_client, external_id)
    req = raw_client.post(
        "/auth/otp/request",
        json={"email": email},
        headers=headers,
    )
    assert req.status_code == 200, req.text
    verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": email, "code": code},
        headers=headers,
    )
    assert verify.status_code == 200, verify.text
    body = verify.json()
    assert body["provider"] == EMAIL_PROVIDER
    return {"Authorization": f"Bearer {body['access_token']}"}


def _nodes(prefix: str) -> list[dict]:
    return [
        UserSkillNode(
            node_id=f"{prefix}-a",
            title=f"{prefix} A",
            status=SkillStatus.RECOMENDADO,
            mastery_score=30,
            priority=Priority.HIGH,
            rationale="r",
            prerequisites=[],
            key_concepts=[],
            tasks=[{"title": "t", "outcome": "o", "evidence_prompt": "e"}],
            references=[],
        ).model_dump(mode="json"),
    ]


def _persist(user: str, run_id: str):
    return persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes(run_id)},
        graph_run_id=run_id,
        goal_id="rag-engineer",
    )


def test_email_resume_requires_otp_verified_session(
    raw_client: TestClient,
) -> None:
    artifact = _persist("resume-email-anon", "run-resume-email-anon")
    assert artifact is not None
    headers = _auth_headers(raw_client, "resume-email-anon")

    # Optional CAR-29 store is not enough — still anonymous JWT.
    patch = raw_client.patch(
        "/me/email",
        json={"email": "stored-only@example.com"},
        headers=headers,
    )
    assert patch.status_code == 200, patch.text

    res = raw_client.post(
        f"/me/forges/{artifact.public_id}/resume/email",
        headers=headers,
    )
    assert res.status_code == 400
    assert "verify" in res.json()["detail"].lower() or "email" in res.json()["detail"].lower()


def test_email_resume_sends_link_via_mailer(
    raw_client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "555666")
    settings.frontend_url = "http://localhost:3300/career-forge"

    sent: list[dict[str, str]] = []

    class _CaptureMailer:
        def send_otp(self, *, to_email: str, code: str) -> None:
            return None

        def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
            sent.append({"to_email": to_email, "resume_url": resume_url})

    monkeypatch.setattr(
        "career_forge.services.forge_access_tokens.get_mailer",
        lambda: _CaptureMailer(),
    )

    owner = "resume-email-owner"
    artifact = _persist(owner, "run-resume-email-ok")
    assert artifact is not None
    headers = _promote_email(
        raw_client,
        external_id=owner,
        email="verified-pilot@example.com",
        code="555666",
    )

    res = raw_client.post(
        f"/me/forges/{artifact.public_id}/resume/email",
        headers=headers,
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["ok"] is True
    assert body["email"] == "verified-pilot@example.com"
    assert body["path"].startswith("/resume/")

    assert len(sent) == 1
    assert sent[0]["to_email"] == "verified-pilot@example.com"
    assert sent[0]["resume_url"] == (
        f"http://localhost:3300/career-forge{body['path']}"
    )

    with SessionLocal() as session:
        rows = list(
            session.scalars(
                select(ForgeAccessToken).where(
                    ForgeAccessToken.role == ROLE_RESUME,
                ),
            ),
        )
        assert any(row.revoked_at is None and row.consumed_at is None for row in rows)


def test_email_resume_rolls_back_when_mailer_fails(
    raw_client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "999000")
    settings.frontend_url = "http://localhost:3300/career-forge"

    class _FailingMailer:
        def send_otp(self, *, to_email: str, code: str) -> None:
            return None

        def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
            raise RuntimeError("smtp down")

    monkeypatch.setattr(
        "career_forge.services.forge_access_tokens.get_mailer",
        lambda: _FailingMailer(),
    )

    owner = "resume-email-fail"
    artifact = _persist(owner, "run-resume-email-fail")
    assert artifact is not None
    headers = _promote_email(
        raw_client,
        external_id=owner,
        email="fail-pilot@example.com",
        code="999000",
    )

    with SessionLocal() as session:
        before = len(
            list(
                session.scalars(
                    select(ForgeAccessToken).where(
                        ForgeAccessToken.role == ROLE_RESUME,
                    ),
                ),
            ),
        )

    res = raw_client.post(
        f"/me/forges/{artifact.public_id}/resume/email",
        headers=headers,
    )
    assert res.status_code == 400
    assert "failed to send" in res.json()["detail"].lower()

    with SessionLocal() as session:
        after = len(
            list(
                session.scalars(
                    select(ForgeAccessToken).where(
                        ForgeAccessToken.role == ROLE_RESUME,
                    ),
                ),
            ),
        )
        assert after == before


def test_email_resume_link_consumable(
    raw_client: TestClient,
    monkeypatch,
) -> None:
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "777888")
    settings.frontend_url = "http://localhost:3300/career-forge"

    class _QuietMailer:
        def send_otp(self, *, to_email: str, code: str) -> None:
            return None

        def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
            return None

    monkeypatch.setattr(
        "career_forge.services.forge_access_tokens.get_mailer",
        lambda: _QuietMailer(),
    )

    owner = "resume-email-consume"
    artifact = _persist(owner, "run-resume-email-consume")
    assert artifact is not None
    headers = _promote_email(
        raw_client,
        external_id=owner,
        email="consume-pilot@example.com",
        code="777888",
    )

    res = raw_client.post(
        f"/me/forges/{artifact.public_id}/resume/email",
        headers=headers,
    )
    assert res.status_code == 200, res.text
    token = res.json()["path"].removeprefix("/resume/")

    consume = raw_client.post(f"/public/resume/{token}")
    assert consume.status_code == 200, consume.text
    assert consume.json()["external_id"] == owner
