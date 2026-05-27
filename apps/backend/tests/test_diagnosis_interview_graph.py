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
    goal_id="fullstack",
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
    async def test_start_returns_round_one_compound_question(self) -> None:
        session = DiagnosisSession(session_id="sess-1", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        assert output["status"] == "asking"
        questions = output["questions"]
        assert len(questions) == 1
        assert questions[0]["rubric_key"] == "hands_on_proof"
        assert output["mapping_progress"]

    @pytest.mark.asyncio
    async def test_round_two_returns_fixed_context_questions(self) -> None:
        session = DiagnosisSession(session_id="sess-r2", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        session = DiagnosisSession.model_validate(output["session"])

        answers = [
            InterviewAnswer(
                question_id=output["questions"][0]["id"],
                text="Resposta detalhada com mais de oito caracteres sobre minha experiência.",
            ),
        ]
        output = await run_interview_phase(
            phase="turn",
            session=session,
            answers=answers,
        )

        assert output["status"] == "asking"
        questions = output["questions"]
        assert len(questions) == 2
        assert [question["rubric_key"] for question in questions] == [
            "constraints",
            "background_transfer",
        ]

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
        assert diagnosis.profile.track_id == "fullstack-beginner"
        assert diagnosis.strengths
        assert diagnosis.gaps

    @pytest.mark.asyncio
    async def test_execute_stream_yields_interview_status_and_mapping(
        self,
        executor: GraphExecutor,
    ) -> None:
        session = DiagnosisSession(session_id="sess-stream", intake=SAMPLE_INTAKE)
        run = GraphRun(
            graph_name="diagnosis_interview",
            user_id="test-user",
            input={"phase": "start", "session": session.model_dump(), "answers": []},
        )
        event_iter = await executor.execute(run, stream=True)
        assert not isinstance(event_iter, GraphRunResult)

        collected = [event async for event in event_iter]
        types = [event["type"] for event in collected]

        assert "interview_status" in types
        assert "mapping_dimension" in types
        assert collected[-1]["type"] == "graph_complete"
        assert collected[-1]["output"]["status"] == "asking"
        assert collected[-1]["output"]["questions"]

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
    async def test_start_never_returns_asking_with_zero_questions(self) -> None:
        session = DiagnosisSession(session_id="sess-empty", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        if output["status"] == "asking":
            assert len(output["questions"]) >= 1
        else:
            assert output["status"] == "complete"
            assert output["diagnosis"] is not None

    @pytest.mark.asyncio
    async def test_cv_rich_belief_still_gets_questions(self) -> None:
        """CV-only high confidence must not skip interview via needs_clarification status."""

        class CvRichMock(MockDiagnosisInterviewLlm):
            async def initialize_belief(self, *args, **kwargs):  # noqa: ANN002, ANN003
                from career_forge.schemas.diagnosis_interview import (
                    PROFILE_DIMENSION_KEYS,
                    PROFILE_DIMENSION_LABELS,
                    BeliefState,
                    RubricDimension,
                )

                belief = BeliefState.empty()
                for key in PROFILE_DIMENSION_KEYS:
                    belief.dimensions[key] = RubricDimension(
                        key=key,
                        label=PROFILE_DIMENSION_LABELS[key],
                        confidence=0.65,
                        evidence=["CV menciona experiência avançada"],
                        status="needs_clarification",
                        note="CV sugere experiência — confirmar na entrevista",
                    )
                return belief

        set_diagnosis_interview_llm(CvRichMock())
        session = DiagnosisSession(session_id="sess-cv", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        assert output["status"] == "asking"
        assert len(output["questions"]) >= 1

    @pytest.mark.asyncio
    async def test_negative_hands_on_answer_still_gets_round_two(self) -> None:
        session = DiagnosisSession(session_id="sess-neg", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        session = DiagnosisSession.model_validate(output["session"])

        answers = [
            InterviewAnswer(
                question_id=output["questions"][0]["id"],
                text="Nunca fiz nada prático nesse caminho, nadinha.",
            ),
        ]
        output = await run_interview_phase(
            phase="turn",
            session=session,
            answers=answers,
        )
        session = DiagnosisSession.model_validate(output["session"])
        proof = session.belief.dimensions["hands_on_proof"]
        assert proof.status == "mapped"

        assert output["status"] == "asking"
        assert [question["rubric_key"] for question in output["questions"]] == [
            "constraints",
            "background_transfer",
        ]

    @pytest.mark.asyncio
    async def test_skips_round_two_when_answer_already_covers_context(self) -> None:
        session = DiagnosisSession(session_id="sess-skip-r2", intake=SAMPLE_INTAKE)
        output = await run_interview_phase(phase="start", session=session)
        session = DiagnosisSession.model_validate(output["session"])

        answers = [
            InterviewAnswer(
                question_id=output["questions"][0]["id"],
                text=(
                    "Nunca fiz projetos práticos em AI/ML, só estudo teórico por enquanto."
                ),
            ),
        ]
        output = await run_interview_phase(
            phase="turn",
            session=session,
            answers=answers,
        )

        assert output["status"] == "complete"
        assert output["diagnosis"] is not None

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
