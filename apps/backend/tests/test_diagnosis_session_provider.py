"""CAR-137 — a diagnosis session keeps the Run provider from its start.

Seams:
- Diagnosis session start and later turns (the stored Run provider)
- Diagnosis interview ChatOpenAI wire (prefix, bare cost name, missing key)
"""

from __future__ import annotations

from unittest.mock import patch

import pytest
from sqlalchemy import delete
from sqlalchemy.orm import Session

from career_forge.ai.llm.diagnosis_interview import (
    DiagnosisInterviewLlmError,
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.ai.llm.model_chat import current_run_provider
from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.operator import Operator
from career_forge.db.models.provider_switch import ProviderSwitch
from career_forge.db.session import SessionLocal
from career_forge.schemas.diagnosis_interview import (
    DiagnosisIntake,
    DiagnosisSession,
    InterviewAnswer,
    InterviewQuestion,
    InterviewStartRequest,
    InterviewTurn,
    InterviewTurnRequest,
)
from career_forge.services.diagnosis_session import (
    DiagnosisSessionService,
    InMemoryDiagnosisSessionStore,
)
from career_forge.services.provider_switch import write_provider_switch
from tests.mocks.diagnosis_interview_llm import MockDiagnosisInterviewLlm

_OPERATOR_EMAIL = "car-137-access@borderless.com"
_BLAND = "A short note with no extra detail."


class _RecordingLlm(MockDiagnosisInterviewLlm):
    """Records the Run provider bound while each model-chat step runs."""

    def __init__(self) -> None:
        self.providers: list[str] = []

    def _note(self) -> None:
        self.providers.append(current_run_provider())

    async def initialize_belief(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self._note()
        return await super().initialize_belief(*args, **kwargs)

    async def update_belief(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self._note()
        return await super().update_belief(*args, **kwargs)

    async def finalize_diagnosis(self, *args, **kwargs):  # noqa: ANN002, ANN003
        self._note()
        return await super().finalize_diagnosis(*args, **kwargs)


def _access_operator(session: Session) -> OperatorPrincipal:
    row = Operator(email=_OPERATOR_EMAIL, desk_roles="access")
    session.add(row)
    session.flush()
    return OperatorPrincipal(email=row.email, operator_id=row.id, desk_roles="access")


@pytest.fixture
def switch_session() -> Session:
    session = SessionLocal()
    session.execute(delete(ProviderSwitch))
    session.execute(delete(Operator).where(Operator.email == _OPERATOR_EMAIL))
    session.commit()
    try:
        yield session
    finally:
        session.execute(delete(ProviderSwitch))
        session.execute(delete(Operator).where(Operator.email == _OPERATOR_EMAIL))
        session.commit()
        session.close()


def _arm(session: Session, principal: OperatorPrincipal, *, on: bool) -> None:
    write_provider_switch(session, principal=principal, on=on)
    session.commit()


def _answers(questions: list[InterviewQuestion]) -> InterviewTurnRequest:
    return InterviewTurnRequest(
        answers=[
            InterviewAnswer(question_id=question.id, text=_BLAND)
            for question in questions
        ],
    )


def _start_body() -> InterviewStartRequest:
    return InterviewStartRequest(
        user_id="learner-137",
        goal_id="rag-engineer",
        motivation="I want a concrete path into retrieval systems.",
        years_xp="0-1",
    )


def _service(recorder: _RecordingLlm) -> tuple[DiagnosisSessionService, InMemoryDiagnosisSessionStore]:
    set_diagnosis_interview_llm(recorder)
    store = InMemoryDiagnosisSessionStore()
    return DiagnosisSessionService(session_store=store), store


@pytest.fixture
def interview_llm() -> _RecordingLlm:
    recorder = _RecordingLlm()
    set_diagnosis_interview_llm(recorder)
    yield recorder
    reset_diagnosis_interview_llm()


@pytest.mark.asyncio
async def test_flip_between_turn_2_and_turn_3_keeps_one_provider_for_the_session(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    interview_llm: _RecordingLlm,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)
    service, store = _service(interview_llm)

    started = await service.start_interview(_start_body())
    pinned = store.get(started.session_id)
    assert pinned is not None
    assert pinned.run_provider == "gateway"
    assert "run_provider" not in pinned.model_dump()
    assert started.status == "asking"

    turn_2 = await service.submit_turn(started.session_id, _answers(started.questions))
    assert turn_2.status == "asking"
    assert turn_2.questions

    _arm(switch_session, principal, on=False)
    before_turn_3 = len(interview_llm.providers)

    turn_3 = await service.submit_turn(turn_2.session_id, _answers(turn_2.questions))

    assert turn_3.status == "complete"
    assert interview_llm.providers
    assert interview_llm.providers[:before_turn_3]
    assert set(interview_llm.providers) == {"gateway"}
    assert interview_llm.providers[before_turn_3:]
    kept = store.get(started.session_id)
    assert kept is not None
    assert kept.run_provider == "gateway"


def test_diagnosis_interview_wire_uses_the_bound_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bare id on OpenAI, openai/ on the wire, cost burn keeps the bare name."""
    from career_forge.ai.llm.client import StructuredLlmClient
    from career_forge.ai.llm.model_chat import bound_run_provider
    from career_forge.services.cost_gate_report import group_usage_by_configured_model

    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")

    with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
        direct = StructuredLlmClient("gpt-5.4")
        with bound_run_provider("gateway"):
            gateway = StructuredLlmClient("openai/gpt-4.1-nano")

    assert direct.model == "gpt-5.4"
    assert chat.call_args_list[0].kwargs["model"] == "gpt-5.4"
    assert chat.call_args_list[0].kwargs["api_key"] == "sk-openai"
    assert "base_url" not in chat.call_args_list[0].kwargs

    assert gateway.model == "gpt-4.1-nano"
    assert chat.call_args_list[1].kwargs["model"] == "openai/gpt-4.1-nano"
    assert chat.call_args_list[1].kwargs["api_key"] == "sk-or"
    assert chat.call_args_list[1].kwargs["base_url"] == "https://openrouter.ai/api/v1"

    grouped = group_usage_by_configured_model(
        {"openai/gpt-4.1-nano": {"input_tokens": 4, "output_tokens": 2}},
    )
    assert grouped == {"gpt-4.1-nano": {"input_tokens": 4, "output_tokens": 2}}


@pytest.mark.asyncio
async def test_missing_gateway_key_fails_the_turn_without_using_openai(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    reset_diagnosis_interview_llm()
    store = InMemoryDiagnosisSessionStore()
    session = DiagnosisSession(
        session_id="11111111-1111-1111-1111-111111111111",
        intake=DiagnosisIntake(
            user_id="learner-137",
            goal_id="rag-engineer",
            motivation="I want a concrete path into retrieval systems.",
        ),
        run_provider="gateway",
        round_count=1,
        transcript=[
            InterviewTurn(
                questions=[
                    InterviewQuestion(
                        id="q-open",
                        topic="Proof",
                        rubric_key="hands_on_proof",
                        question="What have you tried?",
                        example_of_answer="A small notebook.",
                    ),
                ],
            ),
        ],
    )
    store.save(session)
    service = DiagnosisSessionService(session_store=store)

    with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
        with pytest.raises(DiagnosisInterviewLlmError):
            await service.submit_turn(
                session.session_id,
                InterviewTurnRequest(
                    answers=[InterviewAnswer(question_id="q-open", text=_BLAND)],
                ),
            )

    chat.assert_not_called()
    kept = store.get(session.session_id)
    assert kept is not None
    assert kept.run_provider == "gateway"


@pytest.mark.asyncio
async def test_missing_direct_key_fails_the_turn_without_using_the_gateway(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    reset_diagnosis_interview_llm()
    store = InMemoryDiagnosisSessionStore()
    session = DiagnosisSession(
        session_id="33333333-3333-3333-3333-333333333333",
        intake=DiagnosisIntake(
            user_id="learner-137",
            goal_id="rag-engineer",
            motivation="I want a concrete path into retrieval systems.",
        ),
        run_provider="direct",
        round_count=1,
        transcript=[
            InterviewTurn(
                questions=[
                    InterviewQuestion(
                        id="q-open",
                        topic="Proof",
                        rubric_key="hands_on_proof",
                        question="What have you tried?",
                        example_of_answer="A small notebook.",
                    ),
                ],
            ),
        ],
    )
    store.save(session)
    service = DiagnosisSessionService(session_store=store)

    with patch("career_forge.ai.llm.client.ChatOpenAI") as chat:
        with pytest.raises(DiagnosisInterviewLlmError):
            await service.submit_turn(
                session.session_id,
                InterviewTurnRequest(
                    answers=[InterviewAnswer(question_id="q-open", text=_BLAND)],
                ),
            )

    chat.assert_not_called()


@pytest.mark.asyncio
async def test_a_new_session_reads_the_switch_again(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    interview_llm: _RecordingLlm,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)
    service, store = _service(interview_llm)

    first = await service.start_interview(_start_body())
    _arm(switch_session, principal, on=False)
    second = await service.start_interview(_start_body())

    first_stored = store.get(first.session_id)
    second_stored = store.get(second.session_id)
    assert first_stored is not None
    assert second_stored is not None
    assert first_stored.run_provider == "gateway"
    assert second_stored.run_provider == "direct"


@pytest.mark.asyncio
async def test_returning_to_an_unfinished_session_keeps_the_provider_from_its_start(
    switch_session: Session,
    monkeypatch: pytest.MonkeyPatch,
    interview_llm: _RecordingLlm,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-openai")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or")
    principal = _access_operator(switch_session)
    _arm(switch_session, principal, on=True)
    service, store = _service(interview_llm)
    started = await service.start_interview(_start_body())

    returned = DiagnosisSessionService(session_store=store)
    _arm(switch_session, principal, on=False)
    turn = await returned.submit_turn(started.session_id, _answers(started.questions))

    assert turn.session_id == started.session_id
    assert set(interview_llm.providers) == {"gateway"}
    kept = store.get(started.session_id)
    assert kept is not None
    assert kept.run_provider == "gateway"


def test_postgres_session_keeps_the_provider_from_its_start() -> None:
    from uuid import UUID

    from sqlalchemy import delete as sql_delete

    from career_forge.db.models.diagnosis_session import DiagnosisSessionRecord
    from career_forge.services.diagnosis_session import PostgresDiagnosisSessionStore

    session = DiagnosisSession(
        session_id="44444444-4444-4444-4444-444444444444",
        intake=DiagnosisIntake(
            user_id="learner-137",
            goal_id="rag-engineer",
            motivation="I want a concrete path into retrieval systems.",
        ),
        run_provider="gateway",
    )
    store = PostgresDiagnosisSessionStore()
    store.save(session)
    try:
        restored = store.get(session.session_id)
        assert restored is not None
        assert restored.run_provider == "gateway"
    finally:
        db = SessionLocal()
        db.execute(
            sql_delete(DiagnosisSessionRecord).where(
                DiagnosisSessionRecord.id == UUID(session.session_id),
            ),
        )
        db.commit()
        db.close()
