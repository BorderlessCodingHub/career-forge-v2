"""CAR-24 — forge_artifacts persist on graph_ready."""

from __future__ import annotations

from sqlalchemy import select

from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.services.forge_persistence import (
    artifact_title,
    extract_goal_id,
    persist_graph_ready,
)


def _sample_nodes() -> list[dict]:
    return [
        UserSkillNode(
            node_id="rag-retrieval",
            title="Retrieval",
            status=SkillStatus.RECOMENDADO,
            mastery_score=20,
            priority=Priority.HIGH,
            rationale="foundation",
            prerequisites=[],
            key_concepts=["embeddings"],
            tasks=[{"title": "t1", "outcome": "o1", "evidence_prompt": "e1"}],
            references=[],
        ).model_dump(mode="json"),
        UserSkillNode(
            node_id="rag-production",
            title="Production",
            status=SkillStatus.BLOQUEADO,
            mastery_score=0,
            priority=Priority.MEDIUM,
            rationale="next",
            prerequisites=["rag-retrieval"],
            key_concepts=[],
            tasks=[],
            references=[],
        ).model_dump(mode="json"),
    ]


def test_persist_graph_ready_ignores_empty_payload() -> None:
    assert persist_graph_ready("user", None) is None
    assert persist_graph_ready("user", {"type": "artifact_found"}) is None
    assert persist_graph_ready("user", {"type": "graph_ready", "graph": []}) is None


def test_extract_goal_id_from_input() -> None:
    assert extract_goal_id({"goal_id": "rag-engineer"}) == "rag-engineer"
    assert extract_goal_id({"diagnosis": {"goal_id": "agent-engineer"}}) == "agent-engineer"
    assert extract_goal_id({}) is None
    assert artifact_title("rag-engineer") == "Roadmap · rag-engineer"
    assert artifact_title(None) == "Roadmap"


def test_persist_creates_artifact_with_public_id() -> None:
    external_id = "forge-artifact-user-a"
    event = {"type": "graph_ready", "graph": _sample_nodes()}
    artifact = persist_graph_ready(
        external_id,
        event,
        graph_run_id="run-car24-1",
        goal_id="rag-engineer",
    )
    assert artifact is not None
    assert artifact.is_active is True
    assert artifact.graph_run_id == "run-car24-1"
    assert artifact.goal_id == "rag-engineer"
    assert artifact.title == "Roadmap · rag-engineer"
    assert artifact.public_id is not None
    assert isinstance(artifact.id, int)
    assert len(artifact.snapshot) == 2
    for raw in artifact.snapshot:
        UserSkillNode.model_validate(raw)


def test_second_forge_deactivates_previous() -> None:
    external_id = "forge-artifact-user-b"
    nodes = _sample_nodes()
    first = persist_graph_ready(
        external_id,
        {"type": "graph_ready", "graph": nodes},
        graph_run_id="run-car24-2a",
        goal_id="rag-engineer",
    )
    second = persist_graph_ready(
        external_id,
        {"type": "graph_ready", "graph": nodes},
        graph_run_id="run-car24-2b",
        goal_id="agent-engineer",
    )
    assert first is not None and second is not None
    assert second.is_active is True

    with SessionLocal() as session:
        rows = list(
            session.scalars(
                select(ForgeArtifact).where(
                    ForgeArtifact.graph_run_id.in_(["run-car24-2a", "run-car24-2b"]),
                ),
            ),
        )
        by_run = {row.graph_run_id: row for row in rows}
        assert by_run["run-car24-2a"].is_active is False
        assert by_run["run-car24-2b"].is_active is True


def test_same_graph_run_id_upserts_not_duplicate() -> None:
    external_id = "forge-artifact-user-c"
    event = {"type": "graph_ready", "graph": _sample_nodes()}
    first = persist_graph_ready(
        external_id,
        event,
        graph_run_id="run-car24-3",
        goal_id="rag-engineer",
    )
    second = persist_graph_ready(
        external_id,
        event,
        graph_run_id="run-car24-3",
        goal_id="llm-evals",
    )
    assert first is not None and second is not None
    assert first.id == second.id
    assert second.goal_id == "llm-evals"
    assert second.title == "Roadmap · llm-evals"

    with SessionLocal() as session:
        count = len(
            list(
                session.scalars(
                    select(ForgeArtifact).where(ForgeArtifact.graph_run_id == "run-car24-3"),
                ),
            ),
        )
        assert count == 1
