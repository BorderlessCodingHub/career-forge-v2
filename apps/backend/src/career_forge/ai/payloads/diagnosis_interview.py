"""Structured LLM payloads for diagnosis interview — optimized from LangSmith traces."""

from __future__ import annotations

import re
from typing import Any

from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_LABELS,
    BeliefState,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewTurn,
    RubricDimensionKey,
)

_NEGATIVE_PROOF_RE = re.compile(
    r"\b(nunca|nadinha|nada|zero|sem pr[aá]tica|sem projeto|n[aã]o fiz|n[aã]o tenho|s[oó] teoria)\b",
    re.IGNORECASE,
)

_CONSTRAINTS_RE = re.compile(
    r"\b(hora[s]?|semana|dia[s]?|noite|portugu[eê]s|ingl[eê]s|budget|tempo)\b",
    re.IGNORECASE,
)


def detect_negative_hands_on(text: str) -> bool:
    return bool(_NEGATIVE_PROOF_RE.search(text))


def closed_dimensions_from_transcript(
    transcript: list[InterviewTurn],
) -> set[RubricDimensionKey]:
    """Dimensions the user already answered — including explicit negatives."""
    closed: set[RubricDimensionKey] = set()
    for turn in transcript:
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            text = answer_by_qid.get(question.id, "").strip()
            if not text:
                continue
            closed.add(question.rubric_key)
            if question.rubric_key == "hands_on_proof" or detect_negative_hands_on(text):
                if detect_negative_hands_on(text):
                    closed.add("hands_on_proof")
            if question.rubric_key == "constraints" or _CONSTRAINTS_RE.search(text):
                closed.add("constraints")
            if question.rubric_key == "learning_velocity" or _CONSTRAINTS_RE.search(text):
                closed.add("learning_velocity")
    return closed


def build_transcript_digest(transcript: list[InterviewTurn]) -> str:
    if not transcript:
        return "(sem rodadas anteriores)"
    lines: list[str] = []
    for index, turn in enumerate(transcript, start=1):
        lines.append(f"### Rodada {index}")
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            answer = answer_by_qid.get(question.id, "").strip() or "(sem resposta)"
            lines.append(f"- P [{question.rubric_key}]: {question.question}")
            lines.append(f"  R: {answer}")
        lines.append("")
    return "\n".join(lines).strip()


def build_belief_snapshot(belief: BeliefState) -> list[dict[str, Any]]:
    return [
        {
            "key": key,
            "label": PROFILE_DIMENSION_LABELS[key],
            "status": dim.status,
            "confidence": round(dim.confidence, 2),
            "note": dim.note,
        }
        for key, dim in belief.dimensions.items()
    ]


def apply_schedule_overrides(belief: BeliefState, transcript: list[InterviewTurn]) -> BeliefState:
    """Map constraints/learning_velocity when user gave hours or routine."""
    updated = belief.model_copy(deep=True)
    for turn in transcript:
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            text = answer_by_qid.get(question.id, "")
            if not text or not _CONSTRAINTS_RE.search(text):
                continue
            for key in ("constraints", "learning_velocity"):
                dim = updated.dimensions[key]
                updated.dimensions[key] = dim.model_copy(
                    update={
                        "status": "mapped",
                        "confidence": max(dim.confidence, 0.76),
                        "note": "Rotina/tempo mencionados pelo usuário",
                        "evidence": [*dim.evidence, text[:120]][:5],
                    },
                )
    return updated


def apply_negative_proof_overrides(belief: BeliefState, transcript: list[InterviewTurn]) -> BeliefState:
    """Deterministic guard: explicit 'nunca fiz' closes hands_on_proof."""
    updated = belief.model_copy(deep=True)
    for turn in transcript:
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            text = answer_by_qid.get(question.id, "")
            if not text or not detect_negative_hands_on(text):
                continue
            dim = updated.dimensions["hands_on_proof"]
            updated.dimensions["hands_on_proof"] = dim.model_copy(
                update={
                    "status": "mapped",
                    "confidence": max(dim.confidence, 0.68),
                    "note": "Sem prática hands-on ainda — resposta negativa explícita do usuário",
                    "evidence": [*dim.evidence, text[:120]][:5],
                },
            )
    return updated


def apply_transcript_overrides(belief: BeliefState, transcript: list[InterviewTurn]) -> BeliefState:
    return apply_schedule_overrides(apply_negative_proof_overrides(belief, transcript), transcript)


def build_judge_user_message(
    *,
    task: str,
    intake: DiagnosisIntake,
    belief: BeliefState | None = None,
    transcript: list[InterviewTurn] | None = None,
    new_answers: list[InterviewAnswer] | None = None,
    cv_signals: dict[str, Any] | None = None,
    cv_text_excerpt: str | None = None,
) -> str:
    sections = [
        f"## task\n{task}",
        "## intake",
        f"- goal_id: {intake.goal_id}",
        f"- motivation: {intake.motivation}",
        f"- years_xp: {intake.years_xp or 'não informado'}",
    ]
    if cv_signals:
        sections.append(f"- cv_signals: {cv_signals}")
    if cv_text_excerpt:
        sections.append(f"- cv_excerpt: {cv_text_excerpt[:1500]}")
    if belief is not None:
        sections.append("## belief_atual")
        for item in build_belief_snapshot(belief):
            sections.append(
                f"- {item['key']}: {item['status']} ({item['confidence']}) — {item['note']}",
            )
    if transcript:
        sections.append("## transcript")
        sections.append(build_transcript_digest(transcript))
    if new_answers:
        sections.append("## new_answers")
        for answer in new_answers:
            sections.append(f"- {answer.question_id}: {answer.text}")
    return "\n".join(sections)


def build_interviewer_user_message(
    *,
    intake: DiagnosisIntake,
    belief: BeliefState,
    transcript: list[InterviewTurn],
    round_count: int,
    max_questions: int,
) -> str:
    closed = closed_dimensions_from_transcript(transcript)
    interviewable = [key for key in belief.interviewable_keys() if key not in closed]

    do_not_ask: list[str] = []
    for key in closed:
        if key in belief.interviewable_keys() or belief.dimensions[key].status == "mapped":
            do_not_ask.append(f"{key} (já respondido no transcript)")

    for key, dim in belief.dimensions.items():
        if dim.status == "mapped":
            do_not_ask.append(f"{key} (mapped)")

    if "hands_on_proof" in closed:
        do_not_ask.append("hands_on_proof (resposta negativa — NÃO reformular)")

    sections = [
        f"## round_count\n{round_count}",
        f"## max_questions\n{max_questions}",
        f"## goal_id\n{intake.goal_id}",
        "## intake",
        f"- motivation: {intake.motivation}",
        f"- years_xp: {intake.years_xp or 'não informado'}",
        "## belief_snapshot",
    ]
    for item in build_belief_snapshot(belief):
        sections.append(
            f"- {item['key']}: {item['status']} ({item['confidence']}) — {item['note']}",
        )
    sections.extend(
        [
            f"## interviewable\n{interviewable or ['(nenhuma — retorne [])']}",
            "## do_not_ask",
        ],
    )
    sections.extend(f"- {line}" for line in do_not_ask or ["(nada)"])
    sections.extend(["## transcript", build_transcript_digest(transcript)])
    sections.extend(
        [
            "## instrucao_final",
            "Gere 0–2 perguntas APENAS para keys em interviewable.",
            "Se interviewable vazio, retorne questions: [].",
            "Nunca repita eixo já em do_not_ask.",
            "topic = label PT-BR (Prova prática, Contexto real), nunca rubric_key cru.",
        ],
    )
    return "\n".join(sections)
