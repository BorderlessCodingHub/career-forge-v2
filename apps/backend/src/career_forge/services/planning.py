"""Adaptive planning after validation — HAC-11."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.forge import GraphPatch, NodePatch
from career_forge.schemas.planning import PlanUpdateResponse, TodayFocus
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.schemas.validation import ValidationResponse
from career_forge.services.graph_state import apply_graph_patch
from career_forge.services.roadmap import get_user_roadmap, load_roadmap_catalog, sync_user_graph


def _catalog_nodes() -> list[dict[str, Any]]:
    return sorted(
        load_roadmap_catalog()["nodes"],
        key=lambda node: node.get("sort_order", 0),
    )


def _dependents(node_id: str, catalog_nodes: list[dict[str, Any]]) -> list[str]:
    return [
        node["id"]
        for node in catalog_nodes
        if node_id in (node.get("prerequisites") or [])
    ]


def _transitive_dependents(node_id: str, catalog_nodes: list[dict[str, Any]]) -> list[str]:
    blocked: list[str] = []
    queue = _dependents(node_id, catalog_nodes)
    while queue:
        current = queue.pop(0)
        if current in blocked:
            continue
        blocked.append(current)
        queue.extend(_dependents(current, catalog_nodes))
    return blocked


def _status_map(nodes: list[UserSkillNode]) -> dict[str, SkillStatus]:
    return {node.node_id: node.status for node in nodes}


def _persistable_checklist_items(items: list[dict]) -> list[dict[str, str]]:
    """Strip UI-only checklist fields (e.g. done) before UserSkillNode validation."""
    return [
        {str(key): str(value) for key, value in item.items() if key != "done" and value is not None}
        for item in items
    ]


def _nodes_meta(current_graph: list[UserSkillNode]) -> list[dict[str, Any]]:
    """Unified node metadata: static catalog plus persisted AI-generated nodes
    from the user's current graph, so dependency math works for both (HAC-64)."""
    catalog_nodes = _catalog_nodes()
    catalog_ids = {node["id"] for node in catalog_nodes}
    meta = [
        {
            "id": node["id"],
            "title": node["title"],
            "prerequisites": node.get("prerequisites") or [],
        }
        for node in catalog_nodes
    ]
    meta.extend(
        {
            "id": node.node_id,
            "title": node.title or node.node_id,
            "prerequisites": list(node.prerequisites or []),
        }
        for node in current_graph
        if node.node_id not in catalog_ids
    )
    return meta


def _roadmap_to_graph(roadmap: RoadmapResponse) -> list[UserSkillNode]:
    return [
        UserSkillNode(
            node_id=node.node_id,
            title=node.title,
            status=node.status,
            mastery_score=node.mastery_score,
            priority=node.priority,
            rationale=node.rationale,
            prerequisites=node.prerequisites,
            tasks=_persistable_checklist_items(node.tasks),
            references=_persistable_checklist_items(node.references),
        )
        for node in roadmap.nodes
    ]


def build_adaptive_patch(
    node_id: str,
    validation: ValidationResponse,
    current_graph: list[UserSkillNode],
) -> GraphPatch:
    """Build deterministic GraphPatch from validation outcome."""
    nodes_meta = _nodes_meta(current_graph)
    meta_by_id = {node["id"]: node for node in nodes_meta}
    status_by_id = _status_map(current_graph)
    current_by_id = {node.node_id: node for node in current_graph}

    failed_node = meta_by_id.get(node_id)
    if failed_node is None:
        existing = current_by_id.get(node_id)
        failed_node = {
            "id": node_id,
            "title": existing.title if existing and existing.title else node_id,
            "prerequisites": [],
        }

    patches: list[NodePatch] = []
    passed = validation.status.value == SkillStatus.APROVADO.value

    if passed:
        status_by_id[node_id] = SkillStatus.APROVADO
        patches.append(
            NodePatch(
                node_id=node_id,
                status=SkillStatus.APROVADO,
                mastery_estimated=validation.score,
                priority=Priority.LOW,
                rationale="Mastery validado — seguir para próximo tópico",
            ),
        )

        for node in nodes_meta:
            if node["id"] == node_id:
                continue
            prereqs = node.get("prerequisites") or []
            if not prereqs:
                continue
            if status_by_id.get(node["id"]) == SkillStatus.APROVADO:
                continue
            if not all(status_by_id.get(prereq) == SkillStatus.APROVADO for prereq in prereqs):
                continue
            if status_by_id.get(node["id"]) != SkillStatus.BLOQUEADO:
                continue

            existing = current_by_id.get(node["id"])
            patches.append(
                NodePatch(
                    node_id=node["id"],
                    status=SkillStatus.VALIDAR,
                    mastery_estimated=existing.mastery_score if existing else 0,
                    priority=Priority.HIGH,
                    rationale=f"Pré-requisitos concluídos — validar {node['title']}",
                ),
            )
            break

        summary = f"{failed_node['title']} aprovado — trilha liberou próximo nó."
    else:
        patches.append(
            NodePatch(
                node_id=node_id,
                status=SkillStatus.REVISAR,
                mastery_estimated=validation.score,
                priority=Priority.HIGH,
                rationale=validation.gaps[0] if validation.gaps else validation.next_action,
            ),
        )

        for dependent_id in _transitive_dependents(node_id, nodes_meta):
            dependent = meta_by_id[dependent_id]
            existing = current_by_id.get(dependent_id)
            patches.append(
                NodePatch(
                    node_id=dependent_id,
                    status=SkillStatus.BLOQUEADO,
                    mastery_estimated=existing.mastery_score if existing else 0,
                    priority=Priority.LOW,
                    rationale=f"Bloqueado até revisar {failed_node['title']}",
                ),
            )

        summary = (
            f"Falha em {failed_node['title']} — trilha repriorizou revisão "
            f"e bloqueou {len(_transitive_dependents(node_id, nodes_meta))} nós dependentes."
        )

    return GraphPatch(
        patches=patches,
        continue_research=not passed,
        summary=summary,
    )


