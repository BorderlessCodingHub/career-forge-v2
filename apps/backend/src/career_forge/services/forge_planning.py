"""Study-plan draft and evaluation helpers for Roadmap Forge."""

from __future__ import annotations

from typing import Any

from career_forge.ai.tools.study_plan_evaluator import StudyPlanEvaluator
from career_forge.schemas.common import Priority, SkillStatus, UserSkillNode
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanEvaluation,
    StudyPlanNode,
    StudyPlanTask,
    StudyResource,
)
from career_forge.services.forge_context import LearnerForgeContext


def build_draft_study_plan(
    *,
    context: LearnerForgeContext,
    diagnosis: DiagnosisResponse,
    graph: list[UserSkillNode],
    research_events: list[dict[str, Any]],
) -> StudyPlan:
    """Create a draft plan that the evaluator can critique."""
    resources = _resources_from_research_events(research_events)
    nodes = [
        StudyPlanNode(
            node_id=node.node_id,
            title=node.title or node.node_id,
            why_now=node.rationale or "Parte da trilha inicial para o objetivo escolhido.",
            prerequisites=[],
            tasks=[
                StudyPlanTask(
                    title=f"Estudar {node.title or node.node_id}",
                    outcome=f"Explicar e aplicar {node.title or node.node_id} em um exercício.",
                    evidence_prompt="Publique uma evidência prática ou responda uma entrevista curta.",
                ),
            ],
            resources=resources[:3],
        )
        for node in graph
        if node.status != SkillStatus.APROVADO
    ]
    return StudyPlan(
        goal=context.goal_id,
        learner_context_summary=context.compact_summary(),
        strategy=(
            "Começar por fundamentos e prática guiada, conectando habilidades "
            "transferíveis a projetos pequenos com evidência verificável."
        ),
        nodes=nodes or [_starter_node(resources)],
    )


async def evaluate_study_plan_event(
    plan: StudyPlan,
    evaluator: StudyPlanEvaluator,
) -> dict[str, Any]:
    evaluation = await evaluator.evaluate(plan)
    return evaluation_artifact(evaluation)


def evaluation_artifact(evaluation: StudyPlanEvaluation) -> dict[str, Any]:
    if evaluation.verdict == "ship":
        detail = "Avaliador aprovou a estrutura inicial do plano."
    else:
        changes = "; ".join(evaluation.required_changes[:3] or evaluation.gaps[:3])
        detail = f"Avaliador pediu revisão: {changes}"
    return {
        "type": "artifact_found",
        "label": f"Avaliador do plano: {evaluation.verdict}",
        "detail": detail,
    }


def study_plan_to_graph(plan: StudyPlan) -> list[UserSkillNode]:
    """Convert approved StudyPlan nodes into the graph_ready UI contract."""
    graph: list[UserSkillNode] = []
    for index, node in enumerate(plan.nodes):
        graph.append(
            UserSkillNode(
                node_id=node.node_id,
                title=node.title,
                status=SkillStatus.RECOMENDADO if index == 0 else SkillStatus.BLOQUEADO,
                mastery_score=0,
                priority=_priority_for_index(index),
                rationale=node.why_now,
                prerequisites=node.prerequisites,
                tasks=[
                    {
                        "title": task.title,
                        "outcome": task.outcome,
                        "evidence_prompt": task.evidence_prompt,
                    }
                    for task in node.tasks
                ],
                references=[
                    {
                        "title": resource.title,
                        "url": resource.url,
                        "snippet": resource.snippet,
                        "source_type": resource.source_type,
                    }
                    for resource in node.resources
                ],
            ),
        )
    return graph


def _resources_from_research_events(events: list[dict[str, Any]]) -> list[StudyResource]:
    resources: list[StudyResource] = []
    seen: set[str] = set()
    for event in events:
        for source in event.get("sources") or []:
            url = source.get("url")
            if not url or url in seen:
                continue
            seen.add(url)
            resources.append(
                StudyResource(
                    title=source.get("title") or url,
                    url=url,
                    snippet=source.get("snippet") or "",
                ),
            )
    return resources


def _priority_for_index(index: int) -> Priority:
    if index == 0:
        return Priority.HIGH
    if index <= 2:
        return Priority.MEDIUM
    return Priority.LOW


def _starter_node(resources: list[StudyResource]) -> StudyPlanNode:
    return StudyPlanNode(
        node_id="starter",
        title="Primeiro projeto prático",
        why_now="O diagnóstico precisa de evidência hands-on.",
        tasks=[
            StudyPlanTask(
                title="Criar um mini-projeto",
                outcome="Demonstrar prática mínima no objetivo escolhido.",
                evidence_prompt="Mostre código, README ou explicação do que aprendeu.",
            ),
        ],
        resources=resources[:3],
    )
