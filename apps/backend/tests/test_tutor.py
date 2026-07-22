"""Tests — chapter Q&A tutor grounded in concepts + references + gaps (HAC-71)."""

from __future__ import annotations

from sqlalchemy import select

from career_forge.db.models.user import User
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.knowledge_gap import KnowledgeGapDraft
from career_forge.services import knowledge_gaps as gaps_svc
from career_forge.services.tutor import load_tutor_context

NODE_ID = "gen-tutor"
CONCEPTS = ["idempotência de PUT", "status codes HTTP"]


def _node() -> UserSkillNode:
    return UserSkillNode(
        node_id=NODE_ID,
        title="Grounded generation",
        status=SkillStatus.RECOMENDADO,
        mastery_score=0,
        priority=Priority.HIGH,
        key_concepts=CONCEPTS,
        tasks=[{"title": "Estudar REST", "outcome": "Aplicar", "evidence_prompt": "Mostre"}],
        references=[{"title": "MDN HTTP", "url": "https://developer.mozilla.org"}],
    )


def _sync(client, user_id: str) -> None:
    response = client.post(
        "/roadmap/sync",
        json={"user_id": user_id, "nodes": [_node().model_dump()]},
    )
    assert response.status_code == 200


def test_tutor_context_grounds_in_concepts_refs_gaps(client) -> None:
    _sync(client, "tutor-ctx")
    with SessionLocal() as session:
        user = session.scalar(select(User).where(User.external_id == "tutor-ctx"))
        gaps_svc.upsert_knowledge_gap(
            session,
            user_id=user.id,
            skill_node_id=NODE_ID,
            draft=KnowledgeGapDraft(concept="status codes HTTP", severity="high"),
        )
        session.commit()

    with SessionLocal() as session:
        ctx = load_tutor_context(session, "tutor-ctx", NODE_ID, "Grounded generation")

    assert ctx.key_concepts == CONCEPTS
    assert any(ref.title == "MDN HTTP" for ref in ctx.references)
    assert "status codes HTTP" in ctx.open_gaps


def test_post_tutor_returns_grounded_reply(client) -> None:
    _sync(client, "tutor-chat")
    response = client.post(
        "/tutor",
        json={
            "user_id": "tutor-chat",
            "node_id": NODE_ID,
            "node_title": "Grounded generation",
            "message": "O que é idempotência de PUT?",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "completed"
    assert body["tutor"]["reply"]
    assert body["tutor"]["context"]["key_concepts"] == CONCEPTS


def test_tutor_context_endpoint(client) -> None:
    _sync(client, "tutor-ep")
    response = client.get(
        "/tutor/context",
        params={"user_id": "tutor-ep", "node_id": NODE_ID, "node_title": "Grounded generation"},
    )
    assert response.status_code == 200
    assert response.json()["key_concepts"] == CONCEPTS


def test_tutor_agent_is_registered() -> None:
    from career_forge.ai.factory import AgentFactory

    agent = AgentFactory().get("tutor")
    assert agent.graph_name == "tutor"