def build_plan_update(
    node_id: str,
    node_title: str,
    validation: ValidationResponse,
) -> PlanUpdateResponse:
    """Mission banner payload after graph adapts."""
    failed = validation.status.value == SkillStatus.REVISAR.value
    duration = 45 if failed else 30
    objective = validation.next_action
    if failed and validation.gaps:
        objective = f"{validation.gaps[0]} — {validation.next_action}"

    return PlanUpdateResponse(
        today_focus=TodayFocus(
            node_id=node_id,
            title=node_title,
            duration_minutes=duration,
            objective=objective,
        ),
        next_mission=f"{node_title} — {objective[:72].rstrip()}…"
        if len(objective) > 72
        else f"{node_title} — {objective}",
    )


def _apply_graph_to_roadmap(
    roadmap: RoadmapResponse,
    updated_graph: list[UserSkillNode],
) -> RoadmapResponse:
    updated_by_id = {node.node_id: node for node in updated_graph}
    updated_nodes = []
    for node in roadmap.nodes:
        updated = updated_by_id.get(node.node_id)
        if updated is None:
            updated_nodes.append(node)
            continue
        updated_nodes.append(
            node.model_copy(
                update={
                    "status": updated.status,
                    "mastery_score": updated.mastery_score,
                    "priority": updated.priority.value if updated.priority else None,
                    "rationale": updated.rationale,
                    "tasks": updated.tasks,
                    "references": updated.references,
                },
            ),
        )
    return roadmap.model_copy(update={"nodes": updated_nodes})


def recalibrate_from_catalog(
    node_id: str,
    node_title: str,
    validation: ValidationResponse,
) -> tuple[RoadmapResponse, GraphPatch, PlanUpdateResponse]:
    """In-memory adaptive recalibration when Postgres is unavailable."""
    from career_forge.services.roadmap import build_roadmap_from_catalog

    roadmap = build_roadmap_from_catalog()
    graph = _roadmap_to_graph(roadmap)
    patch = build_adaptive_patch(node_id, validation, graph)
    updated_graph = apply_graph_patch(graph, patch)
    updated_roadmap = _apply_graph_to_roadmap(roadmap, updated_graph)
    plan = build_plan_update(node_id, node_title, validation)
    return updated_roadmap, patch, plan


def recalibrate_after_validation(
    session: Session,
    user_id: str,
    node_id: str,
    node_title: str,
    validation: ValidationResponse,
) -> tuple[RoadmapResponse, GraphPatch, PlanUpdateResponse]:
    """Apply adaptive GraphPatch after validation and persist user graph."""
    try:
        roadmap = get_user_roadmap(session, user_id)
        graph = _roadmap_to_graph(roadmap)
        patch = build_adaptive_patch(node_id, validation, graph)
        updated_graph = apply_graph_patch(graph, patch)
        updated_roadmap = sync_user_graph(session, user_id, updated_graph)
        plan = build_plan_update(node_id, node_title, validation)
        return updated_roadmap, patch, plan
    except Exception:
        session.rollback()
        return recalibrate_from_catalog(node_id, node_title, validation)
