"""Roadmap Postgres row access — user/skill node CRUD (HAC-84 split)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.skill_node import SkillNode
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.schemas.common import SkillStatus, UserSkillNode
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.services.roadmap.catalog import load_roadmap_catalog


def _user_state_map(session: Session, user: User) -> dict[str, UserSkillNodeRow]:
    rows = session.scalars(
        select(UserSkillNodeRow).where(UserSkillNodeRow.user_id == user.id),
    ).all()
    return {row.skill_node_id: row for row in rows}


def _delete_stale_generated_rows(
    session: Session,
    existing: dict[str, UserSkillNodeRow],
    incoming_ids: set[str],
) -> None:
    for node_id, row in existing.items():
        if node_id in incoming_ids:
            continue
        if row.skill_node and row.skill_node.track_id == "ai-generated":
            session.delete(row)


def _ensure_skill_node(session: Session, node: UserSkillNode, *, sort_order: int) -> None:
    existing = session.get(SkillNode, node.node_id)
    if existing is not None:
        if existing.track_id == "ai-generated":
            existing.title = node.title or node.node_id
            existing.description = node.rationale
            existing.sort_order = sort_order
            existing.prerequisites = node.prerequisites
            existing.key_concepts = list(node.key_concepts or [])
            existing.outcomes = [
                task.get("outcome", "") for task in node.tasks if task.get("outcome")
            ]
            existing.rubric = [
                task.get("evidence_prompt", "")
                for task in node.tasks
                if task.get("evidence_prompt")
            ]
        return
    session.add(
        SkillNode(
            id=node.node_id,
            track_id="ai-generated",
            title=node.title or node.node_id,
            category="ai_generated",
            description=node.rationale,
            icon="sparkles",
            side="left" if sort_order % 2 == 0 else "right",
            sort_order=sort_order,
            prerequisites=node.prerequisites,
            key_concepts=list(node.key_concepts or []),
            outcomes=[task.get("outcome", "") for task in node.tasks if task.get("outcome")],
            rubric=[
                task.get("evidence_prompt", "")
                for task in node.tasks
                if task.get("evidence_prompt")
            ],
        ),
    )


def _ensure_user_row_for_catalog_node(
    session: Session,
    user: User,
    node_id: str,
    roadmap: RoadmapResponse,
) -> UserSkillNodeRow:
    node = next(item for item in roadmap.nodes if item.node_id == node_id)
    catalog = load_roadmap_catalog(roadmap.track.id if roadmap.track else None)
    catalog_node = next(
        (item for item in catalog["nodes"] if item["id"] == node_id),
        None,
    )
    if catalog_node is not None:
        _ensure_skill_node(
            session,
            UserSkillNode(
                node_id=node_id,
                title=node.title,
                status=node.status,
                mastery_score=node.mastery_score,
                priority=node.priority,
                rationale=node.rationale,
                prerequisites=node.prerequisites,
            ),
            sort_order=catalog_node.get("sort_order", 0),
        )
    row = UserSkillNodeRow(
        user_id=user.id,
        skill_node_id=node_id,
        status=node.status.value if isinstance(node.status, SkillStatus) else node.status,
        mastery_score=node.mastery_score,
        priority=node.priority.value if node.priority else None,
        rationale=node.rationale,
        evidence=[],
        checklist_progress={},
    )
    session.add(row)
    session.flush()
    return row
