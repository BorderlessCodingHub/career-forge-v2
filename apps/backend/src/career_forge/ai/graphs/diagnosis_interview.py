"""Adaptive diagnosis interview graph — Judge + Interviewer (HAC-43)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Literal
from uuid import uuid4

from career_forge.ai.llm.diagnosis_interview import (
    DiagnosisInterviewLlmError,
    get_diagnosis_interview_llm,
)
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    MAX_INTERVIEW_ROUNDS,
    MAX_QUESTIONS_PER_TURN,
    BeliefState,
    CvSignals,
    DiagnosisIntake,
    DiagnosisSession,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    build_rubric_map,
)
from career_forge.services.cv import process_cv_attachment

GraphPhase = Literal["start", "turn"]


def _lc_event(
    event: str,
    name: str,
    run_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    return {
        "event": event,
        "name": name,
        "run_id": run_id,
        "tags": [],
        "metadata": {},
        "data": data,
    }


def _extract_cv_text(intake: DiagnosisIntake) -> tuple[str | None, CvSignals | None]:
    if intake.cv is None:
        return None, None
    result = process_cv_attachment(intake.cv)
    return result.text, result.signals


async def run_interview_phase(
    *,
    phase: GraphPhase,
    session: DiagnosisSession,
    answers: list[InterviewAnswer] | None = None,
) -> dict[str, Any]:
    """Execute one graph phase — start (turn 1) or turn (update + next/finalize)."""
    llm = get_diagnosis_interview_llm()
    intake = session.intake

    if phase == "start":
        cv_text, cv_signals = _extract_cv_text(intake)
        if intake.cv and cv_text:
            intake = intake.model_copy(
                update={
                    "cv": intake.cv.model_copy(update={"extracted_text": cv_text}),
                },
            )
            session = session.model_copy(update={"intake": intake})

        belief = await llm.initialize_belief(intake, cv_signals, cv_text)
        session = session.model_copy(
            update={
                "belief": belief,
                "cv_signals": cv_signals,
                "round_count": 0,
            },
        )

        if session.should_finalize():
            diagnosis = await llm.finalize_diagnosis(session.belief, intake)
            session = session.model_copy(
                update={"status": "complete", "diagnosis": diagnosis},
            )
            return _build_output(session, questions=[], diagnosis=diagnosis)

        questions = await llm.plan_questions(
            session.belief,
            intake,
            session.transcript,
            session.round_count,
        )
        questions = questions[:MAX_QUESTIONS_PER_TURN]
        if not questions:
            diagnosis = await llm.finalize_diagnosis(session.belief, intake)
            session = session.model_copy(
                update={"status": "complete", "diagnosis": diagnosis},
            )
            return _build_output(session, questions=[], diagnosis=diagnosis)

        turn = InterviewTurn(questions=questions, answers=[])
        session = session.model_copy(
            update={
                "transcript": [*session.transcript, turn],
                "round_count": 1,
            },
        )
        return _build_output(session, questions=questions)

    # phase == "turn"
    if not answers:
        msg = "turn phase requires answers"
        raise ValueError(msg)

    if not session.transcript:
        msg = "session has no open question turn"
        raise ValueError(msg)

    transcript = list(session.transcript)
    current_turn = transcript[-1].model_copy(
        update={"answers": answers},
    )
    transcript[-1] = current_turn
    session = session.model_copy(update={"transcript": transcript})

    belief = await llm.update_belief(
        session.belief,
        intake,
        transcript,
        answers,
    )
    session = session.model_copy(update={"belief": belief})

    if session.should_finalize():
        diagnosis = await llm.finalize_diagnosis(session.belief, intake)
        session = session.model_copy(
            update={"status": "complete", "diagnosis": diagnosis},
        )
        return _build_output(session, questions=[], diagnosis=diagnosis)

    if session.round_count >= MAX_INTERVIEW_ROUNDS:
        diagnosis = await llm.finalize_diagnosis(session.belief, intake)
        session = session.model_copy(
            update={"status": "complete", "diagnosis": diagnosis},
        )
        return _build_output(session, questions=[], diagnosis=diagnosis)

    questions = await llm.plan_questions(
        session.belief,
        intake,
        session.transcript,
        session.round_count,
    )
    questions = questions[:MAX_QUESTIONS_PER_TURN]

    if not questions:
        diagnosis = await llm.finalize_diagnosis(session.belief, intake)
        session = session.model_copy(
            update={"status": "complete", "diagnosis": diagnosis},
        )
        return _build_output(session, questions=[], diagnosis=diagnosis)

    next_turn = InterviewTurn(questions=questions, answers=[])
    session = session.model_copy(
        update={
            "transcript": [*session.transcript, next_turn],
            "round_count": session.round_count + 1,
        },
    )
    return _build_output(session, questions=questions)


def _build_output(
    session: DiagnosisSession,
    *,
    questions: list[InterviewQuestion],
    diagnosis: DiagnosisResponse | None = None,
) -> dict[str, Any]:
    mapping = build_rubric_map(session.belief)
    return {
        "session": session.model_dump(),
        "session_id": session.session_id,
        "status": session.status,
        "questions": [question.model_dump() for question in questions],
        "mapping_progress": [item.model_dump() for item in mapping],
        "diagnosis": diagnosis.model_dump() if diagnosis else session.diagnosis.model_dump()
        if session.diagnosis
        else None,
    }


class DiagnosisInterviewGraphRunnable:
    """GraphRunnable for CTRR multi-turn diagnosis interview."""

    graph_name = "diagnosis_interview"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[dict[str, Any]]:
        del version
        run_id = str(uuid4())
        phase: GraphPhase = input_data.get("phase", "start")
        session = DiagnosisSession.model_validate(input_data["session"])
        answers_raw = input_data.get("answers") or []
        answers = [InterviewAnswer.model_validate(item) for item in answers_raw]

        yield _lc_event("on_chain_start", self.graph_name, run_id, {})

        try:
            yield _lc_event(
                "on_chain_stream",
                "ingest_intake",
                run_id,
                {
                    "chunk": {
                        "type": "progress",
                        "step": "ingest_intake",
                        "message": "Processando intake e CV",
                    },
                },
            )

            output = await run_interview_phase(
                phase=phase,
                session=session,
                answers=answers if phase == "turn" else None,
            )

            yield _lc_event(
                "on_chain_stream",
                "plan_questions" if output["status"] == "asking" else "finalize_diagnosis",
                run_id,
                {
                    "chunk": {
                        "type": "progress",
                        "step": "complete" if output["status"] == "complete" else "asking",
                        "questions_count": len(output.get("questions") or []),
                    },
                },
            )

            yield _lc_event(
                "on_chain_end",
                self.graph_name,
                run_id,
                {"output": output, "input": input_data},
            )
        except DiagnosisInterviewLlmError as exc:
            yield _lc_event(
                "on_chain_error",
                self.graph_name,
                run_id,
                {"error": exc.retry_message},
            )
            raise


def build_diagnosis_interview_graph() -> DiagnosisInterviewGraphRunnable:
    """Return configured diagnosis_interview graph runnable."""
    return DiagnosisInterviewGraphRunnable()
