"""Study-plan planner/reviser agent for Roadmap Forge."""

from __future__ import annotations

import asyncio
import os
from typing import Any, Protocol

from langchain_openai import ChatOpenAI

from career_forge.schemas.study_plan import StudyPlan, StudyPlanEvaluation
from career_forge.services.forge_context import LearnerForgeContext


class StudyPlanPlanner(Protocol):
    async def create_plan(
        self,
        *,
        context: LearnerForgeContext,
        research_events: list[dict[str, Any]],
    ) -> StudyPlan:
        """Create an initial study plan from learner context + research."""

    async def revise_plan(
        self,
        *,
        context: LearnerForgeContext,
        research_events: list[dict[str, Any]],
        plan: StudyPlan,
        evaluation: StudyPlanEvaluation,
    ) -> StudyPlan:
        """Revise a study plan using evaluator feedback."""


class OpenAiStudyPlanPlanner:
    """Planner model that creates/revises StudyPlan with structured output."""

    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        resolved_key = (
            api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        ).strip()
        if not resolved_key:
            msg = "OPENAI_API_KEY não configurada. Configure a chave antes de planejar o forge."
            raise RuntimeError(msg)
        self._model = model or os.getenv("FORGE_PLANNER_MODEL", "gpt-5.4")
        self._llm = ChatOpenAI(model=self._model, api_key=resolved_key, temperature=0.2)

    async def create_plan(
        self,
        *,
        context: LearnerForgeContext,
        research_events: list[dict[str, Any]],
    ) -> StudyPlan:
        return await asyncio.to_thread(
            self._invoke_plan,
            context=context,
            research_events=research_events,
            feedback=None,
            previous_plan=None,
        )

    async def revise_plan(
        self,
        *,
        context: LearnerForgeContext,
        research_events: list[dict[str, Any]],
        plan: StudyPlan,
        evaluation: StudyPlanEvaluation,
    ) -> StudyPlan:
        return await asyncio.to_thread(
            self._invoke_plan,
            context=context,
            research_events=research_events,
            feedback=evaluation,
            previous_plan=plan,
        )

    def _invoke_plan(
        self,
        *,
        context: LearnerForgeContext,
        research_events: list[dict[str, Any]],
        feedback: StudyPlanEvaluation | None,
        previous_plan: StudyPlan | None,
    ) -> StudyPlan:
        runnable = self._llm.with_structured_output(StudyPlan)
        return runnable.invoke(
            [
                (
                    "system",
                    "Você é o planner do Career Forge. Gere um StudyPlan robusto, "
                    "prático, sequenciado e baseado em fontes. Dê liberdade à IA, "
                    "mas mantenha qualidade: pré-requisitos, tarefas, evidência prática "
                    "e aderência ao contexto do aluno.",
                ),
                (
                    "user",
                    _planner_prompt(
                        context=context,
                        research_events=research_events,
                        feedback=feedback,
                        previous_plan=previous_plan,
                    ),
                ),
            ],
        )


def build_study_plan_planner_from_env() -> StudyPlanPlanner:
    return OpenAiStudyPlanPlanner()


def _planner_prompt(
    *,
    context: LearnerForgeContext,
    research_events: list[dict[str, Any]],
    feedback: StudyPlanEvaluation | None,
    previous_plan: StudyPlan | None,
) -> str:
    parts = [
        "## learner_context",
        context.compact_summary(),
        "",
        "## research_state",
        _compact_research(research_events),
    ]
    if previous_plan is not None and feedback is not None:
        parts.extend(
            [
                "",
                "## previous_plan",
                previous_plan.model_dump_json(indent=2),
                "",
                "## evaluator_feedback",
                feedback.model_dump_json(indent=2),
                "",
                "Revise o plano preservando o que está bom e corrigindo os required_changes.",
            ],
        )
    else:
        parts.append("Crie o primeiro StudyPlan.")
    return "\n".join(parts)


def _compact_research(research_events: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for event in research_events:
        if not event.get("sources"):
            continue
        lines.append(f"- {event.get('label')}: {event.get('detail')}")
        for source in event.get("sources") or []:
            lines.append(
                f"  - {source.get('title')} — {source.get('url')} — {source.get('snippet', '')}",
            )
    return "\n".join(lines) or "Sem fontes coletadas."
