"""Unit tests — universal profile diagnosis interview schemas (ADR-002)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_DESCRIPTIONS,
    PROFILE_DIMENSION_KEYS,
    PROFILE_DIMENSION_LABELS,
    MAX_INTERVIEW_ROUNDS,
    MAX_QUESTIONS_PER_TURN,
    SATURATION_CONFIDENCE_THRESHOLD,
    BeliefState,
    DiagnosisIntake,
    DiagnosisSession,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    InterviewTurnRequest,
    InterviewTurnResponse,
    RubricDimension,
    build_rubric_map,
)

FIXTURES = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "career_forge"
    / "fixtures"
)


def load_fixture(name: str) -> dict:
    with (FIXTURES / name).open(encoding="utf-8") as f:
        return json.load(f)


class TestProfileConstants:
    def test_dimension_keys_match_labels(self) -> None:
        assert set(PROFILE_DIMENSION_KEYS) == set(PROFILE_DIMENSION_LABELS.keys())
        assert set(PROFILE_DIMENSION_KEYS) == set(PROFILE_DIMENSION_DESCRIPTIONS.keys())
        assert len(PROFILE_DIMENSION_KEYS) == 5

    def test_saturation_threshold(self) -> None:
        assert SATURATION_CONFIDENCE_THRESHOLD == 0.75
        assert MAX_INTERVIEW_ROUNDS == 2
        assert MAX_QUESTIONS_PER_TURN == 2


class TestBeliefState:
    def test_empty_has_all_dimensions(self) -> None:
        belief = BeliefState.empty()
        assert set(belief.dimensions.keys()) == set(PROFILE_DIMENSION_KEYS)
        assert all(dim.confidence == 0.0 for dim in belief.dimensions.values())

    def test_unsaturated_keys(self) -> None:
        belief = BeliefState.empty()
        assert len(belief.unsaturated_keys()) == len(PROFILE_DIMENSION_KEYS)
        assert len(belief.interviewable_keys()) == len(PROFILE_DIMENSION_KEYS)

        belief.dimensions["hands_on_proof"] = RubricDimension(
            key="hands_on_proof",
            label=PROFILE_DIMENSION_LABELS["hands_on_proof"],
            confidence=0.9,
            evidence=["projeto no GitHub"],
            status="mapped",
            note="Entregou projeto no GitHub",
        )
        unsaturated = belief.unsaturated_keys()
        assert "hands_on_proof" not in unsaturated
        assert "learning_velocity" in unsaturated
        assert "hands_on_proof" not in belief.interviewable_keys()
        assert "learning_velocity" in belief.interviewable_keys()

    def test_is_interview_complete(self) -> None:
        belief = BeliefState.empty()
        assert belief.is_interview_complete() is False

        for key in PROFILE_DIMENSION_KEYS:
            belief.dimensions[key] = RubricDimension(
                key=key,
                label=PROFILE_DIMENSION_LABELS[key],
                confidence=0.8,
                evidence=["ev"],
                status="mapped",
                note="Confirmado",
            )
        assert belief.is_interview_complete() is True

        belief.dimensions["constraints"] = RubricDimension(
            key="constraints",
            label=PROFILE_DIMENSION_LABELS["constraints"],
            confidence=0.8,
            evidence=["ev"],
            status="needs_clarification",
            note="Falta confirmar tempo/semana",
        )
        assert belief.is_interview_complete() is False

    def test_profile_completeness(self) -> None:
        belief = BeliefState.empty()
        assert belief.profile_completeness() == 0.0
        belief.dimensions["motivation_goal"] = RubricDimension(
            key="motivation_goal",
            label=PROFILE_DIMENSION_LABELS["motivation_goal"],
            confidence=0.8,
            evidence=["motivação clara"],
            status="mapped",
            note="Objetivo claro",
        )
        assert belief.profile_completeness() == 0.2


class TestInterviewQuestion:
    def test_parses_interviewer_output(self) -> None:
        q = InterviewQuestion.model_validate(
            {
                "id": "q1",
                "topic": "Prova prática",
                "rubric_key": "hands_on_proof",
                "question": "Conte o que você já construiu ou tentou.",
                "example_of_answer": "Fiz um app na faculdade com Git.",
            },
        )
        assert q.rubric_key == "hands_on_proof"
        assert q.topic == "Prova prática"


class TestDiagnosisIntake:
    def test_minimal_intake(self) -> None:
        intake = DiagnosisIntake.model_validate(
            {
                "user_id": "u1",
                "goal_id": "ai-ml",
                "motivation": "Quero migrar de carreira para tecnologia.",
            },
        )
        assert intake.years_xp is None
        assert intake.cv is None


class TestDiagnosisSession:
    def test_should_not_finalize_on_mapped_dims_before_max_rounds(self) -> None:
        session = DiagnosisSession(
            session_id="sess-1",
            intake=DiagnosisIntake(
                goal_id="fullstack",
                motivation="Quero migrar de carreira para tecnologia.",
            ),
            round_count=1,
        )
        for key in PROFILE_DIMENSION_KEYS:
            session.belief.dimensions[key] = RubricDimension(
                key=key,
                label=PROFILE_DIMENSION_LABELS[key],
                confidence=0.8,
                evidence=["ev"],
                status="mapped",
                note="Confirmado",
            )
        assert session.should_finalize() is False

    def test_should_finalize_on_max_rounds(self) -> None:
        session = DiagnosisSession(
            session_id="sess-2",
            intake=DiagnosisIntake(
                goal_id="data",
                motivation="Quero migrar de carreira para tecnologia.",
            ),
            round_count=MAX_INTERVIEW_ROUNDS,
        )
        assert session.should_finalize() is True


class TestRubricMap:
    def test_build_rubric_map_order(self) -> None:
        belief = BeliefState.empty()
        belief.dimensions["hands_on_proof"] = RubricDimension(
            key="hands_on_proof",
            label=PROFILE_DIMENSION_LABELS["hands_on_proof"],
            confidence=0.8,
            evidence=[],
            status="mapped",
            note="Projeto entregue",
        )
        items = build_rubric_map(belief)
        assert [item.rubric_key for item in items] == list(PROFILE_DIMENSION_KEYS)
        proof_item = next(item for item in items if item.rubric_key == "hands_on_proof")
        assert proof_item.saturated is True
        assert proof_item.description == PROFILE_DIMENSION_DESCRIPTIONS["hands_on_proof"]


class TestInterviewTurn:
    def test_append_only_turn(self) -> None:
        turn = InterviewTurn(
            questions=[
                InterviewQuestion(
                    id="q1",
                    topic="Prova prática",
                    rubric_key="hands_on_proof",
                    question="Conte o que você já fez.",
                    example_of_answer="App na faculdade.",
                ),
            ],
            answers=[
                InterviewAnswer(question_id="q1", text="Fiz um app em grupo."),
            ],
        )
        assert len(turn.questions) == 1


class TestInterviewTurnResponse:
    def test_asking_response(self) -> None:
        resp = InterviewTurnResponse.model_validate(
            {
                "session_id": "sess-1",
                "status": "asking",
                "questions": [
                    {
                        "id": "q1",
                        "topic": "Prova prática",
                        "rubric_key": "hands_on_proof",
                        "question": "Conte o que você já fez.",
                        "example_of_answer": "App na faculdade.",
                    },
                ],
                "mapping_progress": build_rubric_map(BeliefState.empty()),
            },
        )
        assert resp.status == "asking"
        assert resp.diagnosis is None

    def test_complete_requires_diagnosis(self) -> None:
        diagnosis = DiagnosisResponse.model_validate(load_fixture("diagnosis_response.json"))
        resp = InterviewTurnResponse.model_validate(
            {
                "session_id": "sess-1",
                "status": "complete",
                "questions": [],
                "mapping_progress": build_rubric_map(BeliefState.empty()),
                "diagnosis": diagnosis.model_dump(),
            },
        )
        assert resp.diagnosis is not None

        with pytest.raises(ValidationError):
            InterviewTurnResponse.model_validate(
                {
                    "session_id": "sess-1",
                    "status": "complete",
                    "questions": [],
                    "mapping_progress": [],
                },
            )
