"""Contextual mentor — learner memory and reply generation (HAC-13)."""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.db.repositories.user import get_by_external_id
from career_forge.demo.ana_state import DEMO_ANA_SKILL_STATE, DEMO_ANA_VALIDATIONS
from career_forge.schemas.common import SkillStatus
from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest, MentorResponse
from career_forge.services.roadmap import read_evidence, resolve_skill_node_catalog_entry


def _catalog_node(node_id: str) -> dict[str, Any] | None:
    try:
        return resolve_skill_node_catalog_entry(None, node_id)
    except ValueError:
        return None


def _demo_context(node_id: str | None) -> MentorContextSnapshot:
    gaps: list[str] = []
    strengths: list[str] = []
    failed_nodes: list[str] = []
    current_status: str | None = None
    current_mastery: int | None = None
    last_feedback: str | None = None

    for validation in DEMO_ANA_VALIDATIONS:
        if not validation.get("passed"):
            failed_nodes.append(str(validation["skill_node_id"]))
        if validation.get("feedback"):
            last_feedback = str(validation["feedback"])

    for node_key, state in DEMO_ANA_SKILL_STATE.items():
        evidence = state.get("evidence") or {}
        gaps.extend(evidence.get("gaps") or [])
        strengths.extend(evidence.get("strengths") or [])
        if state.get("status") == SkillStatus.REVISAR.value:
            failed_nodes.append(node_key)
        if node_id and node_key == node_id:
            current_status = str(state.get("status"))
            current_mastery = int(state.get("mastery_score", 0))

    return MentorContextSnapshot(
        recent_gaps=gaps[:4],
        recent_strengths=strengths[:4],
        failed_nodes=sorted(set(failed_nodes)),
        current_node_status=current_status,
        current_node_mastery=current_mastery,
        validation_count=len(DEMO_ANA_VALIDATIONS),
        last_validation_feedback=last_feedback,
    )


def load_mentor_context(
    session: Session,
    user_id: str,
    node_id: str | None = None,
) -> MentorContextSnapshot:
    """Build mentor memory from validations and skill graph state."""
    try:
        user = get_by_external_id(session, user_id)
        if user is None:
            return _demo_context(node_id)

        validations = session.scalars(
            select(Validation)
            .where(Validation.user_id == user.id)
            .order_by(Validation.created_at.desc())
            .limit(5),
        ).all()
        if not validations:
            return _demo_context(node_id)

        gaps: list[str] = []
        strengths: list[str] = []
        failed_nodes: list[str] = []
        last_feedback: str | None = None

        for row in validations:
            if not row.passed:
                failed_nodes.append(row.skill_node_id)
            if row.feedback and last_feedback is None:
                last_feedback = row.feedback
            user_skill = session.get(UserSkillNodeRow, row.user_skill_node_id)
            summary = read_evidence(user_skill.evidence if user_skill else None).validation_summary()
            gaps.extend(summary.get("gaps") or [])
            strengths.extend(summary.get("strengths") or [])

        # Prefer the structured knowledge-gap ledger (concept-level) over evidence strings (HAC-68).
        try:
            from career_forge.services.knowledge_gaps import list_open_gaps

            ledger = list_open_gaps(session, user_id=user_id, skill_node_id=node_id)
            if not ledger and node_id:
                ledger = list_open_gaps(session, user_id=user_id)
            ledger_concepts = [item.concept for item in ledger]
            if ledger_concepts:
                gaps = ledger_concepts + [g for g in gaps if g not in ledger_concepts]
        except Exception:
            pass

        current_status: str | None = None
        current_mastery: int | None = None
        if node_id:
            user_skill = session.scalar(
                select(UserSkillNodeRow).where(
                    UserSkillNodeRow.user_id == user.id,
                    UserSkillNodeRow.skill_node_id == node_id,
                ),
            )
            if user_skill:
                current_status = user_skill.status
                current_mastery = user_skill.mastery_score

        return MentorContextSnapshot(
            recent_gaps=gaps[:4],
            recent_strengths=strengths[:4],
            failed_nodes=sorted(set(failed_nodes)),
            current_node_status=current_status,
            current_node_mastery=current_mastery,
            validation_count=len(validations),
            last_validation_feedback=last_feedback,
        )
    except Exception:
        return _demo_context(node_id)


def _node_references(node_id: str | None) -> list[str]:
    if not node_id:
        return []
    node = _catalog_node(node_id)
    if not node:
        return []
    outcomes = node.get("outcomes") or []
    return [str(item) for item in outcomes[:3]]


