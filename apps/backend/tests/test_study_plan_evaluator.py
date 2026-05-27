"""Tests for study-plan evaluator artifacts."""

from __future__ import annotations

import pytest

from career_forge.ai.tools.study_plan_evaluator import OpenAiStudyPlanEvaluator
from career_forge.schemas.study_plan import StudyPlanEvaluation
from career_forge.services.forge_planning import evaluation_artifact


def test_evaluation_artifact_for_revision() -> None:
    event = evaluation_artifact(
        StudyPlanEvaluation(
            verdict="revise",
            gaps=["sem fonte oficial"],
            required_changes=["Adicionar fonte oficial ao primeiro nó"],
        ),
    )

    assert event["type"] == "artifact_found"
    assert event["label"] == "Avaliador do plano: revise"
    assert "Adicionar fonte oficial" in event["detail"]


def test_evaluator_fails_fast_without_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(RuntimeError):
        OpenAiStudyPlanEvaluator(api_key="")
