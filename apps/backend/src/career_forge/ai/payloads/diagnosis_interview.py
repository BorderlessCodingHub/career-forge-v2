"""Structured LLM payloads for diagnosis interview — optimized from LangSmith traces."""

from __future__ import annotations

import re
from typing import Any

from career_forge.ai.prompts.diagnosis_interview import interviewer_brief_for_goal
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_LABELS,
    BeliefState,
    DiagnosisIntake,
    InterviewAnswer,
    InterviewTurn,
    RubricDimensionKey,
)

_NEGATIVE_PROOF_RE = re.compile(
    r"\b("
    r"nunca|nadinha|nada|zero|sem pr[aá]tica|sem projeto|n[aã]o fiz|n[aã]o tenho|s[oó] teoria|"
    r"never|nothing|no practice|no projects|haven't built|have not built|theory only"
    r")\b",
    re.IGNORECASE,
)

_CONSTRAINTS_RE = re.compile(
    r"\b("
    r"hora[s]?|semana|dia[s]?|noite|portugu[eê]s|ingl[eê]s|budget|tempo|"
    r"hour[s]?|week|day[s]?|night|english|portuguese|time"
    r")\b",
    re.IGNORECASE,
)

_CONSTRAINTS_CLEAR_RE = re.compile(
    r"\b("
    r"tudo ok|tudo certo|sem restri|n[aã]o tenho restri|nao tenho restri|livre|flex[ií]vel|ta ok|t[aá] ok|"
    r"all good|no constraints|no blockers|flexible|fine with me|no restrictions"
    r")\b",
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
        return "(no prior rounds)"
    lines: list[str] = []
    for index, turn in enumerate(transcript, start=1):
        lines.append(f"### Round {index}")
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            answer = answer_by_qid.get(question.id, "").strip() or "(no answer)"
            lines.append(f"- Q [{question.rubric_key}]: {question.question}")
            lines.append(f"  A: {answer}")
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
                        "note": "Routine/time mentioned by the user",
                        "evidence": [*dim.evidence, text[:120]][:5],
                    },
                )
    return updated


def apply_negative_proof_overrides(belief: BeliefState, transcript: list[InterviewTurn]) -> BeliefState:
    """Deterministic guard: explicit 'never built' closes hands_on_proof."""
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
                    "note": "No hands-on practice yet — explicit negative from the user",
                    "evidence": [*dim.evidence, text[:120]][:5],
                },
            )
    return updated


def apply_constraints_clear_overrides(
    belief: BeliefState,
    transcript: list[InterviewTurn],
) -> BeliefState:
    """Map constraints when user explicitly says there are no blockers."""
    updated = belief.model_copy(deep=True)
    for turn in transcript:
        answer_by_qid = {answer.question_id: answer.text for answer in turn.answers}
        for question in turn.questions:
            text = answer_by_qid.get(question.id, "")
            if not text or not _CONSTRAINTS_CLEAR_RE.search(text):
                continue
            dim = updated.dimensions["constraints"]
            updated.dimensions["constraints"] = dim.model_copy(
                update={
                    "status": "mapped",
                    "confidence": max(dim.confidence, 0.78),
                    "note": "No relevant constraints — user confirmed",
                    "evidence": [*dim.evidence, text[:120]][:5],
                },
            )
    return updated


def apply_baseline_proof_override(belief: BeliefState) -> BeliefState:
    """Close hands_on when baseline was already confirmed (even below saturation threshold)."""
    updated = belief.model_copy(deep=True)
    dim = updated.dimensions["hands_on_proof"]
    note_lower = dim.note.lower()
    baseline_note = (
        "sem prática" in note_lower
        or "no hands-on" in note_lower
        or "baseline" in note_lower
    )
    if dim.status != "mapped" and (baseline_note or dim.confidence >= 0.65):
        if baseline_note or detect_negative_hands_on(" ".join(dim.evidence)):
            updated.dimensions["hands_on_proof"] = dim.model_copy(
                update={
                    "status": "mapped",
                    "confidence": max(dim.confidence, 0.68),
                    "note": dim.note or "No hands-on practice yet — baseline confirmed",
                },
            )
    return updated


def apply_transcript_overrides(belief: BeliefState, transcript: list[InterviewTurn]) -> BeliefState:
    updated = apply_constraints_clear_overrides(
        apply_schedule_overrides(apply_negative_proof_overrides(belief, transcript), transcript),
        transcript,
    )
    return apply_baseline_proof_override(updated)


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
        f"- years_xp: {intake.years_xp or 'not provided'}",
    ]
    if cv_signals:
        sections.append(f"- cv_signals: {cv_signals}")
    if cv_text_excerpt:
        sections.append(f"- cv_excerpt: {cv_text_excerpt[:1500]}")
    if belief is not None:
        sections.append("## current_belief")
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
            do_not_ask.append(f"{key} (already answered in transcript)")

    for key, dim in belief.dimensions.items():
        if dim.status == "mapped":
            do_not_ask.append(f"{key} (mapped)")

    if "hands_on_proof" in closed:
        do_not_ask.append("hands_on_proof (negative answer — do NOT rephrase)")

    sections = [
        f"## round_count\n{round_count}",
        f"## max_questions\n{max_questions}",
        f"## goal_id\n{intake.goal_id}",
        "## goal_brief",
        interviewer_brief_for_goal(intake.goal_id),
        "## intake",
        f"- motivation: {intake.motivation}",
        f"- years_xp: {intake.years_xp or 'not provided'}",
        "## belief_snapshot",
    ]
    for item in build_belief_snapshot(belief):
        sections.append(
            f"- {item['key']}: {item['status']} ({item['confidence']}) — {item['note']}",
        )
    sections.extend(
        [
            f"## interviewable\n{interviewable or ['(none — return [])']}",
            "## do_not_ask",
        ],
    )
    sections.extend(f"- {line}" for line in do_not_ask or ["(nothing)"])
    sections.extend(["## transcript", build_transcript_digest(transcript)])
    sections.extend(
        [
            "## final_instructions",
            "Generate 0–2 questions ONLY for keys in interviewable.",
            "If interviewable is empty, return questions: [].",
            "Never repeat an axis already in do_not_ask.",
            "topic = EN label (Hands-on proof, Real context), never the raw rubric_key.",
        ],
    )
    return "\n".join(sections)
