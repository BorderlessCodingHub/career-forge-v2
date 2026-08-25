"""Operational Reference embed allowlist API contract (CAR-89).

Seams: Content desk CRUD and learner-authenticated GET.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.embed_allowlist import EmbedHostAudit
from career_forge.db.models.skill_node import SkillNode
from career_forge.db.models.user_skill_node import UserSkillNode
from career_forge.db.repositories.user import ensure_user
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
    assert [item["host"] for item in listed.json()["liberated"]].count(host) == 1

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
    forbidden_revoke = raw_client.delete(
        "/operator/content/embed-hosts/developer.mozilla.org"
    )
    assert forbidden_revoke.status_code == 403
    assert forbidden_revoke.json()["detail"]["code"] == "content_desk_forbidden"

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


def test_embed_allowlist_refuses_hosts_that_cover_the_app_own_origin(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`allow-same-origin` lets a same-origin frame strip its own sandbox."""
    suffix = uuid.uuid4().hex
    self_host = f"app-{suffix[:10]}.borderless-self.test"
    parent_host = "borderless-self.test"
    monkeypatch.setattr(
        settings,
        "frontend_url",
        f"https://{self_host}/career-forge",
    )
    monkeypatch.setattr(settings, "cors_origins", f"https://{self_host}")

    skill_id = f"car90-self-{suffix[:10]}"
    with SessionLocal() as session:
        user = ensure_user(session, f"car90-self-learner-{suffix}")
        session.add(
            SkillNode(
                id=skill_id,
                track_id="rag-engineer-beginner",
                title="CAR-90 self-origin reference",
                category="core",
                description="Self-origin guard fixture",
                sort_order=95,
                prerequisites=[],
                outcomes=[],
                rubric=[],
                key_concepts=[],
            )
        )
        session.flush()
        session.add(
            UserSkillNode(
                user_id=user.id,
                skill_node_id=skill_id,
                status="em_estudo",
                evidence={
                    "checklist": [
                        {
                            "type": "reference",
                            "id": "self-ref",
                            "url": f"https://{self_host}/career-forge/reference",
                        }
                    ],
                    "validation": None,
                    "remediation": [],
                    "metadata": {"sort_order": 95},
                },
                checklist_progress={},
                updated_at=datetime.now(UTC),
            )
        )
        session.commit()

    _login_operator(
        raw_client,
        monkeypatch,
        email="embed-self-editor@borderless.com",
        role="editor",
    )

    for candidate in (self_host, f"WWW.{self_host}", parent_host):
        refused = raw_client.post(
            "/operator/content/embed-hosts",
            json={"host": candidate},
        )
        assert refused.status_code == 422, refused.text

    queued = raw_client.get("/operator/content/embed-hosts")
    assert queued.status_code == 200, queued.text
    assert self_host not in {item["host"] for item in queued.json()["pending"]}

    learner_headers = {
        "Authorization": f"Bearer {get_auth_provider().mint_email('car90-self-reader')}"
    }
    hosts = raw_client.get("/reference/embed-hosts", headers=learner_headers)
    assert hosts.status_code == 200, hosts.text
    assert self_host not in hosts.json()["hosts"]
    assert parent_host not in hosts.json()["hosts"]


def test_content_operator_queue_groups_distinct_live_reference_urls_without_identity(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    suffix = uuid.uuid4().hex
    skill_ids = [f"car90-{suffix[:10]}-{index}" for index in range(2)]
    host = f"docs-{suffix}.example.com"
    urls = [
        f"https://{host}/guide/one",
        f"https://www.{host}/guide/two",
    ]
    with SessionLocal() as session:
        user = ensure_user(session, f"car90-learner-{suffix}")
        for index, skill_id in enumerate(skill_ids):
            session.add(
                SkillNode(
                    id=skill_id,
                    track_id="rag-engineer-beginner",
                    title=f"CAR-90 live references {index}",
                    category="core",
                    description="Queue aggregation fixture",
                    sort_order=90 + index,
                    prerequisites=[],
                    outcomes=[],
                    rubric=[],
                    key_concepts=[],
                )
            )
        session.flush()
        now = datetime.now(UTC)
        for index, (skill_id, url) in enumerate(zip(skill_ids, urls, strict=True)):
            session.add(
                UserSkillNode(
                    user_id=user.id,
                    skill_node_id=skill_id,
                    status="em_estudo",
                    evidence={
                        "checklist": [
                            {"type": "reference", "id": f"ref-{index}", "url": url},
                            {"type": "reference", "id": f"dup-{index}", "url": urls[0]},
                        ],
                        "validation": None,
                        "remediation": [],
                        "metadata": {"sort_order": 90 + index},
                    },
                    checklist_progress={},
                    updated_at=now + timedelta(minutes=index),
                )
            )
        session.commit()

    _login_operator(
        raw_client,
        monkeypatch,
        email="embed-queue-editor@borderless.com",
        role="editor",
    )
    response = raw_client.get("/operator/content/embed-hosts")

    assert response.status_code == 200, response.text
    pending = next(item for item in response.json()["pending"] if item["host"] == host)
    assert pending == {
        "host": host,
        "sample_url": urls[1],
        "distinct_url_count": 2,
    }
    assert "user_id" not in pending
    assert "email" not in pending
    assert "liberated" in response.json()

    liberated = raw_client.post(
        "/operator/content/embed-hosts",
        json={"host": host},
    )
    assert liberated.status_code == 200, liberated.text
    refreshed = raw_client.get("/operator/content/embed-hosts")
    assert refreshed.status_code == 200, refreshed.text
    assert host not in {item["host"] for item in refreshed.json()["pending"]}
    assert host in {item["host"] for item in refreshed.json()["liberated"]}
