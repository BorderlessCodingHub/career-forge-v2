"""Tests — key_concepts flow planner → persistence → mock context (HAC-70)."""

from __future__ import annotations

from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services.mock_interview_context import build_mock_interview_context
from career_forge.services.roadmap import resolve_skill_node_catalog_entry

NODE_ID = "gen-key-concepts"
CONCEPTS = ["idempotência de PUT", "status codes HTTP", "design de recursos REST"]


def _node() -> UserSkillNode:
    return UserSkillNode(
        node_id=NODE_ID,
        title="APIs REST",
        status=SkillStatus.RECOMENDADO,
        mastery_score=0,
        priority=Priority.HIGH,
        key_concepts=CONCEPTS,
        tasks=[{"title": "Estudar REST", "outcome": "Aplicar", "evidence_prompt": "Mostre"}],
        references=[{"title": "MDN", "url": "https://developer.mozilla.org"}],
    )


def test_key_concepts_persist_and_surface(client) -> None:
    response = client.post(
        "/roadmap/sync",
        json={"user_id": "kc-user", "nodes": [_node().model_dump()]},
    )
    assert response.status_code == 200

    with SessionLocal() as session:
        ctx = resolve_skill_node_catalog_entry(session, NODE_ID)
        assert ctx["key_concepts"] == CONCEPTS

        study_block, _ = build_mock_interview_context(
            session, user_id="kc-user", node_id=NODE_ID
        )
        assert study_block["key_concepts"] == CONCEPTS


def test_study_plan_node_defaults_key_concepts_empty() -> None:
    from career_forge.schemas.study_plan import StudyPlanNode, StudyPlanTask

    node = StudyPlanNode(
        node_id="n1",
        title="Tópico",
        why_now="agora",
        tasks=[StudyPlanTask(title="t", outcome="o", evidence_prompt="e")],
    )
    assert node.key_concepts == []