def _intent(message: str) -> str:
    lowered = message.lower()
    if re.search(r"\b(referen[cs]e|material|link|study|read)\b", lowered):
        return "references"
    if re.search(r"\b(error|mistake|gap|failed|fail|review|confus)\b", lowered):
        return "gaps"
    if re.search(r"\b(practice|exercise|how do i|train)\b", lowered):
        return "practice"
    if re.search(r"\b(next|focus|priority|now)\b", lowered):
        return "focus"
    return "general"


def _reply_references(
    payload: MentorRequest,
    context: MentorContextSnapshot,
    node_title: str,
    references: list[str],
) -> str:
    if references:
        reply = (
            f"For {node_title}, start with these trail references: "
            f"{'; '.join(references)}. "
        )
    else:
        reply = (
            f"For {node_title}, review the official topic docs and "
            "build a mini project applying the concept in a real endpoint."
        )
    if context.recent_gaps:
        reply += f" Prioritize closing: {context.recent_gaps[0]}."
    return reply


def _reply_gaps(
    payload: MentorRequest,
    context: MentorContextSnapshot,
    node_title: str,
    references: list[str],
) -> str:
    if context.recent_gaps:
        gap_text = "; ".join(context.recent_gaps[:2])
        return (
            f"I see you still have gaps in {node_title}: {gap_text}. "
            "Let's tackle one at a time — explain the concept out loud and "
            "compare it with a concrete API example."
        )
    if context.failed_nodes:
        return (
            f"Your nodes in review: {', '.join(context.failed_nodes)}. "
            f"On {node_title}, return to the criterion that failed validation before advancing."
        )
    if context.last_validation_feedback:
        return (
            f"From recent history: {context.last_validation_feedback} "
            f"Want to resume {node_title} with a short 20-minute plan?"
        )
    return (
        f"I do not have failure evidence for {node_title} yet. "
        "If something is confusing, describe the exact sticking point."
    )


def _reply_practice(
    payload: MentorRequest,
    context: MentorContextSnapshot,
    node_title: str,
    references: list[str],
) -> str:
    reply = (
        f"Quick plan for {node_title}: (1) read one trail outcome, "
        "(2) implement a minimal example, (3) explain it out loud as if "
        "teaching a peer. "
    )
    if context.current_node_status == SkillStatus.REVISAR.value:
        reply += "Focus on the criterion that failed last validation before advancing."
    elif references:
        reply += f"Suggested reference: {references[0]}."
    return reply


def _reply_focus(
    payload: MentorRequest,
    context: MentorContextSnapshot,
    node_title: str,
    references: list[str],
) -> str:
    if context.failed_nodes:
        return (
            f"Your focus now: close {context.failed_nodes[0]} before advancing. "
            f"Then resume {node_title}."
        )
    if context.current_node_status in {SkillStatus.VALIDAR.value, SkillStatus.EM_ESTUDO.value}:
        return (
            f"{node_title} is in {context.current_node_status.replace('_', ' ')} "
            f"with mastery {context.current_node_mastery or 0}%. "
            "Validate or practice more before jumping to the next node."
        )
    return (
        f"Keep going on {node_title} with concrete evidence — "
        "the trail unlocks mastery through validation, not checkboxes."
    )


def _reply_general(
    payload: MentorRequest,
    context: MentorContextSnapshot,
    node_title: str,
    references: list[str],
) -> str:
    memory_bits: list[str] = []
    if context.validation_count:
        memory_bits.append(f"{context.validation_count} validations in history")
    if context.recent_strengths:
        memory_bits.append(f"strength: {context.recent_strengths[0]}")
    if context.recent_gaps:
        memory_bits.append(f"recent gap: {context.recent_gaps[0]}")
    memory = ". ".join(memory_bits)
    return (
        f"About {node_title}: {payload.message.strip()} — "
        f"I have context from your trail ({memory or 'no validations yet'}). "
        "I can suggest references, review gaps, or build a practice plan."
    )


_INTENT_REPLIES: dict[
    str,
    Callable[[MentorRequest, MentorContextSnapshot, str, list[str]], str],
] = {
    "references": _reply_references,
    "gaps": _reply_gaps,
    "practice": _reply_practice,
    "focus": _reply_focus,
    "general": _reply_general,
}


def build_mentor_response(
    payload: MentorRequest,
    context: MentorContextSnapshot,
) -> MentorResponse:
    """Deterministic contextual mentor reply from learner memory (no LLM for MVP)."""
    node_title = payload.node_title or "your trail"
    references = _node_references(payload.node_id)
    intent = _intent(payload.message)

    reply_for = _INTENT_REPLIES.get(intent, _reply_general)
    reply = reply_for(payload, context, node_title, references)

    return MentorResponse(
        reply=reply.strip(),
        references=references,
        context_snapshot=context,
    )
