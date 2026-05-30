"""Build learner + study-block context for MCQ mock interview generation (HAC-65)."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException
from sqlalchemy.orm import Session

from career_forge.services.forge_context import LearnerForgeContext, build_forge_context_from_input
from career_forge.services.profile_diagnosis import load_forge_motor_input
from career_forge.services.roadmap import get_skill_node_context, get_user_roadmap


def _strip_checklist_fields(items: list[dict]) -> list[dict[str, str]]:
    return [
        {str(key): str(value) for key, value in item.items() if key != "done" and value is not None}
        for item in items
    ]


def _open_gap_concepts(session: Session, *, user_id: str, node_id: str) -> list[str]:
    """Unresolved gap concepts for this node — lets the next mock target weak spots (HAC-68)."""
    try:
        from career_forge.services.knowledge_gaps import list_open_gaps

        return [gap.concept for gap in list_open_gaps(session, user_id=user_id, skill_node_id=node_id)]
    except Exception:
        return []


def build_mock_interview_context(
    session: Session,
    *,
    user_id: str,
    node_id: str,
) -> tuple[dict[str, Any], LearnerForgeContext | None]:
    """Return study-block payload + optional learner forge context."""
    node = get_skill_node_context(session, node_id)

    roadmap = get_user_roadmap(session, user_id)
    roadmap_node = next((item for item in roadmap.nodes if item.node_id == node_id), None)
    tasks = _strip_checklist_fields(roadmap_node.tasks if roadmap_node else [])
    references = _strip_checklist_fields(roadmap_node.references if roadmap_node else [])

    open_gaps = _open_gap_concepts(session, user_id=user_id, node_id=node_id)

    study_block = {
        "node_id": node_id,
        "title": node.get("title") or node_id,
        "description": node.get("description") or (roadmap_node.description if roadmap_node else ""),
        "rationale": roadmap_node.rationale if roadmap_node else None,
        "prerequisites": node.get("prerequisites") or [],
        "tasks": tasks,
        "references": references,
        "outcomes": node.get("outcomes") or [],
        "rubric": node.get("rubric") or [],
        "open_gaps": open_gaps,
    }

    learner: LearnerForgeContext | None = None
    try:
        motor_input = load_forge_motor_input(session, user_id)
        learner = build_forge_context_from_input(user_id=user_id, input_data=motor_input)
    except HTTPException:
        learner = None

    return study_block, learner


def format_context_for_prompt(
    study_block: dict[str, Any],
    learner: LearnerForgeContext | None,
) -> str:
    lines = [
        "## Capítulo de estudo",
        f"Título (pode conter logística — extraia o tema técnico): {study_block['title']}",
        f"Descrição: {study_block.get('description') or '—'}",
    ]
    if study_block.get("rationale"):
        lines.append(f"Rationale: {study_block['rationale']}")
    if study_block.get("tasks"):
        lines.append("Tarefas práticas (sinal do conteúdo técnico):")
        for task in study_block["tasks"]:
            title = task.get("title", "Tarefa")
            outcome = task.get("outcome", "")
            evidence = task.get("evidence_prompt", "")
            lines.append(f"- {title} | outcome: {outcome} | evidência: {evidence}")
    if study_block.get("references"):
        lines.append("Referências oficiais (use para ancorar perguntas):")
        for ref in study_block["references"]:
            snippet = ref.get("snippet") or ref.get("description") or ""
            suffix = f" — {snippet}" if snippet else ""
            lines.append(f"- {ref.get('title', 'Ref')} ({ref.get('url', '')}){suffix}")
    if study_block.get("outcomes"):
        lines.append("Outcomes esperados: " + "; ".join(study_block["outcomes"]))
    if study_block.get("open_gaps"):
        lines.extend(
            [
                "",
                "## Lacunas abertas do aluno neste capítulo",
                "Inclua 1-2 perguntas (fase gap_probe) que cubram estes conceitos ainda não dominados:",
                "; ".join(study_block["open_gaps"]),
            ],
        )
    if learner is not None:
        lines.extend(["", "## Perfil do learner", learner.compact_summary()])
    return "\n".join(lines)
