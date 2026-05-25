"""Unit tests — CTRR diagnosis interview schemas (HAC-42)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    CTRR_DIMENSION_KEYS,
    CTRR_DIMENSION_LABELS,
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


class TestCtrrConstants:
    def test_dimension_keys_match_labels(self) -> None:
        assert set(CTRR_DIMENSION_KEYS) == set(CTRR_DIMENSION_LABELS.keys())
        assert len(CTRR_DIMENSION_KEYS) == 8

    def test_saturation_threshold(self) -> None:
        assert SATURATION_CONFIDENCE_THRESHOLD == 0.75
        assert MAX_INTERVIEW_ROUNDS == 5
        assert MAX_QUESTIONS_PER_TURN == 2


class TestBeliefState:
    def test_empty_has_all_dimensions(self) -> None:
        belief = BeliefState.empty()
        assert set(belief.dimensions.keys()) == set(CTRR_DIMENSION_KEYS)
        assert all(dim.confidence == 0.0 for dim in belief.dimensions.values())

    def test_unsaturated_keys(self) -> None:
        belief = BeliefState.empty()
        assert len(belief.unsaturated_keys()) == len(CTRR_DIMENSION_KEYS)

        belief.dimensions["git"] = RubricDimension(
            key="git",
            label=CTRR_DIMENSION_LABELS["git"],
            confidence=0.9,
            evidence=["uso diário"],
        )
        unsaturated = belief.unsaturated_keys()
        assert "git" not in unsaturated
        assert "learning_stage" in unsaturated

    def test_is_saturated(self) -> None:
        belief = BeliefState.empty()
        assert belief.is_saturated() is False

        for key in CTRR_DIMENSION_KEYS:
            belief.dimensions[key] = RubricDimension(
                key=key,
                label=CTRR_DIMENSION_LABELS[key],
                confidence=SATURATION_CONFIDENCE_THRESHOLD,
                evidence=["ok"],
            )
        assert belief.is_saturated() is True


class TestInterviewQuestion:
    def test_parses_interviewer_output(self) -> None:
        q = InterviewQuestion.model_validate(
            {
                "id": "q1",
                "topic": "Senioridade",
                "rubric_key": "learning_stage",
                "question": "Como você descreveria seu nível hoje?",
                "example_of_answer": "Estou no início, fiz um curso de JS.",
            },
        )
        assert q.rubric_key == "learning_stage"
        assert q.topic == "Senioridade"


class TestDiagnosisIntake:
    def test_minimal_intake(self) -> None:
        intake = DiagnosisIntake.model_validate(
            {
                "user_id": "u1",
                "goal_id": "backend",
                "motivation": "Quero migrar de carreira para tecnologia.",
            },
        )
        assert intake.years_xp is None
        assert intake.cv is None

    def test_intake_with_cv(self) -> None:
        intake = DiagnosisIntake.model_validate(
            {
                "goal_id": "backend",
                "motivation": "Quero migrar de carreira para tecnologia.",
                "cv": {
                    "filename": "cv.pdf",
                    "mime_type": "application/pdf",
                    "content_base64": "JVBERi0x",
                },
            },
        )
        assert intake.cv is not None
        assert intake.cv.mime_type == "application/pdf"


class TestDiagnosisSession:
    def test_should_finalize_on_saturation(self) -> None:
        session = DiagnosisSession(
            session_id="sess-1",
            intake=DiagnosisIntake(
                goal_id="backend",
                motivation="Quero migrar de carreira para tecnologia.",
            ),
        )
        assert session.should_finalize() is False

        for key in CTRR_DIMENSION_KEYS:
            session.belief.dimensions[key] = RubricDimension(
                key=key,
                label=CTRR_DIMENSION_LABELS[key],
                confidence=0.8,
                evidence=["ev"],
            )
        assert session.should_finalize() is True

    def test_should_finalize_on_max_rounds(self) -> None:
        session = DiagnosisSession(
            session_id="sess-2",
            intake=DiagnosisIntake(
                goal_id="backend",
                motivation="Quero migrar de carreira para tecnologia.",
            ),
            round_count=MAX_INTERVIEW_ROUNDS,
        )
        assert session.should_finalize() is True


class TestRubricMap:
    def test_build_rubric_map_order(self) -> None:
        belief = BeliefState.empty()
        belief.dimensions["git"] = RubricDimension(
            key="git",
            label=CTRR_DIMENSION_LABELS["git"],
            confidence=0.8,
            evidence=[],
        )
        items = build_rubric_map(belief)
        assert [item.rubric_key for item in items] == list(CTRR_DIMENSION_KEYS)
        git_item = next(item for item in items if item.rubric_key == "git")
        assert git_item.saturated is True
        assert git_item.confidence == 0.8


class TestInterviewTurn:
    def test_append_only_turn(self) -> None:
        turn = InterviewTurn(
            questions=[
                InterviewQuestion(
                    id="q1",
                    topic="Git",
                    rubric_key="git",
                    question="Você já usou Git?",
                    example_of_answer="Sim, commits básicos.",
                ),
            ],
            answers=[
                InterviewAnswer(question_id="q1", text="Uso git init e commit."),
            ],
        )
        assert len(turn.questions) == 1
        assert turn.answers[0].question_id == "q1"

    def test_rejects_too_many_questions(self) -> None:
        with pytest.raises(ValidationError):
            InterviewTurn.model_validate(
                {
                    "questions": [
                        {
                            "id": f"q{i}",
                            "topic": "Git",
                            "rubric_key": "git",
                            "question": f"Q{i}?",
                            "example_of_answer": "Ex.",
                        }
                        for i in range(3)
                    ],
                },
            )


class TestInterviewTurnRequest:
    def test_requires_at_least_one_answer(self) -> None:
        with pytest.raises(ValidationError):
            InterviewTurnRequest.model_validate({"answers": []})

    def test_strips_empty_answer(self) -> None:
        with pytest.raises(ValidationError):
            InterviewAnswer.model_validate({"question_id": "q1", "text": "   "})


class TestInterviewTurnResponse:
    def test_asking_response(self) -> None:
        resp = InterviewTurnResponse.model_validate(
            {
                "session_id": "sess-1",
                "status": "asking",
                "questions": [
                    {
                        "id": "q1",
                        "topic": "Git",
                        "rubric_key": "git",
                        "question": "Você já usou Git?",
                        "example_of_answer": "Sim, commits básicos.",
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
        assert resp.diagnosis.profile.track_id == "backend-beginner"

        with pytest.raises(ValidationError):
            InterviewTurnResponse.model_validate(
                {
                    "session_id": "sess-1",
                    "status": "complete",
                    "questions": [],
                    "mapping_progress": [],
                },
            )
