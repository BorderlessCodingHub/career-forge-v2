"""Forge artifact catalog — list + open with freeze-before-promote (CAR-25)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.models.skill_node import SkillNode
from career_forge.db.repositories.user import ensure_user, get_by_external_id
from career_forge.errors import NotFoundError
from career_forge.schemas.common import UserSkillNode
from career_forge.schemas.roadmap import (
    RoadmapCategory,
    RoadmapNode,
    RoadmapResponse,
    RoadmapTrack,
)
from career_forge.services.roadmap import get_user_roadmap, sync_user_graph
from career_forge.services.roadmap.catalog import load_roadmap_catalog


class ForgeArtifactNotFoundError(NotFoundError):
    """Artifact missing or not owned by the caller."""


def _persistable_checklist_items(items: list[dict]) -> list[dict[str, str]]:
    return [
        {
            str(key): str(value)
            for key, value in item.items()
            if key != "done" and value is not None
        }
        for item in items
    ]


def live_user_skill_nodes(session: Session, external_id: str) -> list[UserSkillNode]:
    """Rebuild snapshot-shaped nodes from the live roadmap (includes post-forge progress)."""
    roadmap = get_user_roadmap(session, external_id)
    node_ids = [node.node_id for node in roadmap.nodes]
    concepts_by_id: dict[str, list[str]] = {}
    if node_ids:
        rows = session.scalars(select(SkillNode).where(SkillNode.id.in_(node_ids))).all()
        concepts_by_id = {row.id: list(row.key_concepts or []) for row in rows}
    return [
        UserSkillNode(
            node_id=node.node_id,
            title=node.title,
            status=node.status,
            mastery_score=node.mastery_score,
            priority=node.priority,
            rationale=node.rationale,
            prerequisites=list(node.prerequisites or []),
            key_concepts=concepts_by_id.get(node.node_id, []),
            tasks=_persistable_checklist_items(node.tasks),
            references=_persistable_checklist_items(node.references),
        )
        for node in roadmap.nodes
    ]


def list_forges(session: Session, external_id: str) -> list[ForgeArtifact]:
    user = get_by_external_id(session, external_id)
    if user is None:
        return []
    return list(
        session.scalars(
            select(ForgeArtifact)
            .where(ForgeArtifact.user_id == user.id)
            .order_by(ForgeArtifact.created_at.desc(), ForgeArtifact.id.desc()),
        ),
    )


def open_forge(
    session: Session,
    external_id: str,
    public_id: uuid.UUID,
) -> RoadmapResponse:
    """Freeze current active artifact from live graph, then promote target snapshot."""
    user = ensure_user(session, external_id)
    target = session.scalar(
        select(ForgeArtifact).where(
            ForgeArtifact.public_id == public_id,
            ForgeArtifact.user_id == user.id,
        ),
    )
    if target is None:
        raise ForgeArtifactNotFoundError("Forge artifact not found")

    if target.is_active:
        return get_user_roadmap(session, external_id)

    active = session.scalar(
        select(ForgeArtifact).where(
            ForgeArtifact.user_id == user.id,
            ForgeArtifact.is_active.is_(True),
        ),
    )
    if active is not None and active.id != target.id:
        live_nodes = live_user_skill_nodes(session, external_id)
        if live_nodes:
            active.snapshot = [n.model_dump(mode="json") for n in live_nodes]

    session.execute(
        update(ForgeArtifact)
        .where(ForgeArtifact.user_id == user.id, ForgeArtifact.is_active.is_(True))
        .values(is_active=False),
    )

    nodes = [UserSkillNode.model_validate(raw) for raw in target.snapshot]
    roadmap = sync_user_graph(session, external_id, nodes, commit=False)
    target.is_active = True
    session.commit()
    return roadmap


def artifact_summary(row: ForgeArtifact) -> dict[str, object]:
    """Serialize list DTO fields (no snapshot, no serial id)."""
    created: datetime = row.created_at
    return {
        "public_id": row.public_id,
        "goal_id": row.goal_id,
        "title": row.title,
        "is_active": row.is_active,
        "created_at": created,
        "graph_run_id": row.graph_run_id,
    }


def roadmap_from_snapshot(artifact: ForgeArtifact) -> RoadmapResponse:
    """Build a read-only RoadmapResponse from an artifact snapshot (no promote)."""
    catalog = load_roadmap_catalog(artifact.goal_id)
    track = RoadmapTrack.model_validate(catalog["track"])
    user_nodes = [UserSkillNode.model_validate(raw) for raw in artifact.snapshot]
    nodes: list[RoadmapNode] = []
    for index, node in enumerate(user_nodes):
        tasks = [
            {
                **{k: v for k, v in item.items() if v is not None},
                "id": item.get("id") or f"task-{i}",
                "done": bool(item.get("done", False)),
            }
            for i, item in enumerate(node.tasks)
        ]
        references = [
            {
                **{k: v for k, v in item.items() if v is not None},
                "id": item.get("id") or f"ref-{i}",
                "done": bool(item.get("done", False)),
            }
            for i, item in enumerate(node.references)
        ]
        completed = sum(1 for item in [*tasks, *references] if item.get("done"))
        nodes.append(
            RoadmapNode(
                node_id=node.node_id,
                title=node.title or node.node_id,
                category="ai_generated",
                description=node.rationale or "",
                icon="sparkles",
                side="left" if index % 2 == 0 else "right",
                sort_order=index,
                prerequisites=list(node.prerequisites or []),
                outcomes=[
                    str(t.get("outcome", ""))
                    for t in node.tasks
                    if t.get("outcome")
                ],
                rubric=[
                    str(t.get("evidence_prompt", ""))
                    for t in node.tasks
                    if t.get("evidence_prompt")
                ],
                status=node.status,
                mastery_score=node.mastery_score,
                priority=node.priority,
                rationale=node.rationale,
                tasks=tasks,
                references=references,
                checklist_completed=completed,
                checklist_total=len(tasks) + len(references),
            ),
        )
    return RoadmapResponse(
        track=track,
        categories=[RoadmapCategory(id="ai_generated", label="Plano gerado por IA")],
        nodes=nodes,
    )
