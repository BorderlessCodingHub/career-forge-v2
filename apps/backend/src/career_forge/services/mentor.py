"""Contextual mentor — learner memory and reply generation (HAC-13)."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.db.repositories.user import get_by_external_id
from career_forge.demo.ana_state import DEMO_ANA_SKILL_STATE, DEMO_ANA_VALIDATIONS
from career_forge.schemas.common import SkillStatus
from career_forge.schemas.mentor import MentorContextSnapshot, MentorRequest, MentorResponse
from career_forge.services.roadmap import load_roadmap_catalog


def _catalog_node(node_id: str) -> dict[str, Any] | None:
    catalog = load_roadmap_catalog()
    for node in catalog["nodes"]:
        if node["id"] == node_id:
            return node
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
            evidence = (user_skill.evidence if user_skill else None) or {}
            if isinstance(evidence, dict):
                gaps.extend(evidence.get("gaps") or [])
                strengths.extend(evidence.get("strengths") or [])

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
    if re.search(r"\b(refer[eê]ncia|material|link|estudar|ler)\b", lowered):
        return "references"
    if re.search(r"\b(erro|errei|lacuna|falhei|revisar|confus)\b", lowered):
        return "gaps"
    if re.search(r"\b(praticar|exerc[ií]cio|como fa[cç]o|treinar)\b", lowered):
        return "practice"
    if re.search(r"\b(pr[oó]ximo|foco|prioridade|agora)\b", lowered):
        return "focus"
    return "general"


def build_mentor_response(
    payload: MentorRequest,
    context: MentorContextSnapshot,
) -> MentorResponse:
    """Deterministic contextual mentor reply from learner memory (no LLM for MVP)."""
    node_title = payload.node_title or "sua trilha"
    references = _node_references(payload.node_id)
    intent = _intent(payload.message)

    if intent == "references":
        if references:
            reply = (
                f"Para {node_title}, comece por estas referências da trilha: "
                f"{'; '.join(references)}. "
            )
        else:
            reply = (
                f"Para {node_title}, revise a documentação oficial do tópico e "
                "monte um mini projeto aplicando o conceito em um endpoint real."
            )
        if context.recent_gaps:
            reply += f" Priorize fechar: {context.recent_gaps[0]}."

    elif intent == "gaps":
        if context.recent_gaps:
            gap_text = "; ".join(context.recent_gaps[:2])
            reply = (
                f"Vi que você ainda tem lacunas em {node_title}: {gap_text}. "
                "Vamos atacar uma de cada vez — explique o conceito em voz alta e "
                "compare com um exemplo concreto de API."
            )
        elif context.failed_nodes:
            reply = (
                f"Seus nós em revisão: {', '.join(context.failed_nodes)}. "
                f"Em {node_title}, volte ao critério que falhou na validação antes de avançar."
            )
        elif context.last_validation_feedback:
            reply = (
                f"Pelo histórico recente: {context.last_validation_feedback} "
                f"Quer retomar {node_title} com um plano curto de 20 minutos?"
            )
        else:
            reply = (
                f"Ainda não tenho evidência de falha em {node_title}. "
                "Se algo ficou confuso, descreva o ponto exato que travou."
            )

    elif intent == "practice":
        reply = (
            f"Plano rápido para {node_title}: (1) leia um outcome da trilha, "
            "(2) implemente um exemplo mínimo, (3) explique em voz alta como se "
            "estivesse ensinando um colega. "
        )
        if context.current_node_status == SkillStatus.REVISAR.value:
            reply += "Foque no critério que falhou na última validação antes de avançar."
        elif references:
            reply += f"Referência sugerida: {references[0]}."

    elif intent == "focus":
        if context.failed_nodes:
            reply = (
                f"Seu foco agora: fechar {context.failed_nodes[0]} antes de avançar. "
                f"Depois retome {node_title}."
            )
        elif context.current_node_status in {SkillStatus.VALIDAR.value, SkillStatus.EM_ESTUDO.value}:
            reply = (
                f"{node_title} está em {context.current_node_status.replace('_', ' ')} "
                f"com mastery {context.current_node_mastery or 0}%. "
                "Valide ou pratique mais antes de pular para o próximo nó."
            )
        else:
            reply = (
                f"Continue {node_title} com evidência concreta — "
                "a trilha só destrava mastery com validação, não com checkbox."
            )

    else:
        memory_bits: list[str] = []
        if context.validation_count:
            memory_bits.append(f"{context.validation_count} validações no histórico")
        if context.recent_strengths:
            memory_bits.append(f"ponto forte: {context.recent_strengths[0]}")
        if context.recent_gaps:
            memory_bits.append(f"lacuna recente: {context.recent_gaps[0]}")
        memory = ". ".join(memory_bits)
        reply = (
            f"Sobre {node_title}: {payload.message.strip()} — "
            f"tenho contexto da sua trilha ({memory or 'sem validações ainda'}). "
            "Posso sugerir referências, revisar lacunas ou montar um plano de prática."
        )

    return MentorResponse(
        reply=reply.strip(),
        references=references,
        context_snapshot=context,
    )
