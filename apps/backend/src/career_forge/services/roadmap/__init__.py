"""Roadmap service facade — re-exports the split modules (HAC-84).

Historically a single 503-LOC module; split into catalog / assembler /
repository / commands. This facade preserves the public import surface
(`from career_forge.services.roadmap import X`) used across services, API
routes and tests, including the private helpers exercised by test_roadmap.
"""

from __future__ import annotations

from career_forge.services.roadmap.assembler import (
    _catalog_node_from_generated_row,
    _checklist_counts,
    _enrich_checklist_items,
    _evidence_from_node,
    _evidence_items,
    _generated_row_sort_order,
    _merge_node,
    _stable_item_id,
    build_roadmap_from_catalog,
    merge_validation_evidence,
)
from career_forge.services.roadmap.catalog import (
    DEFAULT_DEMO_STATE,
    ROADMAP_PATH,
    load_roadmap_catalog,
    resolve_skill_node_catalog_entry,
)
from career_forge.services.roadmap.commands import (
    get_user_roadmap,
    sync_user_graph,
    toggle_checklist_item,
)
from career_forge.services.roadmap.repository import (
    _delete_stale_generated_rows,
    _ensure_skill_node,
    _ensure_user_row_for_catalog_node,
    _user_state_map,
)

__all__ = [
    "DEFAULT_DEMO_STATE",
    "ROADMAP_PATH",
    "build_roadmap_from_catalog",
    "get_user_roadmap",
    "load_roadmap_catalog",
    "merge_validation_evidence",
    "resolve_skill_node_catalog_entry",
    "sync_user_graph",
    "toggle_checklist_item",
]
