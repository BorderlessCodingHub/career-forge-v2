"""Roadmap catalog I/O + catalog-entry resolution (HAC-9, split HAC-84)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from career_forge.db.models.skill_node import SkillNode
from career_forge.demo.ana_state import DEMO_ANA_SKILL_STATE
from career_forge.paths import roadmap_json_path

ROADMAP_PATH = roadmap_json_path()

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


def resolve_skill_node_catalog_entry(session: Session | None, node_id: str) -> dict[str, Any]:
    """Resolve a node's question-building context from the static catalog or a
    persisted AI-generated row (`track_id=ai-generated`), so downstream features
    (mock interview, validation) work for both seeded and StudyPlan nodes.
    """
    for node in load_roadmap_catalog()["nodes"]:
        if node["id"] == node_id:
            return node

    if session is not None:
        row = session.get(SkillNode, node_id)
        if row is not None:
            return {
                "id": row.id,
                "title": row.title,
                "category": row.category,
                "description": row.description or "",
                "icon": row.icon or "sparkles",
                "side": row.side or "left",
                "sort_order": row.sort_order,
                "prerequisites": list(row.prerequisites or []),
                "outcomes": list(row.outcomes or []),
                "rubric": list(row.rubric or []),
                "key_concepts": list(row.key_concepts or []),
            }

    msg = f"Unknown skill node: {node_id}"
    raise ValueError(msg)
