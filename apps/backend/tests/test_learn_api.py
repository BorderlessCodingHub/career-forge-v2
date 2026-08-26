"""ADR-004 — learner GET /learn/{skill_id} and live canonical refs on the trail.

Seams: GET /learn/{skill_id}, GET /roadmap/current nodes[].canonical.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from career_forge.db.models.skill_content import SkillContent
from career_forge.db.models.skill_node import SkillNode
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import SkillStatus, UserSkillNode
from career_forge.services.profile_diagnosis import confirm_diagnosis
from career_forge.schemas.profile_diagnosis import DiagnosisConfirmRequest
from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse


def _publish(skill_id: str, title: str, body: str, canonical_dir) -> None:
    (canonical_dir / f"{skill_id}.md").write_text(body, encoding="utf-8")
    with SessionLocal() as session:
        existing = session.get(SkillContent, skill_id)
        if existing is None:
            session.add(
                SkillContent(
                    skill_id=skill_id,
                    title=title,
                    published=True,
                )
            )
        else:
            existing.title = title
            existing.published = True
        session.commit()


def test_get_learn_returns_published_body_and_404_when_silent(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    skill_id = f"car94-learn-{uuid.uuid4().hex[:8]}"
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir()
    monkeypatch.setenv("CANONICAL_CONTENT_DIR", str(canonical_dir))

    missing = client.get(f"/learn/{skill_id}")
    assert missing.status_code == 404

    _publish(skill_id, "Live title", "# Hello\n\nDeep dive.\n", canonical_dir)

    with SessionLocal() as session:
        session.add(
            SkillNode(
                id=skill_id,
                track_id="rag-engineer-beginner",
                title="Catalog title",
                category="core",
                sort_order=1,
                prerequisites=[],
                outcomes=[],
                rubric=[],
                key_concepts=[],
            )
        )
        session.commit()

    found = client.get(f"/learn/{skill_id}")
    assert found.status_code == 200, found.text
    payload = found.json()
    assert payload["skill_id"] == skill_id
    assert payload["title"] == "Live title"
    assert payload["body_markdown"].startswith("# Hello")
    via_content = client.get(f"/learn/{skill_id}/content")
    assert via_content.status_code == 200
    assert via_content.json() == payload

    with SessionLocal() as session:
        row = session.get(SkillContent, skill_id)
        row.published = False
        session.commit()

    draft = client.get(f"/learn/{skill_id}")
    assert draft.status_code == 404


def test_roadmap_attaches_live_ref_only_on_focus_nodes(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    user_id = f"car94-trail-{uuid.uuid4().hex[:8]}"
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir()
    monkeypatch.setenv("CANONICAL_CONTENT_DIR", str(canonical_dir))

    _publish("rag-chunking", "Chunking for RAG", "# Chunking\n", canonical_dir)
    _publish("rag-eval", "Eval deep-dive", "# Eval\n", canonical_dir)

    with SessionLocal() as session:
        confirm_diagnosis(
            session,
            DiagnosisConfirmRequest(
                user_id=user_id,
                goal_id="no-must-haves-goal",
                motivation="I want a focused RAG path for this attach test.",
                diagnosis=DiagnosisResponse(
                    profile=DiagnosisProfile(
                        label="Test learner",
                        track_id="rag-engineer-beginner",
                    ),
                    strengths=["Python"],
                    gaps=["Chunking"],
                    starting_priorities=["rag-chunking"],
                    estimated_mastery={"rag-chunking": 20},
                ),
            ),
        )

    synced = client.post(
        "/roadmap/sync",
        json={
            "user_id": user_id,
            "nodes": [
                UserSkillNode(
                    node_id="rag-chunking",
                    status=SkillStatus.RECOMENDADO,
                    mastery_score=20,
                ).model_dump(),
                UserSkillNode(
                    node_id="rag-eval",
                    status=SkillStatus.BLOQUEADO,
                    mastery_score=0,
                ).model_dump(),
            ],
        },
    )
    assert synced.status_code == 200, synced.text

    try:
        trail = client.get("/roadmap/current", params={"user_id": user_id})
        assert trail.status_code == 200, trail.text
        by_id = {node["node_id"]: node for node in trail.json()["nodes"]}

        assert by_id["rag-chunking"]["canonical"] == {
            "skill_id": "rag-chunking",
            "title": "Chunking for RAG",
        }
        assert by_id["rag-eval"]["canonical"] is None
    finally:
        with SessionLocal() as session:
            for skill_id in ("rag-chunking", "rag-eval"):
                row = session.get(SkillContent, skill_id)
                if row is not None and row.title in {
                    "Chunking for RAG",
                    "Eval deep-dive",
                }:
                    session.delete(row)
            session.commit()
