"""Validation graph — rubric-based mastery interview (HAC-10)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.validation import ValidationRequest, ValidationResponse
from career_forge.services.assessment_rubric import (
    NEXT_ACTIONS,
    PASS_THRESHOLD,
    RUBRIC_GAPS,
    RUBRIC_STRENGTHS,
    keywords_for,
    score_answer,
)


def build_validation_response(payload: ValidationRequest) -> ValidationResponse:
    """Deterministic rubric evaluation from interview answers (no LLM for MVP)."""
    rubric = payload.rubric or [answer.question_id for answer in payload.answers]
    per_answer_scores: list[int] = []

    for index, answer in enumerate(payload.answers):
        keywords = keywords_for(payload.node_id, index, rubric)
        per_answer_scores.append(score_answer(answer.answer, keywords))

    score = sum(per_answer_scores) // max(len(per_answer_scores), 1)
    status = ValidationStatus.APROVADO if score >= PASS_THRESHOLD else ValidationStatus.REVISAR

    node_strengths = RUBRIC_STRENGTHS.get(payload.node_id, [])
    node_gaps = RUBRIC_GAPS.get(payload.node_id, [])

    strengths: list[str] = []
    gaps: list[str] = []

    for index, answer_score in enumerate(per_answer_scores):
        if answer_score >= 65 and index < len(node_strengths):
            strengths.append(node_strengths[index])
        elif answer_score < 55 and index < len(node_gaps):
            gaps.append(node_gaps[index])

    if not strengths:
        strengths.append(f"Demonstra esforço em explicar {payload.node_title} com palavras próprias")

    if not gaps:
        if status == ValidationStatus.REVISAR:
            gaps.append(f"Ainda faltam evidências concretas sobre critérios de {payload.node_title}")
        else:
            gaps.append("Aprofunde com exemplos reais de projeto na próxima rodada")

    if status == ValidationStatus.REVISAR and len(gaps) < 2:
        gaps.append("Respostas genéricas — faltam termos técnicos da rubrica")

    next_action = NEXT_ACTIONS.get(
        payload.node_id,
        f"Revise os critérios de {payload.node_title} e tente novamente com exemplos concretos.",
    )

    mentor_summary = (
        f"Para o mentor: validação de {payload.node_title} ({payload.node_id}) — "
        f"score {score}/100 ({status.value}). "
    )
    if gaps:
        mentor_summary += f"Lacunas: {'; '.join(gaps[:2])}. "
    if strengths:
        mentor_summary += f"Pontos fortes: {strengths[0]}. "
    mentor_summary += next_action

    return ValidationResponse(
        score=score,
        status=status,
        strengths=strengths[:3],
        gaps=gaps[:3],
        next_action=next_action,
        mentor_summary=mentor_summary,
    )


class ValidationGraphRunnable:
    """GraphRunnable that maps interview answers → ValidationResponse."""

    graph_name = "validation"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        payload = ValidationRequest.model_validate(input_data)
        result = build_validation_response(payload)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        yield emit_chain_stream(
            "evaluate_rubric",
            run_id,
            {
                "type": "progress",
                "step": "evaluate_rubric",
                "message": f"Avaliando evidências de {payload.node_title}",
            },
        )

        output = result.model_dump()
        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=output,
            input_data=input_data,
        )


def build_validation_graph() -> ValidationGraphRunnable:
    """Return configured validation graph runnable."""
    return ValidationGraphRunnable()
