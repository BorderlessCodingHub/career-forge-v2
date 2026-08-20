"""Study plan evaluator agent for Roadmap Forge quality gate."""

from __future__ import annotations

import asyncio
from typing import Protocol

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.ai.tracing import LlmTraceContext
from career_forge.schemas.study_plan import StudyPlan, StudyPlanEvaluation


class StudyPlanEvaluator(Protocol):
    async def evaluate(
        self,
        plan: StudyPlan,
        trace: LlmTraceContext | None = None,
    ) -> StudyPlanEvaluation:
        """Return a quality verdict for a draft study plan."""


class OpenAiStudyPlanEvaluator:
    """Mini-model evaluator over a structured study plan draft."""

    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        self._client = StructuredToolClient(
            model_env="FORGE_EVALUATOR_MODEL",
            default_model="gpt-5.4-mini",
            temperature=0,
            method=None,
            key_error="OPENAI_API_KEY is not configured. Set the key before evaluating the plan.",
            model=model,
            api_key=api_key,
        )

    async def evaluate(
        self,
        plan: StudyPlan,
        trace: LlmTraceContext | None = None,
    ) -> StudyPlanEvaluation:
        return await asyncio.to_thread(self._evaluate_sync, plan, trace)

    def _evaluate_sync(
        self,
        plan: StudyPlan,
        trace: LlmTraceContext | None = None,
    ) -> StudyPlanEvaluation:
        system = (
            "You are the Career Forge quality evaluator. "
            "Critique study plans for tech career transitions. "
            "Mark revise if sequence, practice, evidence, sources, or context fit is missing."
        )
        user = (
            "Evaluate this StudyPlan and return structured JSON:\n"
            f"{plan.model_dump_json(indent=2)}"
        )
        return self._client.invoke(
            system=system,
            user=user,
            schema=StudyPlanEvaluation,
            trace=trace,
            operation="evaluator",
        )


def build_study_plan_evaluator_from_env() -> StudyPlanEvaluator:
    return OpenAiStudyPlanEvaluator()
