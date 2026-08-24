"""Content desk API contract (CAR-79).

Seams: GET/PATCH /operator/content/skills.
"""

from __future__ import annotations

import json
import uuid

import pytest
from fastapi.testclient import TestClient

from career_forge.config import settings
from career_forge.db.models.skill_node import SkillNode
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
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "797979")
    requested = raw_client.post(
        "/operator/auth/otp/request",
        json={"email": email},
    )
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": "797979"},
    )
    assert verified.status_code == 200, verified.text


def _catalog_skill() -> SkillNode:
    suffix = uuid.uuid4().hex[:10]
    return SkillNode(
        id=f"car79-{suffix}",
        track_id="rag-engineer-beginner",
        title="Catalog fallback title",
        category="core",
        description="Content desk test skill",
        sort_order=79,
        prerequisites=[],
        outcomes=[],
        rubric=[],
        key_concepts=[],
    )


def _write_catalog(catalog_dir, skill: SkillNode) -> None:
    (catalog_dir / "rag-engineer-beginner.json").write_text(
        json.dumps(
            {
                "track": {
                    "id": skill.track_id,
                    "title": "RAG",
                    "description": "Test catalog",
                },
                "categories": [{"id": skill.category, "label": "Core"}],
                "nodes": [
                    {
                        "id": skill.id,
                        "title": skill.title,
                        "category": skill.category,
                        "description": skill.description,
                        "sort_order": skill.sort_order,
                    }
                ],
            }
        )
    )


def test_content_desk_lists_catalog_ids_with_read_only_body_status(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    catalog_dir = tmp_path / "catalog"
    catalog_dir.mkdir()
    monkeypatch.setenv("CATALOG_DIR", str(catalog_dir))
    _login_operator(
        raw_client,
        monkeypatch,
        email="editor@borderless.com",
        role="editor",
    )
    skill = _catalog_skill()
    skill_id = skill.id
    _write_catalog(catalog_dir, skill)
    with SessionLocal() as session:
        session.add_all(
            [
                skill,
                SkillNode(
                    id=f"ai-generated-{uuid.uuid4().hex[:10]}",
                    track_id="ai-generated",
                    title="Personalized node",
                    category="generated",
                    sort_order=1,
                    prerequisites=[],
                    outcomes=[],
                    rubric=[],
                    key_concepts=[],
                ),
            ]
        )
        session.commit()

    response = raw_client.get("/operator/content/skills")

    assert response.status_code == 200, response.text
    listed = {item["skill_id"]: item for item in response.json()["skills"]}
    assert listed[skill_id] == {
        "skill_id": skill_id,
        "track_id": "rag-engineer-beginner",
        "title": "Catalog fallback title",
        "description": "Content desk test skill",
        "url": None,
        "published": False,
        "body_present": False,
    }
    assert len(listed) == 1


def test_content_desk_updates_metadata_and_only_publishes_with_git_body(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    catalog_dir = tmp_path / "catalog"
    canonical_dir = tmp_path / "canonical"
    catalog_dir.mkdir()
    canonical_dir.mkdir()
    monkeypatch.setenv("CATALOG_DIR", str(catalog_dir))
    _login_operator(
        raw_client,
        monkeypatch,
        email="editor-publish@borderless.com",
        role="editor",
    )
    skill = _catalog_skill()
    skill_id = skill.id
    _write_catalog(catalog_dir, skill)

    draft = raw_client.patch(
        f"/operator/content/skills/{skill_id}",
        json={
            "title": "Edited canonical title",
            "url": "https://learn.borderlesscoding.com/rag",
            "published": False,
        },
    )

    assert draft.status_code == 200, draft.text
    assert draft.json()["published"] is False
    assert draft.json()["body_present"] is False

    missing_body = raw_client.patch(
        f"/operator/content/skills/{skill_id}",
        json={"published": True},
    )

    assert missing_body.status_code == 409, missing_body.text

    (canonical_dir / f"{skill_id}.md").write_text("# Git-owned body\n")
    published = raw_client.patch(
        f"/operator/content/skills/{skill_id}",
        json={
            "title": "Edited canonical title",
            "url": "https://learn.borderlesscoding.com/rag",
            "published": True,
        },
    )

    assert published.status_code == 200, published.text
    assert published.json() == {
        "skill_id": skill_id,
        "track_id": "rag-engineer-beginner",
        "title": "Edited canonical title",
        "description": "Content desk test skill",
        "url": "https://learn.borderlesscoding.com/rag",
        "published": True,
        "body_present": True,
    }
    listed = raw_client.get("/operator/content/skills").json()["skills"]
    assert {item["skill_id"]: item for item in listed}[skill_id] == published.json()


def test_content_desk_rejects_access_role_and_unknown_catalog_ids(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _login_operator(
        raw_client,
        monkeypatch,
        email="access-only@borderless.com",
        role="access",
    )

    forbidden = raw_client.get("/operator/content/skills")

    assert forbidden.status_code == 403
    assert forbidden.json()["detail"]["code"] == "content_desk_forbidden"

    raw_client.cookies.clear()
    _login_operator(
        raw_client,
        monkeypatch,
        email="editor-no-mint@borderless.com",
        role="editor",
    )
    unknown = raw_client.patch(
        "/operator/content/skills/not-in-the-catalog",
        json={"title": "Must not be minted"},
    )

    assert unknown.status_code == 404


def test_content_desk_exposes_exactly_the_40_repo_catalog_ids(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CATALOG_DIR", raising=False)
    monkeypatch.delenv("ROADMAP_JSON_PATH", raising=False)
    _login_operator(
        raw_client,
        monkeypatch,
        email="editor-inventory@borderless.com",
        role="both",
    )

    response = raw_client.get("/operator/content/skills")

    assert response.status_code == 200, response.text
    skill_ids = [skill["skill_id"] for skill in response.json()["skills"]]
    assert len(skill_ids) == 40
    assert len(set(skill_ids)) == 40
