"""Tests for study-plan evaluator artifacts."""

from __future__ import annotations

import pytest

from career_forge.ai.tools.study_plan_evaluator import OpenAiStudyPlanEvaluator
from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanEvaluation,
    StudyPlanNode,
    StudyPlanTask,
    StudyResource,
)
from career_forge.services.forge_planning import evaluation_artifact, study_plan_to_graph


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


def test_study_resource_uses_plain_string_url_for_openai_schema() -> None:
    resource = StudyResource(
        title="OpenAI docs",
        url="https://platform.openai.com/docs",
    )
    schema = StudyResource.model_json_schema()
    assert resource.url == "https://platform.openai.com/docs"
    assert schema["properties"]["url"]["type"] == "string"
    assert "format" not in schema["properties"]["url"]


def test_study_plan_to_graph_preserves_references_and_tasks() -> None:
    plan = StudyPlan(
        goal="AI Engineer",
        learner_context_summary="summary",
        strategy="strategy",
        nodes=[
            StudyPlanNode(
                node_id="python-ai",
                title="Python para IA",
                why_now="Base para IA.",
                prerequisites=["setup"],
                tasks=[
                    StudyPlanTask(
                        title="Criar notebook",
                        outcome="Publicar notebook",
                        evidence_prompt="Explique o notebook.",
                    ),
                ],
                resources=[
                    StudyResource(
                        title="Python docs",
                        url="https://docs.python.org/3/tutorial/",
                    ),
                ],
            ),
        ],
    )

    graph = study_plan_to_graph(plan)
    assert graph[0].node_id == "python-ai"
    assert graph[0].prerequisites == ["setup"]
    assert graph[0].tasks[0]["title"] == "Criar notebook"
    assert graph[0].references[0]["title"] == "Python docs"
