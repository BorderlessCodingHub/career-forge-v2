"""Diagnosis interview session persistence + graph orchestration (HAC-44)."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable
from uuid import UUID, uuid4

from career_forge.ai.executor import GraphExecutor, get_graph_executor
from career_forge.ai.llm.diagnosis_interview import DiagnosisInterviewLlmError
from career_forge.ai.run import GraphRun, GraphRunResult, GraphRunStore, InMemoryGraphRunStore
from career_forge.ai.streaming.sse import events_to_sse
from career_forge.db.models.diagnosis_session import DiagnosisSessionRecord
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis_interview import (
    MAX_INTERVIEW_ROUNDS,
    MAX_QUESTIONS_PER_TURN,
    BeliefState,
    DiagnosisSession,
    InterviewStartRequest,
    InterviewTurnRequest,
    InterviewTurnResponse,
    RubricMapItem,
    InterviewQuestion,
    build_rubric_map,
)
from career_forge.services.cv import enrich_cv_attachment


class DiagnosisSessionNotFoundError(Exception):
    """Session id not found."""


class DiagnosisSessionCompleteError(Exception):
    """Cannot submit turn on completed session."""


class DiagnosisInterviewTurnError(Exception):
    """Validation error on turn submission."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@runtime_checkable
class DiagnosisSessionStore(Protocol):
    def save(self, session: DiagnosisSession) -> None: ...
    def get(self, session_id: str) -> DiagnosisSession | None: ...


