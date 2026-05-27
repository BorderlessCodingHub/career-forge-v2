"""Study plan evaluator agent for Roadmap Forge quality gate."""

from __future__ import annotations

import asyncio
import os
from typing import Protocol

from langchain_openai import ChatOpenAI

from career_forge.schemas.study_plan import StudyPlan, StudyPlanEvaluation


class StudyPlanEvaluator(Protocol):
    async def evaluate(self, plan: StudyPlan) -> StudyPlanEvaluation:
        """Return a quality verdict for a draft study plan."""


class OpenAiStudyPlanEvaluator:
    """Mini-model evaluator over a structured study plan draft."""

    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        resolved_key = (
            api_key if api_key is not None else os.getenv("OPENAI_API_KEY", "")
        ).strip()
        if not resolved_key:
            msg = "OPENAI_API_KEY não configurada. Configure a chave antes de avaliar o plano."
            raise RuntimeError(msg)
        self._model = model or os.getenv("FORGE_EVALUATOR_MODEL", "gpt-5.4-mini")
        self._llm = ChatOpenAI(model=self._model, api_key=resolved_key, temperature=0)

    async def evaluate(self, plan: StudyPlan) -> StudyPlanEvaluation:
        return await asyncio.to_thread(self._evaluate_sync, plan)

    def _evaluate_sync(self, plan: StudyPlan) -> StudyPlanEvaluation:
        runnable = self._llm.with_structured_output(StudyPlanEvaluation)
        return runnable.invoke(
            [
                (
                    "system",
                    "Você é o avaliador de qualidade do Career Forge. "
                    "Critique planos de estudo para transição de carreira em tech. "
                    "Marque revise se faltar sequência, prática, evidência, fontes ou aderência ao contexto.",
                ),
                (
                    "user",
                    "Avalie este StudyPlan e retorne JSON estruturado:\n"
                    f"{plan.model_dump_json(indent=2)}",
                ),
            ],
        )


def build_study_plan_evaluator_from_env() -> StudyPlanEvaluator:
    return OpenAiStudyPlanEvaluator()
