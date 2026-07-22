"""Roadmap catalog I/O + catalog-entry resolution (HAC-9, split HAC-84)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from career_forge.db.models.skill_node import SkillNode
from career_forge.demo.ana_state import DEMO_ANA_SKILL_STATE
from career_forge.paths import DEFAULT_TRACK_ID, list_catalog_paths, roadmap_json_path

ROADMAP_PATH = roadmap_json_path()

DEFAULT_DEMO_STATE: dict[str, dict[str, Any]] = {
    node_id: {
        key: value
        for key, value in state.items()
        if key != "evidence"
    }
    for node_id, state in DEMO_ANA_SKILL_STATE.items()
}


def load_roadmap_catalog(
    track_id: str | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Load one track catalog.

    ``path`` wins when provided (tests). Otherwise resolve via
    ``roadmap_json_path(track_id)`` (default track: rag-engineer-beginner).
    """
    resolved = path if path is not None else roadmap_json_path(track_id)
    with resolved.open(encoding="utf-8") as handle:
        return json.load(handle)


def load_all_catalogs() -> list[dict[str, Any]]:
    """Load every seeded track catalog (for resolve-by-node-id)."""
    catalogs: list[dict[str, Any]] = []
    for catalog_path in list_catalog_paths():
        with catalog_path.open(encoding="utf-8") as handle:
            catalogs.append(json.load(handle))
    return catalogs


def resolve_skill_node_catalog_entry(session: Session | None, node_id: str) -> dict[str, Any]:
    """Resolve a node's question-building context from the static catalog or a
    persisted AI-generated row (`track_id=ai-generated`), so downstream features
    (mock interview, validation) work for both seeded and StudyPlan nodes.
    """
    for catalog in load_all_catalogs():
        for node in catalog.get("nodes", []):
            if node["id"] == node_id:
                return node

    # Fallback: default track only (covers ROADMAP_JSON_PATH single-file mode)
    try:
        for node in load_roadmap_catalog(DEFAULT_TRACK_ID)["nodes"]:
            if node["id"] == node_id:
                return node
    except FileNotFoundError:
        pass

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