class InMemoryDiagnosisSessionStore:
    """Dev/test session store."""

    def __init__(self) -> None:
        self._sessions: dict[str, DiagnosisSession] = {}

    def save(self, session: DiagnosisSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> DiagnosisSession | None:
        return self._sessions.get(session_id)


class PostgresDiagnosisSessionStore:
    """Postgres-backed session store."""

    def save(self, session: DiagnosisSession) -> None:
        db = SessionLocal()
        try:
            record_id = UUID(session.session_id)
            existing = db.get(DiagnosisSessionRecord, record_id)
            payload = _session_to_record_fields(session)
            if existing is None:
                db.add(
                    DiagnosisSessionRecord(
                        id=record_id,
                        user_id=session.intake.user_id,
                        **payload,
                    ),
                )
            else:
                for key, value in payload.items():
                    setattr(existing, key, value)
            db.commit()
        finally:
            db.close()

    def get(self, session_id: str) -> DiagnosisSession | None:
        db = SessionLocal()
        try:
            record = db.get(DiagnosisSessionRecord, UUID(session_id))
            if record is None:
                return None
            return _record_to_session(record)
        finally:
            db.close()


def _session_to_record_fields(session: DiagnosisSession) -> dict:
    return {
        "status": session.status,
        "intake": session.intake.model_dump(),
        "belief_state": session.belief.model_dump(),
        "cv_signals": session.cv_signals.model_dump() if session.cv_signals else None,
        "transcript": [turn.model_dump() for turn in session.transcript],
        "round_count": session.round_count,
        "diagnosis": session.diagnosis.model_dump() if session.diagnosis else None,
    }


def _record_to_session(record: DiagnosisSessionRecord) -> DiagnosisSession:
    return DiagnosisSession(
        session_id=str(record.id),
        intake=record.intake,
        belief=BeliefState.model_validate(record.belief_state),
        cv_signals=record.cv_signals,
        transcript=record.transcript,
        status=record.status,
        round_count=record.round_count,
        diagnosis=record.diagnosis,
    )


_default_store: DiagnosisSessionStore | None = None


def get_diagnosis_session_store() -> DiagnosisSessionStore:
    global _default_store
    if _default_store is not None:
        return _default_store

    mode = os.getenv("DIAGNOSIS_SESSION_STORE", "auto").lower()
    if mode == "memory":
        _default_store = InMemoryDiagnosisSessionStore()
    elif mode == "postgres" or (mode == "auto" and os.getenv("DATABASE_URL")):
        _default_store = PostgresDiagnosisSessionStore()
    else:
        _default_store = InMemoryDiagnosisSessionStore()
    return _default_store


def set_diagnosis_session_store(store: DiagnosisSessionStore | None) -> None:
    global _default_store
    _default_store = store


def _extract_graph_output(result: GraphRunResult) -> dict:
    output = result.run.output
    if output is None:
        msg = "diagnosis_interview graph completed without output"
        raise DiagnosisInterviewLlmError(msg)

    if output.get("type") == "graph_complete" and isinstance(output.get("output"), dict):
        return output["output"]

    if isinstance(output, dict) and "session" in output:
        return output

    msg = "unexpected graph output shape"
    raise DiagnosisInterviewLlmError(msg)


def _graph_output_to_response(graph_output: dict) -> InterviewTurnResponse:
    return InterviewTurnResponse.model_validate(
        {
            "session_id": graph_output["session_id"],
            "status": graph_output["status"],
            "questions": graph_output.get("questions") or [],
            "mapping_progress": graph_output.get("mapping_progress") or [],
            "diagnosis": graph_output.get("diagnosis"),
        },
    )


class DiagnosisSessionService:
    """Orchestrates interview sessions via GraphExecutor."""

    def __init__(
        self,
        *,
        session_store: DiagnosisSessionStore | None = None,
        graph_store: GraphRunStore | None = None,
        executor: GraphExecutor | None = None,
    ) -> None:
        self._sessions = session_store or get_diagnosis_session_store()
        self._graph_store = graph_store or InMemoryGraphRunStore()
        self._executor = executor or GraphExecutor(store=self._graph_store)

    async def start_interview(self, body: InterviewStartRequest) -> InterviewTurnResponse:
        intake = body.model_copy(deep=True)
        if intake.cv is not None:
            intake = intake.model_copy(update={"cv": enrich_cv_attachment(intake.cv)})

        session_id = str(uuid4())
        session = DiagnosisSession(
            session_id=session_id,
            intake=intake,
        )
        self._sessions.save(session)

        graph_output = await self._execute_graph(
            phase="start",
            session=session,
            answers=None,
        )
        updated = DiagnosisSession.model_validate(graph_output["session"])
        self._sessions.save(updated)
        return _graph_output_to_response(graph_output)

    async def stream_interview_start(
        self,
        body: InterviewStartRequest,
    ) -> AsyncIterator[str]:
        intake = body.model_copy(deep=True)
        if intake.cv is not None:
            intake = intake.model_copy(update={"cv": enrich_cv_attachment(intake.cv)})

        session_id = str(uuid4())
        session = DiagnosisSession(
            session_id=session_id,
            intake=intake,
        )
        self._sessions.save(session)

        async for line in self._stream_graph(
            phase="start",
            session=session,
            answers=None,
        ):
            yield line

    async def stream_interview_turn(
        self,
        session_id: str,
        body: InterviewTurnRequest,
    ) -> AsyncIterator[str]:
        session = self._sessions.get(session_id)
        if session is None:
            raise DiagnosisSessionNotFoundError(session_id)
        if session.is_complete():
            raise DiagnosisSessionCompleteError(session_id)

        self._validate_turn(session, body)

        async for line in self._stream_graph(
            phase="turn",
            session=session,
            answers=body.answers,
        ):
            yield line

    async def _stream_graph(
        self,
        *,
        phase: str,
        session: DiagnosisSession,
        answers: list | None,
    ) -> AsyncIterator[str]:
        run = GraphRun(
            graph_name="diagnosis_interview",
            user_id=session.intake.user_id,
            input={
                "phase": phase,
                "session": session.model_dump(),
                "answers": [answer.model_dump() for answer in answers or []],
            },
        )
        self._graph_store.save(run)
        event_iter = await self._executor.execute(run, stream=True)
        assert not isinstance(event_iter, GraphRunResult)

        async def _events() -> AsyncIterator[dict]:
            async for event in event_iter:
                if event.get("type") == "graph_complete":
                    graph_output = event.get("output") or {}
                    if isinstance(graph_output, dict) and "session" in graph_output:
                        updated = DiagnosisSession.model_validate(graph_output["session"])
                        self._sessions.save(updated)
                yield event

        async for line in events_to_sse(_events()):
            yield line

    async def submit_turn(
        self,
        session_id: str,
        body: InterviewTurnRequest,
    ) -> InterviewTurnResponse:
        session = self._sessions.get(session_id)
        if session is None:
            raise DiagnosisSessionNotFoundError(session_id)
        if session.is_complete():
            raise DiagnosisSessionCompleteError(session_id)

        self._validate_turn(session, body)

        graph_output = await self._execute_graph(
            phase="turn",
            session=session,
            answers=body.answers,
        )
        updated = DiagnosisSession.model_validate(graph_output["session"])
        self._sessions.save(updated)
        return _graph_output_to_response(graph_output)

    def _validate_turn(
        self,
        session: DiagnosisSession,
        body: InterviewTurnRequest,
    ) -> None:
        if not session.transcript:
            raise DiagnosisInterviewTurnError("Nenhuma pergunta aberta nesta sessão.")

        open_turn = session.transcript[-1]
        expected_ids = {question.id for question in open_turn.questions}
        submitted_ids = {answer.question_id for answer in body.answers}

        if not submitted_ids.issubset(expected_ids):
            raise DiagnosisInterviewTurnError(
                "Respostas não correspondem às perguntas da rodada atual.",
            )

        if len(body.answers) > MAX_QUESTIONS_PER_TURN:
            raise DiagnosisInterviewTurnError(
                f"Máximo de {MAX_QUESTIONS_PER_TURN} respostas por rodada.",
            )

        if len(body.answers) < len(open_turn.questions):
            raise DiagnosisInterviewTurnError(
                "Responda todas as perguntas desta rodada.",
            )

    async def _execute_graph(
        self,
        *,
        phase: str,
        session: DiagnosisSession,
        answers: list | None,
    ) -> dict:
        run = GraphRun(
            graph_name="diagnosis_interview",
            user_id=session.intake.user_id,
            input={
                "phase": phase,
                "session": session.model_dump(),
                "answers": [answer.model_dump() for answer in answers or []],
            },
        )
        self._graph_store.save(run)
        try:
            result = await self._executor.execute(run, stream=False)
        except DiagnosisInterviewLlmError:
            raise
        assert isinstance(result, GraphRunResult)
        if result.run.status == "failed":
            raise DiagnosisInterviewLlmError(result.run.error or DiagnosisInterviewLlmError().retry_message)
        return _extract_graph_output(result)


_default_service: DiagnosisSessionService | None = None


def get_diagnosis_session_service() -> DiagnosisSessionService:
    global _default_service
    if _default_service is None:
        _default_service = DiagnosisSessionService()
    return _default_service


def set_diagnosis_session_service(service: DiagnosisSessionService | None) -> None:
    global _default_service
    _default_service = service
