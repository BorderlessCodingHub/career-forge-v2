"""Unit tests — OpenAiDiagnosisInterviewLlm with mocked StructuredLlmClient."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from career_forge.ai.llm.diagnosis_interview import OpenAiDiagnosisInterviewLlm
from career_forge.schemas.diagnosis import DiagnosisProfile
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_KEYS,
    PROFILE_DIMENSION_LABELS,
    BeliefState,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
)
from career_forge.schemas.llm_outputs import (
    EstimatedMasteryEntry,
    FinalizeDiagnosisOutput,
    JudgeBeliefOutput,
)


def _sample_dimension(
    key: str,
    *,
    confidence: float = 0.5,
    status: str = "needs_clarification",
) -> RubricDimension:
    return RubricDimension(
        key=key,  # type: ignore[arg-type]
        label=PROFILE_DIMENSION_LABELS[key],  # type: ignore[index]
        confidence=confidence,
        evidence=["evidência"],
        status=status,  # type: ignore[arg-type]
        note="nota",
    )


def _judge_output(**overrides: RubricDimension) -> JudgeBeliefOutput:
    defaults = {key: _sample_dimension(key) for key in PROFILE_DIMENSION_KEYS}
    defaults.update(overrides)
    return JudgeBeliefOutput(**defaults)  # type: ignore[arg-type]


SAMPLE_INTAKE = DiagnosisIntake(
    user_id="test-user",
    goal_id="fullstack",
    motivation="Quero migrar de carreira para tecnologia e construir APIs.",
    years_xp="0-1",
)


@pytest.fixture
def llm() -> OpenAiDiagnosisInterviewLlm:
    with patch("career_forge.ai.llm.diagnosis_interview.StructuredLlmClient"):
        return OpenAiDiagnosisInterviewLlm(model="gpt-4.1-nano")


@pytest.mark.asyncio
async def test_initialize_belief_invokes_judge_schema(llm: OpenAiDiagnosisInterviewLlm) -> None:
    expected = _judge_output(
        motivation_goal=_sample_dimension("motivation_goal", confidence=0.82, status="mapped"),
    )
    llm._client.invoke = AsyncMock(return_value=expected)

    belief = await llm.initialize_belief(SAMPLE_INTAKE, cv_signals=None, cv_text=None)

    llm._client.invoke.assert_awaited_once()
    assert belief.dimensions["motivation_goal"].confidence == 0.82
    assert belief.dimensions["motivation_goal"].status == "mapped"


@pytest.mark.asyncio
async def test_update_belief_applies_transcript_overrides(llm: OpenAiDiagnosisInterviewLlm) -> None:
    belief = BeliefState.empty()
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Consistência",
                rubric_key="learning_velocity",
                question="Quanto tempo dedica?",
                example_of_answer="Ex.: 2 horas por dia.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="2 horas por dia")],
    )
    llm._client.invoke = AsyncMock(return_value=_judge_output())

    updated = await llm.update_belief(belief, SAMPLE_INTAKE, [turn], turn.answers)

    llm._client.invoke.assert_awaited_once()
    assert updated.dimensions["constraints"].status == "mapped"
    assert updated.dimensions["constraints"].confidence >= 0.76
    assert updated.dimensions["learning_velocity"].status == "mapped"
    assert updated.dimensions["learning_velocity"].confidence >= 0.76


@pytest.mark.asyncio
async def test_finalize_diagnosis_invokes_finalize_schema(llm: OpenAiDiagnosisInterviewLlm) -> None:
    belief = BeliefState.empty()
    expected = FinalizeDiagnosisOutput(
        profile=DiagnosisProfile(
            label="Iniciante em transição",
            track_id="fullstack-beginner",
            persona_slug="transicao_iniciante",
        ),
        strengths=["Motivação clara"],
        gaps=["Prova prática"],
        starting_priorities=["http", "git"],
        estimated_mastery=[
            EstimatedMasteryEntry(node_id="js", score=40),
            EstimatedMasteryEntry(node_id="git", score=30),
        ],
    )
    llm._client.invoke = AsyncMock(return_value=expected)

    diagnosis = await llm.finalize_diagnosis(belief, SAMPLE_INTAKE)

    llm._client.invoke.assert_awaited_once()
    assert diagnosis.profile.track_id == "fullstack-beginner"
    assert diagnosis.strengths == ["Motivação clara"]
