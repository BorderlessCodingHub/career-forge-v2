"""Roadmap catalog and user graph persistence — HAC-9."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.skill_node import SkillNode
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.paths import roadmap_json_path
from career_forge.schemas.roadmap import (
    RoadmapCategory,
    RoadmapNode,
    RoadmapResponse,
    RoadmapTrack,
)

ROADMAP_PATH = roadmap_json_path()

from career_forge.demo.ana_state import DEMO_ANA_SKILL_STATE

DEFAULT_DEMO_STATE: dict[str, dict[str, Any]] = {
    node_id: {
        key: value
        for key, value in state.items()
        if key != "evidence"
    }
    for node_id, state in DEMO_ANA_SKILL_STATE.items()
}


def load_roadmap_catalog(path: Path = ROADMAP_PATH) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def _resolve_user(session: Session, external_id: str) -> User | None:
    return session.scalar(select(User).where(User.external_id == external_id))


def _user_state_map(session: Session, user: User) -> dict[str, UserSkillNodeRow]:
    rows = session.scalars(
        select(UserSkillNodeRow).where(UserSkillNodeRow.user_id == user.id),
    ).all()
    return {row.skill_node_id: row for row in rows}


def _merge_node(
    catalog_node: dict[str, Any],
    user_row: UserSkillNodeRow | None,
    fallback: dict[str, Any] | None,
) -> RoadmapNode:
    state = fallback or {}
    evidence: list[dict[str, Any]] = []
    if user_row is not None:
        evidence = user_row.evidence or []
        state = {
            "status": user_row.status,
            "mastery_score": user_row.mastery_score,
            "priority": user_row.priority,
            "rationale": user_row.rationale,
        }

    status = SkillStatus(state.get("status", SkillStatus.BLOQUEADO))
    priority_raw = state.get("priority")
    priority = Priority(priority_raw) if priority_raw else None

    return RoadmapNode(
        node_id=catalog_node["id"],
        title=catalog_node["title"],
        category=catalog_node["category"],
        description=catalog_node.get("description") or "",
        icon=catalog_node.get("icon") or "code",
        side=catalog_node.get("side") or "left",
        sort_order=catalog_node.get("sort_order", 0),
        prerequisites=catalog_node.get("prerequisites") or [],
        outcomes=catalog_node.get("outcomes") or [],
        rubric=catalog_node.get("rubric") or [],
        status=status,
        mastery_score=int(state.get("mastery_score", 0)),
        priority=priority,
        rationale=state.get("rationale"),
        tasks=_evidence_items(evidence, "task"),
        references=_evidence_items(evidence, "reference"),
    )


def build_roadmap_from_catalog(
    user_state: dict[str, dict[str, Any]] | None = None,
) -> RoadmapResponse:
    """File-based fallback when Postgres is unavailable or user has no rows."""
    catalog = load_roadmap_catalog()
    state = user_state or DEFAULT_DEMO_STATE
    track = catalog["track"]
    nodes = [
        _merge_node(node, None, state.get(node["id"]))
        for node in sorted(catalog["nodes"], key=lambda n: n.get("sort_order", 0))
    ]
    return RoadmapResponse(
        track=RoadmapTrack.model_validate(track),
        categories=[RoadmapCategory.model_validate(c) for c in catalog["categories"]],
        nodes=nodes,
    )


def get_user_roadmap(session: Session, user_id: str = "demo-ana") -> RoadmapResponse:
    """Join skill catalog with per-user state from Postgres."""
    catalog = load_roadmap_catalog()
    user = _resolve_user(session, user_id)
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
    user = _resolve_user(session, user_id)
    if user is None:
        user = User(
            external_id=user_id,
            display_name=user_id.replace("-", " ").title(),
            email=f"{user_id}@demo.careerforge.local",
        )
        session.add(user)
        session.flush()

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
                setattr(row, key, value)
        else:
            session.add(
                UserSkillNodeRow(
                    user_id=user.id,
                    skill_node_id=node.node_id,
                    **payload,
                ),
            )

    session.commit()
    return get_user_roadmap(session, user_id)


def _evidence_items(evidence: list[dict[str, Any]], item_type: str) -> list[dict[str, str]]:
    return [
        {str(key): str(value) for key, value in item.items() if key != "type" and value is not None}
        for item in evidence
        if isinstance(item, dict) and item.get("type") == item_type
    ]


def _evidence_from_node(node: UserSkillNode, *, sort_order: int) -> list[dict[str, Any]]:
    return [
        {"type": "metadata", "sort_order": sort_order},
    ] + [
        {"type": "task", **task}
        for task in node.tasks
    ] + [
        {"type": "reference", **reference}
        for reference in node.references
    ]


def _ensure_skill_node(session: Session, node: UserSkillNode, *, sort_order: int) -> None:
    existing = session.get(SkillNode, node.node_id)
    if existing is not None:
        if existing.track_id == "ai-generated":
            existing.title = node.title or node.node_id
            existing.description = node.rationale
            existing.sort_order = sort_order
            existing.prerequisites = node.prerequisites
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
            outcomes=[task.get("outcome", "") for task in node.tasks if task.get("outcome")],
            rubric=[
                task.get("evidence_prompt", "")
                for task in node.tasks
                if task.get("evidence_prompt")
            ],
        ),
    )


def _catalog_node_from_generated_row(
    row: UserSkillNodeRow,
) -> dict[str, Any]:
    evidence = row.evidence or []
    tasks = _evidence_items(evidence, "task")
    sort_order = _generated_row_sort_order(row)
    return {
        "id": row.skill_node_id,
        "title": row.skill_node.title if row.skill_node else row.skill_node_id,
        "category": "ai_generated",
        "description": row.rationale or "",
        "icon": "sparkles",
        "side": "left" if sort_order % 2 == 0 else "right",
        "sort_order": sort_order,
        "prerequisites": row.skill_node.prerequisites if row.skill_node else [],
        "outcomes": [task.get("outcome", "") for task in tasks if task.get("outcome")],
        "rubric": [
            task.get("evidence_prompt", "")
            for task in tasks
            if task.get("evidence_prompt")
        ],
    }


def _generated_row_sort_order(row: UserSkillNodeRow) -> int:
    evidence = row.evidence or []
    for item in evidence:
        if isinstance(item, dict) and item.get("type") == "metadata":
            try:
                return int(item.get("sort_order", 0))
            except (TypeError, ValueError):
                return 0
    if row.skill_node is not None:
        return row.skill_node.sort_order
    return 0
