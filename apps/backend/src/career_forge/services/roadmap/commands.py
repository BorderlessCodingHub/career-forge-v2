"""Roadmap commands — read, sync and checklist toggle orchestration (HAC-84 split)."""

from __future__ import annotations

from typing import Literal

from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.repositories.user import ensure_user, get_by_external_id
from career_forge.errors import ChecklistItemNotFoundError, NodeNotFoundError
from career_forge.schemas.common import SkillStatus, UserSkillNode
from career_forge.schemas.roadmap import RoadmapCategory, RoadmapResponse, RoadmapTrack
from career_forge.services.roadmap.assembler import (
    _catalog_node_from_generated_row,
    _evidence_from_node,
    _generated_row_sort_order,
    _merge_node,
    build_roadmap_from_catalog,
)
from career_forge.services.roadmap.catalog import load_roadmap_catalog
from career_forge.services.roadmap.repository import (
    _delete_stale_generated_rows,
    _ensure_skill_node,
    _ensure_user_row_for_catalog_node,
    _user_state_map,
)


def get_user_roadmap(session: Session, user_id: str = "demo-ana") -> RoadmapResponse:
    """Join skill catalog with per-user state from Postgres."""
    catalog = load_roadmap_catalog()
    user = get_by_external_id(session, user_id)
    if user is None:
        return build_roadmap_from_catalog()

    state_by_node = _user_state_map(session, user)
    if not state_by_node:
        return build_roadmap_from_catalog()

    track = catalog["track"]
    catalog_nodes = sorted(catalog["nodes"], key=lambda n: n.get("sort_order", 0))
    catalog_ids = {node["id"] for node in catalog_nodes}
    generated_rows = [
        row for node_id, row in state_by_node.items() if node_id not in catalog_ids
    ]
    generated_nodes = [
        _catalog_node_from_generated_row(row)
        for row in sorted(generated_rows, key=_generated_row_sort_order)
    ]
    if generated_nodes:
        nodes = [
            _merge_node(node, state_by_node.get(node["id"]), None)
            for node in generated_nodes
        ]
        categories = [RoadmapCategory(id="ai_generated", label="Plano gerado por IA")]
    else:
        nodes = [
            _merge_node(node, state_by_node.get(node["id"]), None)
            for node in catalog_nodes
        ]
        categories = [RoadmapCategory.model_validate(c) for c in catalog["categories"]]
    return RoadmapResponse(
        track=RoadmapTrack.model_validate(track),
        categories=categories,
        nodes=nodes,
    )


def sync_user_graph(
    session: Session,
    user_id: str,
    nodes: list[UserSkillNode],
) -> RoadmapResponse:
    """Upsert forge graph into user_skill_nodes and return merged roadmap."""
    user = ensure_user(session, user_id)

    existing = _user_state_map(session, user)
    incoming_ids = {node.node_id for node in nodes}
    if any(node.node_id not in existing for node in nodes):
        _delete_stale_generated_rows(session, existing, incoming_ids)
        existing = _user_state_map(session, user)
    for index, node in enumerate(nodes, start=len(existing)):
        _ensure_skill_node(session, node, sort_order=index)
        row = existing.get(node.node_id)
        payload = {
            "status": node.status.value if isinstance(node.status, SkillStatus) else node.status,
            "mastery_score": node.mastery_score,
            "priority": node.priority.value if node.priority else None,
            "rationale": node.rationale,
            "evidence": _evidence_from_node(node, sort_order=index),
        }
        if row:
            for key, value in payload.items():
                if key == "checklist_progress":
                    continue
                setattr(row, key, value)
        else:
            session.add(
                UserSkillNodeRow(
                    user_id=user.id,
                    skill_node_id=node.node_id,
                    checklist_progress={},
                    **payload,
                ),
            )

    session.commit()
    return get_user_roadmap(session, user_id)


def toggle_checklist_item(
    session: Session,
    user_id: str,
    node_id: str,
    item_type: Literal["task", "reference"],
    item_id: str,
    done: bool,
) -> RoadmapResponse:
    """Persist lightweight checklist progress for a single task or reference item."""
    user = ensure_user(session, user_id)

    roadmap = get_user_roadmap(session, user_id)
    node = next((item for item in roadmap.nodes if item.node_id == node_id), None)
    if node is None:
        raise NodeNotFoundError(f"Node {node_id} not found")

    items = node.tasks if item_type == "task" else node.references
    if not any(str(item.get("id")) == item_id for item in items):
        raise ChecklistItemNotFoundError(
            f"Unknown {item_type} item_id {item_id} for node {node_id}",
        )

    existing = _user_state_map(session, user)
    row = existing.get(node_id)
    if row is None:
        row = _ensure_user_row_for_catalog_node(session, user, node_id, roadmap)
        existing[node_id] = row

    progress = dict(row.checklist_progress or {})
    bucket_key = "tasks" if item_type == "task" else "references"
    bucket = dict(progress.get(bucket_key) or {})
    bucket[item_id] = done
    progress[bucket_key] = bucket
    row.checklist_progress = progress
    session.commit()
    return get_user_roadmap(session, user_id)
