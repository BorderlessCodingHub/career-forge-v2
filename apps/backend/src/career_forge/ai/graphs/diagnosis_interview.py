"""Adaptive diagnosis interview graph — Judge + deterministic script (HAC-43)."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any, Literal

from career_forge.ai.interview.script import build_round_questions, round_index_for_count
from career_forge.ai.llm.diagnosis_interview import (
    DiagnosisInterviewLlmError,
    get_diagnosis_interview_llm,
)
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
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


from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    emit_chain_error,
    new_run_id,
)


def _extract_cv_text(intake: DiagnosisIntake) -> tuple[str | None, CvSignals | None]:
    if intake.cv is None:
        return None, None
    result = process_cv_attachment(intake.cv)
    return result.text, result.signals


def _load_round_questions(
    round_count: int,
    *,
    belief: BeliefState | None = None,
    transcript: list[InterviewTurn] | None = None,
) -> list[InterviewQuestion]:
    round_index = round_index_for_count(round_count)
    if round_index is None:
        return []
    return build_round_questions(
        round_index,
        belief=belief,
        transcript=transcript,
    )[:MAX_QUESTIONS_PER_TURN]


async def _finalize_session(
    session: DiagnosisSession,
    intake: DiagnosisIntake,
    llm: Any,
) -> tuple[DiagnosisSession, DiagnosisResponse]:
    diagnosis = await llm.finalize_diagnosis(session.belief, intake)
    updated = session.model_copy(
        update={"status": "complete", "diagnosis": diagnosis},
    )
    return updated, diagnosis


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
            session, diagnosis = await _finalize_session(session, intake, llm)
            return _build_output(session, questions=[], diagnosis=diagnosis)

        questions = _load_round_questions(session.round_count)
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
        session, diagnosis = await _finalize_session(session, intake, llm)
        return _build_output(session, questions=[], diagnosis=diagnosis)

    questions = _load_round_questions(
        session.round_count,
        belief=session.belief,
        transcript=session.transcript,
    )
    if not questions:
        session, diagnosis = await _finalize_session(session, intake, llm)
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


async def _yield_mapping_progress(
    belief: BeliefState,
) -> AsyncIterator[dict[str, Any]]:
    """Stream rubric dimensions one-by-one for live UI updates."""
    mapping = build_rubric_map(belief)
    for index, item in enumerate(mapping):
        yield {
            "type": "mapping_dimension",
            "item": item.model_dump(),
            "index": index,
            "total": len(mapping),
        }
        if index < len(mapping) - 1:
            await asyncio.sleep(0.12)


async def _run_start_phase_streaming(
    session: DiagnosisSession,
) -> AsyncIterator[dict[str, Any]]:
    """Start phase with SSE chunks; final yield is `_output` sentinel."""
    llm = get_diagnosis_interview_llm()
    intake = session.intake

    yield {"type": "interview_status", "phase": "analyzing_intake"}

    cv_text, cv_signals = _extract_cv_text(intake)
    if intake.cv and cv_text:
        yield {"type": "interview_status", "phase": "analyzing_cv"}
        intake = intake.model_copy(
            update={
                "cv": intake.cv.model_copy(update={"extracted_text": cv_text}),
            },
        )
        session = session.model_copy(update={"intake": intake})

    yield {"type": "interview_status", "phase": "judging"}
    belief = await llm.initialize_belief(intake, cv_signals, cv_text)
    session = session.model_copy(
        update={
            "belief": belief,
            "cv_signals": cv_signals,
            "round_count": 0,
        },
    )

    async for chunk in _yield_mapping_progress(session.belief):
        yield chunk

    if session.should_finalize():
        yield {"type": "interview_status", "phase": "finalizing"}
        session, diagnosis = await _finalize_session(session, intake, llm)
        yield {"type": "_output", "output": _build_output(session, questions=[], diagnosis=diagnosis)}
        return

    yield {"type": "interview_status", "phase": "loading_questions"}
    questions = _load_round_questions(session.round_count)
    turn = InterviewTurn(questions=questions, answers=[])
    session = session.model_copy(
        update={
            "transcript": [*session.transcript, turn],
            "round_count": 1,
        },
    )
    yield {"type": "_output", "output": _build_output(session, questions=questions)}


async def _run_turn_phase_streaming(
    session: DiagnosisSession,
    answers: list[InterviewAnswer],
) -> AsyncIterator[dict[str, Any]]:
    llm = get_diagnosis_interview_llm()
    intake = session.intake

    if not session.transcript:
        msg = "session has no open question turn"
        raise ValueError(msg)

    yield {"type": "interview_status", "phase": "processing_answers"}

    transcript = list(session.transcript)
    current_turn = transcript[-1].model_copy(update={"answers": answers})
    transcript[-1] = current_turn
    session = session.model_copy(update={"transcript": transcript})

    yield {"type": "interview_status", "phase": "judging"}
    belief = await llm.update_belief(session.belief, intake, transcript, answers)
    session = session.model_copy(update={"belief": belief})

    async for chunk in _yield_mapping_progress(session.belief):
        yield chunk

    if session.should_finalize():
        yield {"type": "interview_status", "phase": "finalizing"}
        session, diagnosis = await _finalize_session(session, intake, llm)
        yield {"type": "_output", "output": _build_output(session, questions=[], diagnosis=diagnosis)}
        return

    yield {"type": "interview_status", "phase": "loading_questions"}
    questions = _load_round_questions(
        session.round_count,
        belief=session.belief,
        transcript=session.transcript,
    )
    if not questions:
        yield {"type": "interview_status", "phase": "finalizing"}
        session, diagnosis = await _finalize_session(session, intake, llm)
        yield {"type": "_output", "output": _build_output(session, questions=[], diagnosis=diagnosis)}
        return

    next_turn = InterviewTurn(questions=questions, answers=[])
    session = session.model_copy(
        update={
            "transcript": [*session.transcript, next_turn],
            "round_count": session.round_count + 1,
        },
    )
    yield {"type": "_output", "output": _build_output(session, questions=questions)}


class DiagnosisInterviewGraphRunnable:
    """GraphRunnable for CTRR multi-turn diagnosis interview."""

    graph_name = "diagnosis_interview"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        run_id = new_run_id()
        phase: GraphPhase = input_data.get("phase", "start")
        session = DiagnosisSession.model_validate(input_data["session"])
        answers_raw = input_data.get("answers") or []
        answers = [InterviewAnswer.model_validate(item) for item in answers_raw]

        yield emit_chain_start(self.graph_name, run_id)

        try:
            output: dict[str, Any] | None = None

            if phase == "start":
                stream = _run_start_phase_streaming(session)
            else:
                stream = _run_turn_phase_streaming(session, answers)

            async for chunk in stream:
                if chunk.get("type") == "_output":
                    output = chunk["output"]
                    continue
                yield emit_chain_stream(self.graph_name, run_id, chunk)

            if output is None:
                msg = "diagnosis interview graph completed without output"
                raise DiagnosisInterviewLlmError(msg)

            yield emit_chain_end(
                self.graph_name,
                run_id,
                output=output,
                input_data=input_data,
            )
        except DiagnosisInterviewLlmError as exc:
            yield emit_chain_error(self.graph_name, run_id, exc.retry_message)
            raise


def build_diagnosis_interview_graph() -> DiagnosisInterviewGraphRunnable:
    """Return configured diagnosis_interview graph runnable."""
    return DiagnosisInterviewGraphRunnable()
