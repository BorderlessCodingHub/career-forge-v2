"""Study-plan planner/reviser agent for Roadmap Forge."""

from __future__ import annotations

import asyncio
from typing import Any, Protocol

from career_forge.ai.llm.client import StructuredToolClient
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
        self._client = StructuredToolClient(
            model_env="FORGE_PLANNER_MODEL",
            default_model="gpt-5.4",
            temperature=0.2,
            method=None,
            key_error="OPENAI_API_KEY is not configured. Set the key before planning the forge.",
            model=model,
            api_key=api_key,
        )

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
        system = (
            "You are the Career Forge planner. Generate a robust, practical, sequenced, "
            "source-based StudyPlan. Give the model room to invent, but keep quality: "
            "prerequisites, tasks, practical evidence, and fit to the learner context. "
            "For each node fill `key_concepts`: 3 to 6 atomic TECHNICAL concepts the chapter "
            "teaches (e.g. 'list comprehension', 'PUT idempotency', 'np.reshape'). "
            "Never study-logistics language — those concepts become the base for mock "
            "interviews and the Q&A tutor."
        )
        user = _planner_prompt(
            context=context,
            research_events=research_events,
            feedback=feedback,
            previous_plan=previous_plan,
        )
        return self._client.invoke(system=system, user=user, schema=StudyPlan)


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
                "Revise the plan, keeping what is good and fixing the required_changes.",
            ],
        )
    else:
        parts.append("Create the first StudyPlan.")
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
