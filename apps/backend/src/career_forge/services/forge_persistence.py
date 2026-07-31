"""Persist Forge output into the user's roadmap state + forge_artifacts (CAR-24)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.schemas.common import UserSkillNode
from career_forge.services.roadmap import sync_user_graph


def extract_goal_id(run_input: dict[str, Any] | None) -> str | None:
    """Pull goal_id from forge GraphRun.input (top-level or nested diagnosis)."""
    if not run_input:
        return None
    raw = run_input.get("goal_id")
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    diagnosis = run_input.get("diagnosis")
    if isinstance(diagnosis, dict):
        nested = diagnosis.get("goal_id")
        if isinstance(nested, str) and nested.strip():
            return nested.strip()
    return None


def artifact_title(goal_id: str | None) -> str:
    if goal_id:
        return f"Roadmap · {goal_id}"
    return "Roadmap"


def _upsert_forge_artifact(
    session: Session,
    *,
    external_user_id: str,
    graph_run_id: str,
    goal_id: str | None,
    nodes: list[UserSkillNode],
) -> ForgeArtifact:
    user = ensure_user(session, external_user_id)
    snapshot = [node.model_dump(mode="json") for node in nodes]
    title = artifact_title(goal_id)

    existing = session.scalar(
        select(ForgeArtifact).where(ForgeArtifact.graph_run_id == graph_run_id),
    )
    if existing is not None:
        existing.snapshot = snapshot
        existing.goal_id = goal_id
        existing.title = title
        if not existing.is_active:
            session.execute(
                update(ForgeArtifact)
                .where(
                    ForgeArtifact.user_id == user.id,
                    ForgeArtifact.is_active.is_(True),
                    ForgeArtifact.id != existing.id,
                )
                .values(is_active=False),
            )
            existing.is_active = True
        return existing

    session.execute(
        update(ForgeArtifact)
        .where(ForgeArtifact.user_id == user.id, ForgeArtifact.is_active.is_(True))
        .values(is_active=False),
    )
    row = ForgeArtifact(
        user_id=user.id,
        graph_run_id=graph_run_id,
        goal_id=goal_id,
        title=title,
        snapshot=snapshot,
        is_active=True,
    )
    session.add(row)
    session.flush()
    return row


def persist_graph_ready(
    user_id: str,
    graph_ready_event: dict[str, Any] | None,
    *,
    graph_run_id: str | None = None,
    goal_id: str | None = None,
) -> ForgeArtifact | None:
    """Persist graph_ready nodes for reload and create/upsert a forge_artifact.

    When ``graph_run_id`` is omitted (legacy callers/tests), only syncs the roadmap.
    """
    if not graph_ready_event or graph_ready_event.get("type") != "graph_ready":
        return None
    raw_nodes = graph_ready_event.get("graph")
    if not isinstance(raw_nodes, list) or not raw_nodes:
        return None

    nodes = [UserSkillNode.model_validate(node) for node in raw_nodes]
    with SessionLocal() as session:
        sync_user_graph(session, user_id, nodes, commit=False)
        if not graph_run_id:
            session.commit()
            return None
        artifact = _upsert_forge_artifact(
            session,
            external_user_id=user_id,
            graph_run_id=graph_run_id,
            goal_id=goal_id,
            nodes=nodes,
        )
        session.commit()
        session.refresh(artifact)
        return artifact
