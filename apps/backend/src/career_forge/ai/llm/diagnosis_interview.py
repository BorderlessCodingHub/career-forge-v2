"""Diagnosis interview LLM — OpenAI via LangChain structured output."""

from __future__ import annotations

import logging
from typing import Protocol, runtime_checkable
from uuid import uuid4

from career_forge.ai.llm.client import DEFAULT_KEY_ERROR, StructuredLlmClient
from career_forge.ai.llm.errors import DiagnosisInterviewLlmError, RETRY_MESSAGE
from career_forge.ai.llm.model_chat import ModelGatewayKeyMissing
from career_forge.ai.payloads.diagnosis_interview import (
    apply_transcript_overrides,
    build_interviewer_user_message,
    build_judge_user_message,
    closed_dimensions_from_transcript,
)
from career_forge.ai.prompts.diagnosis_interview import (
    finalize_system,
    interviewer_system,
    judge_system,
)
from career_forge.config import settings
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    MAX_QUESTIONS_PER_TURN,
    BeliefState,
    CvSignals,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
)
from career_forge.schemas.llm_outputs import (
    FinalizeDiagnosisOutput,
    InterviewerOutput,
    JudgeBeliefOutput,
)

logger = logging.getLogger(__name__)

_GATEWAY_KEY_MISSING = "The Model gateway key is missing. This turn cannot continue."
_DIRECT_KEY_MISSING = (
    "OPENAI_API_KEY is not configured. Set the key in .env before using diagnosis."
)


@runtime_checkable
class DiagnosisInterviewLlm(Protocol):
    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
        *,
        locale: str | None = None,
    ) -> BeliefState: ...

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
        *,
        locale: str | None = None,
    ) -> BeliefState: ...

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
        *,
        locale: str | None = None,
    ) -> list[InterviewQuestion]: ...

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        *,
        locale: str | None = None,
    ) -> DiagnosisResponse: ...


def _filter_interview_questions(
    belief: BeliefState,
    questions: list[InterviewQuestion],
    transcript: list[InterviewTurn],
) -> list[InterviewQuestion]:
    """Drop questions targeting closed or non-interviewable dimensions."""
    interviewable = set(belief.interviewable_keys())
    closed = closed_dimensions_from_transcript(transcript)
    filtered = [
        question
        for question in questions
        if question.rubric_key in interviewable and question.rubric_key not in closed
    ]
    return filtered[:MAX_QUESTIONS_PER_TURN]


def _effective_interviewable(
    belief: BeliefState,
    transcript: list[InterviewTurn],
) -> list[str]:
    closed = closed_dimensions_from_transcript(transcript)
    return [key for key in belief.interviewable_keys() if key not in closed]


class OpenAiDiagnosisInterviewLlm:
    """OpenAI-backed Judge + Interviewer using with_structured_output."""

    def __init__(self, model: str) -> None:
        try:
            self._client = StructuredLlmClient(model)
        except ValueError as exc:
            raise DiagnosisInterviewLlmError(
                "DIAGNOSIS_INTERVIEW_MODEL is not configured. Set it in .env.",
            ) from exc

    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
        *,
        locale: str | None = None,
    ) -> BeliefState:
        payload = build_judge_user_message(
            task="initialize_belief",
            intake=intake,
            cv_signals=cv_signals.model_dump() if cv_signals else None,
            cv_text_excerpt=(cv_text or "")[:2000],
        )
        output = await self._client.invoke(
            system=judge_system(locale),
            user=payload,
            schema=JudgeBeliefOutput,
            error_type=DiagnosisInterviewLlmError,
        )
        return output.to_belief_state()

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
        *,
        locale: str | None = None,
    ) -> BeliefState:
        payload = build_judge_user_message(
            task="update_belief",
            intake=intake,
            belief=belief,
            transcript=transcript,
            new_answers=answers,
        )
        output = await self._client.invoke(
            system=judge_system(locale),
            user=payload,
            schema=JudgeBeliefOutput,
            error_type=DiagnosisInterviewLlmError,
        )
        updated = output.to_belief_state()
        return apply_transcript_overrides(updated, transcript, locale=locale)

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
        *,
        locale: str | None = None,
    ) -> list[InterviewQuestion]:
        effective = _effective_interviewable(belief, transcript)
        if not effective:
            return []

        payload = build_interviewer_user_message(
            intake=intake,
            belief=belief,
            transcript=transcript,
            round_count=round_count,
            max_questions=MAX_QUESTIONS_PER_TURN,
        )
        output = await self._client.invoke(
            system=interviewer_system(locale),
            user=payload,
            schema=InterviewerOutput,
            error_type=DiagnosisInterviewLlmError,
        )
        questions = _filter_interview_questions(belief, output.questions, transcript)

        if not questions and not output.questions:
            raise DiagnosisInterviewLlmError(
                "AI did not generate questions to continue. Try again in a few seconds.",
            )
        if not questions and output.questions:
            logger.warning(
                "Interviewer returned %d question(s) but all were filtered (closed dims=%s)",
                len(output.questions),
                sorted(closed_dimensions_from_transcript(transcript)),
            )
        return questions

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        *,
        locale: str | None = None,
    ) -> DiagnosisResponse:
        payload = build_judge_user_message(
            task="finalize_diagnosis",
            intake=intake,
            belief=belief,
        )
        output = await self._client.invoke(
            system=finalize_system(locale),
            user=payload,
            schema=FinalizeDiagnosisOutput,
            error_type=DiagnosisInterviewLlmError,
        )
        return output.to_diagnosis_response(profile_score=belief.mean_confidence())


_override_llm: DiagnosisInterviewLlm | None = None


def set_diagnosis_interview_llm(client: DiagnosisInterviewLlm | None) -> None:
    global _override_llm
    _override_llm = client


def reset_diagnosis_interview_llm() -> None:
    set_diagnosis_interview_llm(None)


def get_diagnosis_interview_llm() -> DiagnosisInterviewLlm:
    if _override_llm is not None:
        return _override_llm

    try:
        return OpenAiDiagnosisInterviewLlm(model=settings.diagnosis_interview_model)
    except ModelGatewayKeyMissing as exc:
        raise DiagnosisInterviewLlmError(_GATEWAY_KEY_MISSING) from exc
    except RuntimeError as exc:
        if str(exc) != DEFAULT_KEY_ERROR:
            raise
        raise DiagnosisInterviewLlmError(_DIRECT_KEY_MISSING) from exc


def new_question_id(prefix: str = "q") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"


# Backward-compatible re-export
__all__ = [
    "DiagnosisInterviewLlm",
    "DiagnosisInterviewLlmError",
    "RETRY_MESSAGE",
    "get_diagnosis_interview_llm",
    "new_question_id",
    "reset_diagnosis_interview_llm",
    "set_diagnosis_interview_llm",
]
