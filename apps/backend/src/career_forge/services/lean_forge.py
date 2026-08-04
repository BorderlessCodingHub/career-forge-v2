"""Lean forge prune — must-haves ∩ catalog + one foundation hop (CAR-15)."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from career_forge.paths import (
    GOAL_TO_CATALOG_TRACK,
    must_haves_dir,
    normalize_catalog_track_id,
)
from career_forge.services.roadmap.catalog import load_roadmap_catalog

logger = logging.getLogger(__name__)


def load_must_have_ids(goal_id: str, *, directory: Path | None = None) -> list[str]:
    """Load machine-readable must-have ids for a goal (frozen set, CAR-17)."""
    root = directory if directory is not None else must_haves_dir()
    path = root / f"{goal_id}.json"
    if not path.is_file():
        # Legacy goal aliases share rag-engineer must-haves
        mapped = GOAL_TO_CATALOG_TRACK.get(goal_id)
        if mapped and mapped.startswith("rag-engineer"):
            path = root / "rag-engineer.json"
        if not path.is_file():
            logger.warning("must-haves file missing for goal_id=%s path=%s", goal_id, path)
            return []

    payload = json.loads(path.read_text(encoding="utf-8"))
    ids = payload.get("ids") or []
    return [str(node_id) for node_id in ids if isinstance(node_id, str) and node_id.strip()]


def compute_lean_allowlist(
    goal_id: str,
    track_id: str | None,
    *,
    must_have_ids: list[str] | None = None,
    catalog: dict[str, Any] | None = None,
) -> set[str]:
    """Must-haves present in catalog ∪ direct ``prerequisites`` (one foundation layer)."""
    resolved_track = normalize_catalog_track_id(track_id)
    catalog_data = catalog if catalog is not None else load_roadmap_catalog(resolved_track)
    nodes = catalog_data.get("nodes") or []
    by_id = {str(node["id"]): node for node in nodes if "id" in node}
    catalog_ids = set(by_id)

    seeds = must_have_ids if must_have_ids is not None else load_must_have_ids(goal_id)
    must_in_catalog = {node_id for node_id in seeds if node_id in catalog_ids}

    allowlist = set(must_in_catalog)
    for node_id in must_in_catalog:
        prereqs = by_id[node_id].get("prerequisites") or []
        for prereq in prereqs:
            if prereq in catalog_ids:
                allowlist.add(str(prereq))

    return allowlist


def apply_lean_forge_input(forge_input: dict[str, Any]) -> dict[str, Any]:
    """Attach must-have ids + soft-gate lean allowlist to forge GraphRun input.

    Always sets ``must_have_node_ids`` (CAR-17 bias). When soft-gated, also sets
    ``lean_allowed_node_ids``. Empty allowlist while soft-gated → fail-open
    (no lean_allowed_node_ids).
    """
    from career_forge.schemas.diagnosis import DiagnosisResponse
    from career_forge.services.soft_gate import (
        diagnosis_dump_for_persist,
        evaluate_soft_gate,
    )

    raw_diagnosis = forge_input.get("diagnosis")
    if not isinstance(raw_diagnosis, dict):
        return forge_input

    diagnosis = DiagnosisResponse.model_validate(raw_diagnosis)
    decision = evaluate_soft_gate(diagnosis)

    merged = dict(forge_input)
    # Soft-gate fields on diagnosis for GraphRun audit; score presence via dump helper.
    diagnosis_payload = diagnosis_dump_for_persist(diagnosis)
    diagnosis_payload["soft_gated"] = decision.soft_gated
    diagnosis_payload["soft_gate_warning"] = decision.soft_gate_warning
    merged["diagnosis"] = diagnosis_payload
    merged["soft_gated"] = decision.soft_gated
    if decision.soft_gate_warning:
        merged["soft_gate_warning"] = decision.soft_gate_warning
    else:
        merged.pop("soft_gate_warning", None)

    goal_id = forge_input.get("goal_id")
    if not goal_id:
        goal_id = _goal_from_track(diagnosis.profile.track_id)
    else:
        goal_id = str(goal_id)

    must_ids = load_must_have_ids(goal_id)
    if must_ids:
        merged["must_have_node_ids"] = list(must_ids)
    else:
        merged.pop("must_have_node_ids", None)

    if not decision.soft_gated:
        merged.pop("lean_allowed_node_ids", None)
        return merged

    allowlist = compute_lean_allowlist(goal_id, diagnosis.profile.track_id)
    if not allowlist:
        logger.warning(
            "soft_gated but lean allowlist empty for goal_id=%s — fail-open full catalog",
            goal_id,
        )
        merged.pop("lean_allowed_node_ids", None)
        return merged

    merged["lean_allowed_node_ids"] = sorted(allowlist)
    return merged


def _goal_from_track(track_id: str) -> str:
    for goal, track in GOAL_TO_CATALOG_TRACK.items():
        if track == track_id and not goal.startswith(("backend", "data", "frontend")):
            return goal
    return track_id.removesuffix("-beginner")


def resolve_lean_allowed_node_ids(input_data: dict[str, Any]) -> set[str] | None:
    """Return allowlist when lean prune is active; else None (full catalog)."""
    if not input_data.get("soft_gated"):
        return None
    ids = input_data.get("lean_allowed_node_ids")
    if not ids:
        return None
    return {str(node_id) for node_id in ids}
