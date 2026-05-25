"""Diagnosis interview LLM — OpenAI via langchain."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from career_forge.config import settings
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    CTRR_DIMENSION_LABELS,
    CTRR_DIMENSION_KEYS,
    MAX_QUESTIONS_PER_TURN,
    BeliefState,
    CvSignals,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
)

logger = logging.getLogger(__name__)

RETRY_MESSAGE = (
    "A IA não respondeu agora. Tente novamente em alguns segundos — suas respostas foram salvas."
)


class DiagnosisInterviewLlmError(Exception):
    """LLM call failed — API should surface retry message."""

    def __init__(self, message: str = RETRY_MESSAGE) -> None:
        super().__init__(message)
        self.retry_message = message


@runtime_checkable
class DiagnosisInterviewLlm(Protocol):
    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
    ) -> BeliefState: ...

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
    ) -> BeliefState: ...

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
    ) -> list[InterviewQuestion]: ...

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
    ) -> DiagnosisResponse: ...


def _parse_json_payload(raw: str) -> Any:
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        text = fence.group(1).strip()
    return json.loads(text)


def _belief_from_dict(payload: dict[str, Any]) -> BeliefState:
    dims_raw = payload.get("dimensions") or payload
    base = BeliefState.empty()
    for key in CTRR_DIMENSION_KEYS:
        if key in dims_raw and isinstance(dims_raw[key], dict):
            item = dims_raw[key]
            base.dimensions[key] = RubricDimension(
                key=key,
                label=str(item.get("label") or CTRR_DIMENSION_LABELS[key]),
                confidence=min(1.0, max(0.0, float(item.get("confidence", 0)))),
                evidence=[str(e) for e in item.get("evidence") or []],
            )
    return base


def _questions_from_list(payload: list[Any], round_count: int) -> list[InterviewQuestion]:
    questions: list[InterviewQuestion] = []
    for index, item in enumerate(payload[:MAX_QUESTIONS_PER_TURN]):
        if not isinstance(item, dict):
            continue
        rubric_key = item.get("rubric_key")
        if rubric_key not in CTRR_DIMENSION_KEYS:
            continue
        question_text = item.get("question")
        example_text = item.get("example_of_answer")
        if not question_text or not example_text:
            raise DiagnosisInterviewLlmError(
                "A IA retornou perguntas incompletas. Tente novamente em alguns segundos.",
            )
        qid = str(item.get("id") or f"q-r{round_count + 1}-{index + 1}")
        questions.append(
            InterviewQuestion(
                id=qid,
                topic=str(item.get("topic") or CTRR_DIMENSION_LABELS[rubric_key]),
                rubric_key=rubric_key,
                question=str(question_text),
                example_of_answer=str(example_text),
            ),
        )
    return questions


class OpenAiDiagnosisInterviewLlm:
    """OpenAI-backed Judge + Interviewer via langchain."""

    def __init__(self, model: str) -> None:
        if not model.strip():
            raise DiagnosisInterviewLlmError(
                "DIAGNOSIS_INTERVIEW_MODEL não configurado. Defina em .env.",
            )
        self._model = model.strip()

    def _chat(self):
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=self._model, temperature=0.2)

    async def _invoke_json(self, system: str, user: str) -> Any:
        from langchain_core.messages import HumanMessage, SystemMessage

        try:
            response = await self._chat().ainvoke(
                [SystemMessage(content=system), HumanMessage(content=user)],
            )
            content = response.content
            if not isinstance(content, str):
                msg = "LLM returned non-text content"
                raise DiagnosisInterviewLlmError(msg)
            return _parse_json_payload(content)
        except DiagnosisInterviewLlmError:
            raise
        except Exception as exc:
            logger.exception("Diagnosis interview LLM call failed")
            raise DiagnosisInterviewLlmError(RETRY_MESSAGE) from exc

    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
    ) -> BeliefState:
        from career_forge.ai.prompts.diagnosis_interview import JUDGE_SYSTEM

        payload = {
            "intake": intake.model_dump(exclude={"cv"}),
            "cv_signals": cv_signals.model_dump() if cv_signals else None,
            "cv_text_excerpt": (cv_text or "")[:2000],
            "task": "initialize_belief",
        }
        parsed = await self._invoke_json(JUDGE_SYSTEM, json.dumps(payload, ensure_ascii=False))
        if not isinstance(parsed, dict):
            raise DiagnosisInterviewLlmError(
                "A IA retornou um mapa de competências inválido. Tente novamente.",
            )
        return _belief_from_dict(parsed)

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
    ) -> BeliefState:
        from career_forge.ai.prompts.diagnosis_interview import JUDGE_SYSTEM

        payload = {
            "intake": intake.model_dump(exclude={"cv"}),
            "belief": belief.model_dump(),
            "transcript": [turn.model_dump() for turn in transcript],
            "new_answers": [answer.model_dump() for answer in answers],
            "task": "update_belief",
        }
        parsed = await self._invoke_json(JUDGE_SYSTEM, json.dumps(payload, ensure_ascii=False))
        if not isinstance(parsed, dict):
            raise DiagnosisInterviewLlmError(
                "A IA retornou um mapa de competências inválido. Tente novamente.",
            )
        return _belief_from_dict(parsed)

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
    ) -> list[InterviewQuestion]:
        from career_forge.ai.prompts.diagnosis_interview import INTERVIEWER_SYSTEM

        payload = {
            "intake": intake.model_dump(exclude={"cv"}),
            "belief": belief.model_dump(),
            "transcript": [turn.model_dump() for turn in transcript],
            "round_count": round_count,
            "max_questions": MAX_QUESTIONS_PER_TURN,
            "unsaturated": belief.unsaturated_keys(),
        }
        parsed = await self._invoke_json(
            INTERVIEWER_SYSTEM,
            json.dumps(payload, ensure_ascii=False),
        )
        if isinstance(parsed, dict) and "questions" in parsed:
            parsed = parsed["questions"]
        if not isinstance(parsed, list):
            raise DiagnosisInterviewLlmError(
                "A IA retornou perguntas inválidas. Tente novamente em alguns segundos.",
            )
        questions = _questions_from_list(parsed, round_count)
        if not questions and belief.unsaturated_keys():
            raise DiagnosisInterviewLlmError(
                "A IA não gerou perguntas para continuar. Tente novamente em alguns segundos.",
            )
        return questions

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
    ) -> DiagnosisResponse:
        from career_forge.ai.prompts.diagnosis_interview import FINALIZE_SYSTEM

        payload = {
            "intake": intake.model_dump(exclude={"cv"}),
            "belief": belief.model_dump(),
            "task": "finalize_diagnosis",
        }
        parsed = await self._invoke_json(
            FINALIZE_SYSTEM,
            json.dumps(payload, ensure_ascii=False),
        )
        if not isinstance(parsed, dict):
            raise DiagnosisInterviewLlmError
        return DiagnosisResponse.model_validate(parsed)


_override_llm: DiagnosisInterviewLlm | None = None


def set_diagnosis_interview_llm(client: DiagnosisInterviewLlm | None) -> None:
    global _override_llm
    _override_llm = client


def reset_diagnosis_interview_llm() -> None:
    set_diagnosis_interview_llm(None)


def get_diagnosis_interview_llm() -> DiagnosisInterviewLlm:
    if _override_llm is not None:
        return _override_llm

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise DiagnosisInterviewLlmError(
            "OPENAI_API_KEY não configurada. Configure a chave em .env antes de usar o diagnóstico.",
        )
    return OpenAiDiagnosisInterviewLlm(model=settings.diagnosis_interview_model)


def new_question_id(prefix: str = "q") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"
