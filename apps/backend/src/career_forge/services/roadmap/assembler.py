"""Roadmap DTO assembly — node merge, checklist enrichment, evidence (HAC-84 split)."""

from __future__ import annotations

from typing import Any

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.roadmap import (
    RoadmapCategory,
    RoadmapNode,
    RoadmapResponse,
    RoadmapTrack,
)
from career_forge.services.roadmap.catalog import DEFAULT_DEMO_STATE, load_roadmap_catalog


def _evidence_items(evidence: list[dict[str, Any]], item_type: str) -> list[dict[str, str]]:
    return [
        {str(key): str(value) for key, value in item.items() if key != "type" and value is not None}
        for item in evidence
        if isinstance(item, dict) and item.get("type") == item_type
    ]


def _stable_item_id(item_type: str, index: int) -> str:
    prefix = "task" if item_type == "task" else "ref"
    return f"{prefix}-{index}"


def _enrich_checklist_items(
    items: list[dict[str, str]],
    bucket_key: str,
    checklist_progress: dict[str, Any],
) -> list[dict[str, str | bool]]:
    bucket = checklist_progress.get(bucket_key) or {}
    enriched: list[dict[str, str | bool]] = []
    item_type = "task" if bucket_key == "tasks" else "reference"
    for index, item in enumerate(items):
        item_id = item.get("id") or _stable_item_id(item_type, index)
        done = bool(bucket.get(item_id, False))
        enriched.append({**item, "id": item_id, "done": done})
    return enriched


def _checklist_counts(
    tasks: list[dict[str, str | bool]],
    references: list[dict[str, str | bool]],
) -> tuple[int, int]:
    items = [*tasks, *references]
    total = len(items)
    completed = sum(1 for item in items if item.get("done"))
    return completed, total


def _merge_node(
    catalog_node: dict[str, Any],
    user_row: UserSkillNodeRow | None,
    fallback: dict[str, Any] | None,
) -> RoadmapNode:
    state = fallback or {}
    evidence: list[dict[str, Any]] = []
    checklist_progress: dict[str, Any] = {}
    if user_row is not None:
        evidence = user_row.evidence or []
        checklist_progress = user_row.checklist_progress or {}
        state = {
            "status": user_row.status,
            "mastery_score": user_row.mastery_score,
            "priority": user_row.priority,
            "rationale": user_row.rationale,
        }

    status = SkillStatus(state.get("status", SkillStatus.BLOQUEADO))
    priority_raw = state.get("priority")
    priority = Priority(priority_raw) if priority_raw else None

    tasks = _enrich_checklist_items(_evidence_items(evidence, "task"), "tasks", checklist_progress)
    references = _enrich_checklist_items(
        _evidence_items(evidence, "reference"),
        "references",
        checklist_progress,
    )
    completed, total = _checklist_counts(tasks, references)

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
        tasks=tasks,
        references=references,
        checklist_completed=completed,
        checklist_total=total,
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


def merge_validation_evidence(
    existing: list | dict | None,
    *,
    strengths: list[str],
    gaps: list[str],
    next_action: str,
    mock_interview: bool = False,
) -> list | dict:
    """Persist validation feedback without dropping StudyPlan checklist evidence."""
    summary: dict[str, Any] = {
        "type": "validation",
        "strengths": strengths,
        "gaps": gaps,
        "next_action": next_action,
    }
    if mock_interview:
        summary["mock_interview"] = True

    if isinstance(existing, list):
        kept = [
            item
            for item in existing
            if isinstance(item, dict) and item.get("type") in ("metadata", "task", "reference")
        ]
        return [*kept, summary]

    return {
        "strengths": strengths,
        "gaps": gaps,
        "next_action": next_action,
        **({"mock_interview": True} if mock_interview else {}),
    }


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
