"""Diagnosis interview LLM — OpenAI via langchain with mock fallback for tests."""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from career_forge.schemas.diagnosis import DiagnosisProfile, DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    CTRR_DIMENSION_LABELS,
    CTRR_DIMENSION_KEYS,
    MAX_QUESTIONS_PER_TURN,
    RubricDimensionKey,
    BeliefState,
    CvSignals,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewQuestion,
    InterviewTurn,
    RubricDimension,
    SATURATION_CONFIDENCE_THRESHOLD,
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
        qid = str(item.get("id") or f"q-r{round_count + 1}-{index + 1}")
        questions.append(
            InterviewQuestion(
                id=qid,
                topic=str(item.get("topic") or CTRR_DIMENSION_LABELS[rubric_key]),
                rubric_key=rubric_key,
                question=str(item.get("question") or "Conte mais sobre sua experiência."),
                example_of_answer=str(
                    item.get("example_of_answer") or "Ex.: estou aprendendo aos poucos.",
                ),
            ),
        )
    return questions


class MockDiagnosisInterviewLlm:
    """Deterministic LLM for tests and local dev without API key."""

    QUESTION_BANK: dict[RubricDimensionKey, tuple[str, str]] = {
        "learning_stage": (
            "Como você descreveria seu nível atual com programação?",
            "Ex.: estou no início, fiz um curso de JS há 3 meses.",
        ),
        "project_scope": (
            "Qual foi o maior projeto que você já construiu ou tentou construir?",
            "Ex.: um todo app, uma API simples, um site estático.",
        ),
        "background_context": (
            "De onde você vem e como está estudando tecnologia hoje?",
            "Ex.: migrei de outra área, estudo sozinho à noite.",
        ),
        "hands_on_evidence": (
            "Conte algo concreto que você já fez ou tentou fazer na prática.",
            "Ex.: subi um projeto no GitHub, fiz exercícios de lógica.",
        ),
        "git": (
            "Você já usou Git ou GitHub em algum projeto?",
            "Ex.: clone, commit, push — mesmo que básico.",
        ),
        "client_server": (
            "Consegue explicar, com suas palavras, frontend vs backend?",
            "Ex.: frontend é o que o usuário vê; backend processa dados.",
        ),
        "http_apis": (
            "Você já fez ou viu uma requisição HTTP ou chamada de API?",
            "Ex.: GET/POST, JSON, status code 200 ou 404.",
        ),
        "database": (
            "Já trabalhou ou ouviu falar de banco de dados em algum projeto?",
            "Ex.: salvar dados de um formulário, SQL básico.",
        ),
    }

    async def initialize_belief(
        self,
        intake: DiagnosisIntake,
        cv_signals: CvSignals | None,
        cv_text: str | None,
    ) -> BeliefState:
        belief = BeliefState.empty()
        merged = intake.motivation.lower()

        if intake.years_xp:
            boost = {"0-1": 0.35, "1-3": 0.5, "3-5": 0.65, "5+": 0.75}.get(intake.years_xp, 0.3)
            belief.dimensions["learning_stage"] = RubricDimension(
                key="learning_stage",
                label=CTRR_DIMENSION_LABELS["learning_stage"],
                confidence=boost,
                evidence=[f"Autodeclaração: {intake.years_xp} anos de experiência"],
            )
            belief.dimensions["background_context"] = RubricDimension(
                key="background_context",
                label=CTRR_DIMENSION_LABELS["background_context"],
                confidence=min(0.7, boost),
                evidence=[intake.motivation[:120]],
            )

        if cv_signals:
            if cv_signals.skills:
                if any(s.lower().find("git") >= 0 for s in cv_signals.skills):
                    belief.dimensions["git"] = RubricDimension(
                        key="git",
                        label=CTRR_DIMENSION_LABELS["git"],
                        confidence=0.78,
                        evidence=[f"CV menciona: {', '.join(cv_signals.skills[:3])}"],
                    )
                if any("api" in s.lower() or "http" in s.lower() for s in cv_signals.skills):
                    belief.dimensions["http_apis"] = RubricDimension(
                        key="http_apis",
                        label=CTRR_DIMENSION_LABELS["http_apis"],
                        confidence=0.76,
                        evidence=["CV menciona APIs/HTTP"],
                    )
            if cv_signals.roles:
                belief.dimensions["hands_on_evidence"] = RubricDimension(
                    key="hands_on_evidence",
                    label=CTRR_DIMENSION_LABELS["hands_on_evidence"],
                    confidence=0.72,
                    evidence=[f"CV: {cv_signals.roles[0]}"],
                )

        if any(token in merged for token in ("javascript", "js", "program")):
            belief.dimensions["learning_stage"].confidence = max(
                belief.dimensions["learning_stage"].confidence,
                0.55,
            )
            belief.dimensions["learning_stage"].evidence.append("Motivação menciona programação")

        return belief

    async def update_belief(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        answers: list[InterviewAnswer],
    ) -> BeliefState:
        del intake
        updated = belief.model_copy(deep=True)
        answer_by_qid = {answer.question_id: answer.text for answer in answers}

        last_turn = transcript[-1] if transcript else None
        if not last_turn:
            return updated

        for question in last_turn.questions:
            text = answer_by_qid.get(question.id, "")
            if not text:
                continue
            score = min(0.85, 0.45 + len(text) / 120)
            dim = updated.dimensions[question.rubric_key]
            updated.dimensions[question.rubric_key] = RubricDimension(
                key=question.rubric_key,
                label=dim.label,
                confidence=max(dim.confidence, score),
                evidence=[*dim.evidence, text[:160]],
            )
        return updated

    async def plan_questions(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
        transcript: list[InterviewTurn],
        round_count: int,
    ) -> list[InterviewQuestion]:
        del intake, transcript
        unsaturated = belief.unsaturated_keys(SATURATION_CONFIDENCE_THRESHOLD)
        if not unsaturated:
            return []

        questions: list[InterviewQuestion] = []
        for index, key in enumerate(unsaturated[:MAX_QUESTIONS_PER_TURN]):
            prompt, example = self.QUESTION_BANK[key]
            questions.append(
                InterviewQuestion(
                    id=f"q-r{round_count + 1}-{index + 1}",
                    topic=CTRR_DIMENSION_LABELS[key],
                    rubric_key=key,
                    question=prompt,
                    example_of_answer=example,
                ),
            )
        return questions

    async def finalize_diagnosis(
        self,
        belief: BeliefState,
        intake: DiagnosisIntake,
    ) -> DiagnosisResponse:
        mastery = {
            "js": int(belief.dimensions["learning_stage"].confidence * 100),
            "git": int(belief.dimensions["git"].confidence * 100),
            "http": int(belief.dimensions["http_apis"].confidence * 100),
            "db": int(belief.dimensions["database"].confidence * 100),
            "rest": int(belief.dimensions["client_server"].confidence * 40),
            "auth": 0,
            "final": 0,
        }
        strengths: list[str] = []
        gaps: list[str] = []

        if belief.dimensions["learning_stage"].confidence >= 0.55:
            strengths.append("Motivação clara e noção do próprio estágio de aprendizado")
        if belief.dimensions["git"].confidence >= 0.6:
            strengths.append("Já tem exposição a Git/versionamento")
        if belief.dimensions["http_apis"].confidence >= 0.55:
            strengths.append("Familiaridade inicial com HTTP e APIs")

        if belief.dimensions["http_apis"].confidence < 0.6:
            gaps.append("HTTP e APIs REST — métodos, status codes e contrato")
        if belief.dimensions["database"].confidence < 0.6:
            gaps.append("Banco relacional — modelagem e SQL aplicado")
        if belief.dimensions["git"].confidence < 0.55:
            gaps.append("Git colaborativo — branches, merge e fluxo em equipe")

        if not strengths:
            strengths.append("Motivação clara sobre o objetivo de carreira escolhido")
        if len(gaps) < 2:
            gaps.append("Persistência relacional — modelagem e SQL aplicado")

        priorities = []
        for node_id, key in (
            ("http", "http_apis"),
            ("git", "git"),
            ("db", "database"),
        ):
            if belief.dimensions[key].confidence < 0.7:
                priorities.append(node_id)
        if not priorities:
            priorities = ["http", "git", "db"]

        label = "Iniciante em transição para backend"
        if intake.goal_id == "backend":
            label = "Iniciante focado em backend"

        return DiagnosisResponse(
            profile=DiagnosisProfile(
                label=label,
                track_id="backend-beginner",
                persona_slug="transicao_iniciante",
            ),
            strengths=strengths[:3],
            gaps=gaps[:4],
            starting_priorities=priorities[:3],
            estimated_mastery=mastery,
        )


class OpenAiDiagnosisInterviewLlm:
    """OpenAI-backed Judge + Interviewer via langchain."""

    def __init__(self, model: str = "gpt-4o-mini") -> None:
        self._model = model

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
        return _belief_from_dict(parsed if isinstance(parsed, dict) else {})

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
        return _belief_from_dict(parsed if isinstance(parsed, dict) else belief.model_dump())

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
            return []
        return _questions_from_list(parsed, round_count)

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

    mode = os.getenv("DIAGNOSIS_LLM_MODE", "auto").lower()
    if mode == "mock":
        return MockDiagnosisInterviewLlm()

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if mode == "openai" or (mode == "auto" and api_key):
        if not api_key:
            raise DiagnosisInterviewLlmError(
                "OPENAI_API_KEY não configurada. Configure a chave ou use DIAGNOSIS_LLM_MODE=mock.",
            )
        return OpenAiDiagnosisInterviewLlm()

    return MockDiagnosisInterviewLlm()


def new_question_id(prefix: str = "q") -> str:
    return f"{prefix}-{uuid4().hex[:8]}"
