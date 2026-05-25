"""Tests for structured diagnosis interview payloads."""

from career_forge.ai.payloads.diagnosis_interview import (
    apply_schedule_overrides,
    apply_transcript_overrides,
    build_interviewer_user_message,
    closed_dimensions_from_transcript,
    detect_negative_hands_on,
)
from career_forge.schemas.diagnosis_interview import (
    BeliefState,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
)


def test_detect_negative_hands_on() -> None:
    assert detect_negative_hands_on("nunca, nadinha")
    assert detect_negative_hands_on("Só teoria, zero projetos")
    assert not detect_negative_hands_on("Fiz um dashboard no GitHub")


def test_closed_dimensions_from_negative_answer() -> None:
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Prova prática",
                rubric_key="hands_on_proof",
                question="Já fez algum projeto?",
                example_of_answer="Ex.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="nunca, nadinha")],
    )
    closed = closed_dimensions_from_transcript([turn])
    assert "hands_on_proof" in closed


def test_apply_schedule_overrides_maps_hours_per_day() -> None:
    belief = BeliefState.empty()
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Consistência",
                rubric_key="learning_velocity",
                question="Quanto tempo dedica por semana?",
                example_of_answer="Ex.: 2 horas por dia.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="2 horas por dia")],
    )
    updated = apply_schedule_overrides(belief, [turn])
    constraints = updated.dimensions["constraints"]
    velocity = updated.dimensions["learning_velocity"]
    assert constraints.status == "mapped"
    assert constraints.confidence >= 0.76
    assert velocity.status == "mapped"
    assert velocity.confidence >= 0.76
    assert "Rotina/tempo mencionados pelo usuário" in constraints.note


def test_apply_transcript_overrides_maps_negative_proof() -> None:
    belief = BeliefState.empty()
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Prova prática",
                rubric_key="hands_on_proof",
                question="Já fez algum projeto?",
                example_of_answer="Ex.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="nunca fiz nada prático")],
    )
    updated = apply_transcript_overrides(belief, [turn])
    proof = updated.dimensions["hands_on_proof"]
    assert proof.status == "mapped"
    assert proof.confidence >= 0.68


def test_interviewer_payload_lists_do_not_ask() -> None:
    intake = DiagnosisIntake(
        goal_id="ai-ml",
        motivation="Quero ser engenheiro de IA",
        years_xp="0-1",
    )
    belief = BeliefState.empty()
    turn = InterviewTurn(
        questions=[
            InterviewQuestion(
                id="q-1",
                topic="Prova prática",
                rubric_key="hands_on_proof",
                question="Já fez algum projeto?",
                example_of_answer="Ex.",
            ),
        ],
        answers=[InterviewAnswer(question_id="q-1", text="nunca, nadinha")],
    )
    message = build_interviewer_user_message(
        intake=intake,
        belief=belief,
        transcript=[turn],
        round_count=1,
        max_questions=2,
    )
    assert "## do_not_ask" in message
    assert "hands_on_proof" in message
    assert "resposta negativa" in message.lower()
