"""Roadmap catalog and user graph persistence — HAC-9."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.skill_node import SkillNode
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.roadmap import (
    RoadmapCategory,
    RoadmapNode,
    RoadmapResponse,
    RoadmapTrack,
)

REPO_ROOT = Path(__file__).resolve().parents[5]
ROADMAP_PATH = REPO_ROOT / "data" / "roadmap.json"

DEFAULT_DEMO_STATE: dict[str, dict[str, Any]] = {
    "js": {"status": "aprovado", "mastery_score": 65, "priority": "low"},
    "git": {"status": "aprovado", "mastery_score": 78, "priority": "low"},
    "http": {
        "status": "recomendado",
        "mastery_score": 42,
        "priority": "high",
        "rationale": "Lacuna principal — foco do onboarding",
    },
    "db": {"status": "recomendado", "mastery_score": 35, "priority": "high"},
    "rest": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "auth": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "final": {"status": "bloqueado", "mastery_score": 0, "priority": None},
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
    if user_row is not None:
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
    nodes = [
        _merge_node(node, state_by_node.get(node["id"]), None)
        for node in sorted(catalog["nodes"], key=lambda n: n.get("sort_order", 0))
    ]
    return RoadmapResponse(
        track=RoadmapTrack.model_validate(track),
        categories=[RoadmapCategory.model_validate(c) for c in catalog["categories"]],
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
    for node in nodes:
        row = existing.get(node.node_id)
        payload = {
            "status": node.status.value if isinstance(node.status, SkillStatus) else node.status,
            "mastery_score": node.mastery_score,
            "priority": node.priority.value if node.priority else None,
            "rationale": node.rationale,
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
