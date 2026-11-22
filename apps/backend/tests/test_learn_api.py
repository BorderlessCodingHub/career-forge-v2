"""LABS01-222 — the skill lesson leaves the Node and the old /learn address.

Seams: GET /roadmap/current nodes[].canonical, GET /learn/{skill_id}.
"""

from __future__ import annotations

import uuid

from fastapi.testclient import TestClient

from career_forge.db.models.skill_content import SkillContent
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


def test_learn_address_does_not_present_the_skill_lesson(
    client: TestClient, monkeypatch, tmp_path
) -> None:
    skill_id = f"car94-learn-{uuid.uuid4().hex[:8]}"
    canonical_dir = tmp_path / "canonical"
    canonical_dir.mkdir()
    monkeypatch.setenv("CANONICAL_CONTENT_DIR", str(canonical_dir))
    _publish(skill_id, "Live title", "# Hello\n\nDeep dive.\n", canonical_dir)

    found = client.get(f"/learn/{skill_id}")
    assert found.status_code == 404
    assert found.json()["detail"] == "skill lesson not found"
    assert "canonical skill content" not in found.text
    assert "Deep dive" not in found.text
    assert "Live title" not in found.text

    via_content = client.get(f"/learn/{skill_id}/content")
    assert via_content.status_code == 404
    assert via_content.json()["detail"] == "skill lesson not found"
    assert "canonical skill content" not in via_content.text
    assert "Deep dive" not in via_content.text


def test_roadmap_node_does_not_carry_the_skill_lesson(
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

        assert by_id["rag-chunking"]["canonical"] is None
        assert by_id["rag-eval"]["canonical"] is None
        assert "Chunking for RAG" not in trail.text
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
