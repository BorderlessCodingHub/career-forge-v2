"""Operational Reference embed allowlist API contract (CAR-89).

Seams: Content desk CRUD and learner-authenticated GET.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.embed_allowlist import EmbedHostAudit
from career_forge.db.session import SessionLocal
from career_forge.services import operator_otp as operator_otp_service


def _login_operator(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    *,
    email: str,
    role: str,
) -> None:
    monkeypatch.setattr(settings, "operator_allowlist", f"{email}:{role}")
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "898989")
    requested = raw_client.post("/operator/auth/otp/request", json={"email": email})
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": "898989"},
    )
    assert verified.status_code == 200, verified.text


def test_content_operator_adds_and_removes_normalized_host_with_live_learner_reads(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid.uuid4().hex
    host = f"docs-{suffix}.example.com"
    _login_operator(
        raw_client,
        monkeypatch,
        email="embed-editor@borderless.com",
        role="editor",
    )
    learner_headers = {
        "Authorization": f"Bearer {get_auth_provider().mint_email('car89-learner')}"
    }

    initial = raw_client.get("/reference/embed-hosts", headers=learner_headers)
    assert initial.status_code == 200, initial.text
    assert initial.headers["cache-control"] == "no-store"
    assert host not in initial.json()["hosts"]

    created = raw_client.post(
        "/operator/content/embed-hosts",
        json={"host": f"WWW.{host.upper()}."},
    )
    assert created.status_code == 200, created.text
    assert created.json()["host"] == host

    duplicate = raw_client.post(
        "/operator/content/embed-hosts",
        json={"host": host},
    )
    assert duplicate.status_code == 200, duplicate.text
    listed = raw_client.get("/operator/content/embed-hosts")
    assert listed.status_code == 200, listed.text
    assert [item["host"] for item in listed.json()["hosts"]].count(host) == 1

    after_add = raw_client.get("/reference/embed-hosts", headers=learner_headers)
    assert after_add.status_code == 200, after_add.text
    assert host in after_add.json()["hosts"]

    removed = raw_client.delete(f"/operator/content/embed-hosts/{host}")
    assert removed.status_code == 204, removed.text
    after_remove = raw_client.get("/reference/embed-hosts", headers=learner_headers)
    assert after_remove.status_code == 200, after_remove.text
    assert host not in after_remove.json()["hosts"]

    with SessionLocal() as session:
        audit = list(
            session.scalars(
                select(EmbedHostAudit)
                .where(EmbedHostAudit.host == host)
                .order_by(EmbedHostAudit.id)
            )
        )
    assert [row.action for row in audit] == ["add", "remove"]
    assert all(row.actor_email == "embed-editor@borderless.com" for row in audit)
    with SessionLocal() as session:
        with pytest.raises(DBAPIError):
            session.execute(
                delete(EmbedHostAudit).where(EmbedHostAudit.host == host)
            )


def test_embed_allowlist_rejects_access_only_operator_and_unauthenticated_learner(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _login_operator(
        raw_client,
        monkeypatch,
        email="embed-access@borderless.com",
        role="access",
    )

    forbidden = raw_client.post(
        "/operator/content/embed-hosts",
        json={"host": "developer.mozilla.org"},
    )
    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "content_desk_forbidden"

    raw_client.cookies.clear()
    _login_operator(
        raw_client,
        monkeypatch,
        email="embed-both@borderless.com",
        role="both",
    )
    both_host = f"both-{uuid.uuid4().hex}.example.com"
    allowed = raw_client.post(
        "/operator/content/embed-hosts",
        json={"host": both_host},
    )
    assert allowed.status_code == 200, allowed.text

    raw_client.cookies.clear()
    unauthenticated = raw_client.get("/reference/embed-hosts")
    assert unauthenticated.status_code == 401
