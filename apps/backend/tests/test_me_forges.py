"""HTTP tests — /me/forges list + open freeze-before-promote (CAR-25)."""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.auth.providers import get_auth_provider
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services.forge_persistence import persist_graph_ready
from career_forge.services.roadmap import sync_user_graph


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    with SessionLocal() as session:
        row = ensure_user(session, external_id)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def _nodes(prefix: str, mastery: int = 20) -> list[dict]:
    return [
        UserSkillNode(
            node_id=f"{prefix}-a",
            title=f"{prefix} A",
            status=SkillStatus.RECOMENDADO,
            mastery_score=mastery,
            priority=Priority.HIGH,
            rationale="r",
            prerequisites=[],
            key_concepts=[],
            tasks=[{"title": "t", "outcome": "o", "evidence_prompt": "e"}],
            references=[],
        ).model_dump(mode="json"),
        UserSkillNode(
            node_id=f"{prefix}-b",
            title=f"{prefix} B",
            status=SkillStatus.BLOQUEADO,
            mastery_score=0,
            priority=Priority.MEDIUM,
            rationale="r",
            prerequisites=[f"{prefix}-a"],
            key_concepts=[],
            tasks=[],
            references=[],
        ).model_dump(mode="json"),
    ]


def test_list_forges_requires_bearer(raw_client: TestClient) -> None:
    res = raw_client.get("/me/forges")
    assert res.status_code == 401


def test_list_forges_isolates_users(raw_client: TestClient) -> None:
    persist_graph_ready(
        "me-forges-user-a",
        {"type": "graph_ready", "graph": _nodes("iso-a")},
        graph_run_id="run-iso-a",
        goal_id="rag-engineer",
    )
    persist_graph_ready(
        "me-forges-user-b",
        {"type": "graph_ready", "graph": _nodes("iso-b")},
        graph_run_id="run-iso-b",
        goal_id="agent-engineer",
    )

    headers_a = _auth_headers(raw_client, "me-forges-user-a")
    res = raw_client.get("/me/forges", headers=headers_a)
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["graph_run_id"] == "run-iso-a"
    assert "id" not in items[0]
    assert items[0]["public_id"]
    assert items[0]["is_active"] is True


def test_open_promotes_and_freezes_previous(raw_client: TestClient) -> None:
    user = "me-forges-user-open"
    first = persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes("open1", mastery=10)},
        graph_run_id="run-open-1",
        goal_id="rag-engineer",
    )
    second = persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes("open2", mastery=20)},
        graph_run_id="run-open-2",
        goal_id="agent-engineer",
    )
    assert first is not None and second is not None

    # Mutate live roadmap (progress on active forge) before switching back.
    with SessionLocal() as session:
        mutated = [
            UserSkillNode.model_validate({**n, "mastery_score": 77})
            for n in _nodes("open2", mastery=20)
        ]
        sync_user_graph(session, user, mutated)

    headers = _auth_headers(raw_client, user)
    res = raw_client.post(f"/me/forges/{first.public_id}/open", headers=headers)
    assert res.status_code == 200, res.text
    roadmap = res.json()
    node_ids = {n["node_id"] for n in roadmap["nodes"]}
    assert "open1-a" in node_ids
    assert "open2-a" not in node_ids

    with SessionLocal() as session:
        rows = {
            row.graph_run_id: row
            for row in session.scalars(
                select(ForgeArtifact).where(
                    ForgeArtifact.graph_run_id.in_(["run-open-1", "run-open-2"]),
                ),
            )
        }
        assert rows["run-open-1"].is_active is True
        assert rows["run-open-2"].is_active is False
        frozen_mastery = {
            n["node_id"]: n["mastery_score"] for n in rows["run-open-2"].snapshot
        }
        assert frozen_mastery.get("open2-a") == 77

    roadmap_get = raw_client.get("/roadmap/", headers=headers)
    assert roadmap_get.status_code == 200
    get_ids = {n["node_id"] for n in roadmap_get.json()["nodes"]}
    assert "open1-a" in get_ids


def test_open_other_user_or_unknown_returns_404(raw_client: TestClient) -> None:
    artifact = persist_graph_ready(
        "me-forges-owner",
        {"type": "graph_ready", "graph": _nodes("own")},
        graph_run_id="run-own-1",
        goal_id="rag-engineer",
    )
    assert artifact is not None

    thief = _auth_headers(raw_client, "me-forges-thief")
    res = raw_client.post(f"/me/forges/{artifact.public_id}/open", headers=thief)
    assert res.status_code == 404

    owner = _auth_headers(raw_client, "me-forges-owner")
    missing = raw_client.post(f"/me/forges/{uuid.uuid4()}/open", headers=owner)
    assert missing.status_code == 404


def test_open_already_active_is_idempotent(raw_client: TestClient) -> None:
    user = "me-forges-idem"
    artifact = persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes("idem")},
        graph_run_id="run-idem-1",
        goal_id="rag-engineer",
    )
    assert artifact is not None
    headers = _auth_headers(raw_client, user)
    first = raw_client.post(f"/me/forges/{artifact.public_id}/open", headers=headers)
    second = raw_client.post(f"/me/forges/{artifact.public_id}/open", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 200
    assert {n["node_id"] for n in first.json()["nodes"]} == {
        n["node_id"] for n in second.json()["nodes"]
    }


def test_patch_forge_title(raw_client: TestClient) -> None:
    user = "me-forges-title"
    artifact = persist_graph_ready(
        user,
        {"type": "graph_ready", "graph": _nodes("title")},
        graph_run_id="run-title-1",
        goal_id="rag-engineer",
    )
    assert artifact is not None
    headers = _auth_headers(raw_client, user)

    res = raw_client.patch(
        f"/me/forges/{artifact.public_id}",
        headers=headers,
        json={"title": "  My custom roadmap  "},
    )
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["title"] == "My custom roadmap"
    assert body["public_id"] == str(artifact.public_id)

    listed = raw_client.get("/me/forges", headers=headers)
    assert listed.status_code == 200
    assert listed.json()["items"][0]["title"] == "My custom roadmap"


def test_patch_forge_title_other_user_404(raw_client: TestClient) -> None:
    artifact = persist_graph_ready(
        "me-forges-title-owner",
        {"type": "graph_ready", "graph": _nodes("ttl")},
        graph_run_id="run-title-x",
        goal_id="rag-engineer",
    )
    assert artifact is not None
    thief = _auth_headers(raw_client, "me-forges-title-thief")
    res = raw_client.patch(
        f"/me/forges/{artifact.public_id}",
        headers=thief,
        json={"title": "stolen"},
    )
    assert res.status_code == 404
