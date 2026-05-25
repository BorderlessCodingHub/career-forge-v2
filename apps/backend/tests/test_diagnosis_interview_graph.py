"""Unit + integration tests — diagnosis_interview graph (HAC-43)."""

from __future__ import annotations

import pytest

from career_forge.ai.executor import GraphExecutor
from career_forge.ai.factory import AgentFactory
from career_forge.ai.graphs.diagnosis_interview import (
    DiagnosisInterviewGraphRunnable,
    run_interview_phase,
)
from career_forge.ai.llm.diagnosis_interview import (
    reset_diagnosis_interview_llm,
    set_diagnosis_interview_llm,
)
from career_forge.ai.run import GraphRun, GraphRunResult, InMemoryGraphRunStore
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    MAX_INTERVIEW_ROUNDS,
    MAX_QUESTIONS_PER_TURN,
    DiagnosisIntake,
    DiagnosisSession,
    InterviewAnswer,
)
from tests.mocks.diagnosis_interview_llm import MockDiagnosisInterviewLlm


@pytest.fixture(autouse=True)
def mock_llm() -> None:
    set_diagnosis_interview_llm(MockDiagnosisInterviewLlm())
    yield
    reset_diagnosis_interview_llm()


SAMPLE_INTAKE = DiagnosisIntake(
    user_id="test-user",
    goal_id="backend",
    motivation="Quero migrar de carreira para tecnologia e trabalhar com APIs.",
    years_xp="0-1",
)


@pytest.fixture
def executor() -> GraphExecutor:
    return GraphExecutor(factory=AgentFactory(), store=InMemoryGraphRunStore())


class TestDiagnosisInterviewGraph:
    def test_factory_registers_graph(self) -> None:
        factory = AgentFactory()
        runnable = factory.get("diagnosis_interview")
        assert isinstance(runnable, DiagnosisInterviewGraphRunnable)
        assert runnable.graph_name == "diagnosis_interview"

    @pytest.mark.asyncio
    async def test_start_returns_one_to_two_questions(self) -> None:
        session = DiagnosisSession(session_id="sess-1", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        assert output["status"] == "asking"
        questions = output["questions"]
        assert 1 <= len(questions) <= MAX_QUESTIONS_PER_TURN
        assert output["mapping_progress"]

    @pytest.mark.asyncio
    async def test_golden_path_completes_with_diagnosis(self) -> None:
        session = DiagnosisSession(session_id="sess-golden", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        session = DiagnosisSession.model_validate(output["session"])

        for _ in range(MAX_INTERVIEW_ROUNDS):
            if output["status"] == "complete":
                break
            questions = output["questions"]
            answers = [
                InterviewAnswer(
                    question_id=question["id"],
                    text="Resposta detalhada com mais de oito caracteres sobre minha experiência.",
                )
                for question in questions
            ]
            output = await run_interview_phase(
                phase="turn",
                session=session,
                answers=answers,
            )
            session = DiagnosisSession.model_validate(output["session"])

        assert output["status"] == "complete"
        diagnosis = DiagnosisResponse.model_validate(output["diagnosis"])
        assert diagnosis.profile.track_id == "backend-beginner"
        assert diagnosis.strengths
        assert diagnosis.gaps

    @pytest.mark.asyncio
    async def test_execute_collect_via_graph_executor(self, executor: GraphExecutor) -> None:
        session = DiagnosisSession(session_id="sess-exec", intake=SAMPLE_INTAKE)
        run = GraphRun(
            graph_name="diagnosis_interview",
            user_id="test-user",
            input={"phase": "start", "session": session.model_dump(), "answers": []},
        )
        result = await executor.execute(run, stream=False)
        assert isinstance(result, GraphRunResult)
        assert result.run.status == "completed"
        assert result.run.output is not None
        inner = result.run.output.get("output") or result.run.output
        assert inner["status"] == "asking"
        assert len(inner["questions"]) >= 1


class TestSaturationGuardrails:
    @pytest.mark.asyncio
    async def test_max_rounds_enforced(self) -> None:
        session = DiagnosisSession(session_id="sess-max", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        session = DiagnosisSession.model_validate(output["session"])

        turns = 0
        while output["status"] == "asking" and turns < MAX_INTERVIEW_ROUNDS + 2:
            answers = [
                InterviewAnswer(
                    question_id=question["id"],
                    text="Resposta curta mas válida com contexto suficiente aqui.",
                )
                for question in output["questions"]
            ]
            output = await run_interview_phase(
                phase="turn",
                session=session,
                answers=answers,
            )
            session = DiagnosisSession.model_validate(output["session"])
            turns += 1

        assert output["status"] == "complete"
        assert session.round_count <= MAX_INTERVIEW_ROUNDS
