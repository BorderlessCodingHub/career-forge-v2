"""Mock interview graph — 5–7 contextual questions recalibrate trail (HAC-14)."""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from typing import Any
from career_forge.ai.streaming.langchain_events import (
    LangChainStreamEvent,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    new_run_id,
)
from career_forge.services.assessment_rubric import (
    NEXT_ACTIONS,
    PASS_THRESHOLD,
    RUBRIC_GAPS,
    RUBRIC_STRENGTHS,
    keywords_for,
    score_answer,
)
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.mock_interview import MockInterviewRequest
from career_forge.schemas.validation import ValidationResponse


def _outcome_keywords(criterion: str) -> tuple[str, ...]:
    tokens = tuple(
        token for token in re.findall(r"[a-záàâãéêíóôõúç0-9]+", criterion.lower()) if len(token) > 3
    )
    return tokens or ("projeto", "aplicar", "exemplo", "prática")


def _gap_keywords(criterion: str) -> tuple[str, ...]:
    tokens = tuple(
        token for token in re.findall(r"[a-záàâãéêíóôõúç0-9]+", criterion.lower()) if len(token) > 3
    )
    return tokens + ("corrigir", "melhorar", "praticar", "exemplo")


def build_mock_interview_response(payload: MockInterviewRequest) -> ValidationResponse:
    """Evaluate 5–7 contextual answers with richer gap extraction."""
    rubric = payload.rubric or [answer.question_id for answer in payload.answers]
    per_answer_scores: list[int] = []
    answer_count = len(payload.answers)

    for index, answer in enumerate(payload.answers):
        if index < 3:
            keywords = keywords_for(payload.node_id, index, rubric)
        elif index < 5:
            criterion = rubric[index] if index < len(rubric) else answer.question_id
            keywords = _gap_keywords(criterion)
        else:
            criterion = rubric[index] if index < len(rubric) else answer.question_id
            keywords = _outcome_keywords(criterion)
        per_answer_scores.append(score_answer(answer.answer, keywords))

    base_scores = per_answer_scores[:3]
    extended_scores = per_answer_scores[3:]
    base_avg = sum(base_scores) // max(len(base_scores), 1)
    extended_avg = sum(extended_scores) // max(len(extended_scores), 1) if extended_scores else base_avg
    score = (base_avg * 60 + extended_avg * 40) // 100

    status = ValidationStatus.APROVADO if score >= PASS_THRESHOLD else ValidationStatus.REVISAR

    node_strengths = RUBRIC_STRENGTHS.get(payload.node_id, [])
    node_gaps = RUBRIC_GAPS.get(payload.node_id, [])

    strengths: list[str] = []
    gaps: list[str] = []

    for index, answer_score in enumerate(per_answer_scores[:3]):
        if answer_score >= 65 and index < len(node_strengths):
            strengths.append(node_strengths[index])
        elif answer_score < 55 and index < len(node_gaps):
            gaps.append(node_gaps[index])

    for index, answer_score in enumerate(per_answer_scores[3:5], start=3):
        gap_index = index - 3
        if answer_score < 60 and gap_index < len(node_gaps):
            gaps.append(f"[Follow-up] {node_gaps[gap_index]}")
        elif answer_score < 50:
            criterion = rubric[index] if index < len(rubric) else "critério contextual"
            gaps.append(f"Resposta superficial sobre: {criterion[:80]}")

    for index, answer_score in enumerate(per_answer_scores[5:], start=5):
        if answer_score < 55:
            criterion = rubric[index] if index < len(rubric) else "cenário prático"
            gaps.append(f"Cenário prático insuficiente: {criterion[:80]}")

    if not strengths:
        strengths.append(f"Demonstra esforço em explicar {payload.node_title} com palavras próprias")

    if not gaps:
        if status == ValidationStatus.REVISAR:
            gaps.append(f"Ainda faltam evidências concretas sobre critérios de {payload.node_title}")
        else:
            gaps.append("Aprofunde com exemplos reais de projeto na próxima rodada")

    if status == ValidationStatus.REVISAR and len(gaps) < 3:
        gaps.append("Respostas genéricas — faltam termos técnicos da rubrica e cenários aplicados")

    next_action = NEXT_ACTIONS.get(
        payload.node_id,
        f"Revise os critérios de {payload.node_title} e tente novamente com exemplos concretos.",
    )

    mentor_summary = (
        f"Para o mentor: mock interview de {payload.node_title} — "
        f"{answer_count} perguntas contextuais, score {score}/100 ({status.value}). "
    )
    if gaps:
        mentor_summary += f"Lacunas ({len(gaps)}): {'; '.join(gaps[:3])}. "
    if strengths:
        mentor_summary += f"Pontos fortes: {strengths[0]}. "
    mentor_summary += next_action

    return ValidationResponse(
        score=score,
        status=status,
        strengths=strengths[:4],
        gaps=gaps[:5],
        next_action=next_action,
        mentor_summary=mentor_summary,
    )


class MockInterviewGraphRunnable:
    """GraphRunnable that maps 5–7 mock interview answers → ValidationResponse."""

    graph_name = "mock_interview"

    async def astream_events(
        self,
        input_data: dict[str, Any],
        *,
        version: str = "v2",
    ) -> AsyncIterator[LangChainStreamEvent]:
        del version
        payload = MockInterviewRequest.model_validate(input_data)
        result = build_mock_interview_response(payload)
        run_id = new_run_id()

        yield emit_chain_start(self.graph_name, run_id)

        yield emit_chain_stream(
            "evaluate_contextual",
            run_id,
            {
                "type": "progress",
                "step": "evaluate_contextual",
                "message": (
                    f"Avaliando {len(payload.answers)} respostas contextuais de {payload.node_title}"
                ),
            },
        )

        output = result.model_dump()
        yield emit_chain_end(
            self.graph_name,
            run_id,
            output=output,
            input_data=input_data,
        )


def build_mock_interview_graph() -> MockInterviewGraphRunnable:
    """Return configured mock interview graph runnable."""
    return MockInterviewGraphRunnable()
