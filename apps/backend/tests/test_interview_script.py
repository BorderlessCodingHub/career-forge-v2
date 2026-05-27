"""Unit tests — deterministic diagnosis interview script."""

from __future__ import annotations

import pytest

from career_forge.ai.interview.script import (
    COMPOUND_ROUND_ONE,
    FOLLOW_UP_BANK,
    INTERVIEW_ROUND_LABELS,
    ROUND_TWO_KEYS,
    build_round_questions,
    pending_round_two_keys,
    round_index_for_count,
)
from career_forge.schemas.diagnosis_interview import (
    BeliefState,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
    PROFILE_DIMENSION_LABELS,
)


class TestRoundIndexForCount:
    def test_maps_start_to_round_zero(self) -> None:
        assert round_index_for_count(0) == 0

    def test_maps_after_round_one_to_round_one(self) -> None:
        assert round_index_for_count(1) == 1

    def test_maps_done_when_max_rounds_reached(self) -> None:
        assert round_index_for_count(2) is None
        assert round_index_for_count(3) is None


class TestBuildRoundQuestions:
    def test_round_one_is_single_compound_question(self) -> None:
        questions = build_round_questions(0)
        assert len(questions) == 1
        question = questions[0]
        assert question.id == "q-r1-1"
        assert question.rubric_key == "hands_on_proof"
        assert question.question == COMPOUND_ROUND_ONE[0]
        assert question.example_of_answer == COMPOUND_ROUND_ONE[1]

    def test_round_two_has_constraints_and_background(self) -> None:
        questions = build_round_questions(1)
        assert len(questions) == 2
        assert [question.rubric_key for question in questions] == list(ROUND_TWO_KEYS)
        for question in questions:
            prompt, example = FOLLOW_UP_BANK[question.rubric_key]
            assert question.question == prompt
            assert question.example_of_answer == example

    def test_invalid_round_index_raises(self) -> None:
        with pytest.raises(ValueError, match="invalid round_index"):
            build_round_questions(2)

    def test_round_two_skips_mapped_dimensions(self) -> None:
        belief = BeliefState.empty()
        belief.dimensions["constraints"] = RubricDimension(
            key="constraints",
            label=PROFILE_DIMENSION_LABELS["constraints"],
            confidence=0.8,
            evidence=["8h/semana"],
            status="mapped",
            note="Tempo informado",
        )
        questions = build_round_questions(1, belief=belief, transcript=[])
        assert len(questions) == 1
        assert questions[0].rubric_key == "background_transfer"

    def test_round_two_skips_closed_from_transcript(self) -> None:
        belief = BeliefState.empty()
        turn = InterviewTurn(
            questions=[
                InterviewQuestion(
                    id="q-r1-1",
                    topic="Prova prática",
                    rubric_key="hands_on_proof",
                    question="?",
                    example_of_answer="?",
                ),
            ],
            answers=[
                InterviewAnswer(
                    question_id="q-r1-1",
                    text="Estudo 8h por semana em português, sem budget extra.",
                ),
            ],
        )
        assert "constraints" not in pending_round_two_keys(belief, [turn])
        questions = build_round_questions(1, belief=belief, transcript=[turn])
        assert [question.rubric_key for question in questions] == ["background_transfer"]


class TestInterviewRoundLabels:
    def test_two_fixed_round_labels(self) -> None:
        assert len(INTERVIEW_ROUND_LABELS) == 2
        assert INTERVIEW_ROUND_LABELS[0] == "Prática e rotina"
        assert INTERVIEW_ROUND_LABELS[1] == "Contexto e limitações"
