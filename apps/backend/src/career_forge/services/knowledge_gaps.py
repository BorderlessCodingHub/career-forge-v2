"""Knowledge gap ledger service — the adaptive memory (HAC-67).

Capture-at-submit + async classification keeps the gabarito → gap mapping durable
without a separate session table: the API captures the wrong-answer payload while
the in-memory MCQ session is still alive, then hands a self-contained payload to a
fire-and-forget background task that opens its own DB session.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from career_forge.ai.tools.gap_classifier import classify_gaps
from career_forge.db.models.knowledge_gap import KnowledgeGap
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.session import SessionLocal

REMEDIATION_PREFIX = "gap-rem-"
REMEDIATION_SEVERITY = "high"
from career_forge.schemas.knowledge_gap import (
    KnowledgeGapDraft,
    KnowledgeGapItem,
    WrongAnswerItem,
)
from career_forge.schemas.mock_interview import MockInterviewRequest
from career_forge.services.mock_interview_session import MockInterviewSessionRecord


def build_gap_capture(
    session_record: MockInterviewSessionRecord,
    payload: MockInterviewRequest,
) -> tuple[list[WrongAnswerItem], list[str]]:
    """From the live MCQ session + submitted letters, derive wrong items + correct concepts."""
    answers_by_id = {
        answer.question_id: answer.answer.strip().upper() for answer in payload.answers
    }
    questions_by_id = {q.get("id"): q for q in session_record.questions_public}

    wrong: list[WrongAnswerItem] = []
    correct_concepts: list[str] = []

    for index, (question_id, expected) in enumerate(session_record.answer_key.items()):
        concept = (
            session_record.rubric[index]
            if index < len(session_record.rubric)
            else question_id
        )
        chosen = answers_by_id.get(question_id, "")
        question = questions_by_id.get(question_id, {})
        options = {opt.get("letter"): opt.get("text", "") for opt in (question.get("options") or [])}

        if chosen == expected:
            correct_concepts.append(concept)
            continue

        wrong.append(
            WrongAnswerItem(
                question_id=question_id,
                concept=concept,
                prompt=str(question.get("prompt", "")),
                chosen=chosen,
                chosen_text=options.get(chosen, "(sem resposta)"),
                correct=expected,
                correct_text=options.get(expected, ""),
            ),
        )

    return wrong, correct_concepts


def _resolve_user(session: Session, external_id: str) -> User | None:
    return session.scalar(select(User).where(User.external_id == external_id))


def upsert_knowledge_gap(
    session: Session,
    *,
    user_id: uuid.UUID,
    skill_node_id: str,
    draft: KnowledgeGapDraft,
    source: str = "mock_interview",
) -> None:
    """Idempotent upsert keyed by (user, node, concept) — re-opens resolved gaps.

    Uses Postgres INSERT ... ON CONFLICT DO UPDATE so repeated concepts within one
    commit and concurrent attempts never violate the unique constraint.
    """
    stmt = pg_insert(KnowledgeGap).values(
        user_id=user_id,
        skill_node_id=skill_node_id,
        concept=draft.concept,
        severity=draft.severity,
        evidence=draft.evidence or None,
        suggested_remediation=draft.suggested_remediation or None,
        status="open",
        source=source,
    )
    stmt = stmt.on_conflict_do_update(
        constraint="uq_knowledge_gap_user_node_concept",
        set_={
            "severity": stmt.excluded.severity,
            "evidence": func.coalesce(stmt.excluded.evidence, KnowledgeGap.evidence),
            "suggested_remediation": func.coalesce(
                stmt.excluded.suggested_remediation, KnowledgeGap.suggested_remediation
            ),
            "status": "open",
            "resolved_at": None,
            "source": source,
            "updated_at": func.now(),
        },
    )
    session.execute(stmt)


def resolve_concepts(
    session: Session,
    *,
    user_id: uuid.UUID,
    skill_node_id: str,
    concepts: list[str],
) -> int:
    """Mark open gaps for these concepts as resolved. Returns count resolved."""
    if not concepts:
        return 0
    rows = session.scalars(
        select(KnowledgeGap).where(
            KnowledgeGap.user_id == user_id,
            KnowledgeGap.skill_node_id == skill_node_id,
            KnowledgeGap.concept.in_(concepts),
            KnowledgeGap.status == "open",
        ),
    ).all()
    now = datetime.now(UTC)
    for row in rows:
        row.status = "resolved"
        row.resolved_at = now
    return len(rows)


def list_open_gaps(
    session: Session,
    *,
    user_id: str,
    skill_node_id: str | None = None,
    limit: int = 20,
) -> list[KnowledgeGapItem]:
    """Open gaps for a learner, optionally scoped to a node (mentor / next mock / drawer)."""
    user = _resolve_user(session, user_id)
    if user is None:
        return []
    query = select(KnowledgeGap).where(
        KnowledgeGap.user_id == user.id,
        KnowledgeGap.status == "open",
    )
    if skill_node_id is not None:
        query = query.where(KnowledgeGap.skill_node_id == skill_node_id)
    query = query.order_by(KnowledgeGap.updated_at.desc()).limit(limit)
    rows = session.scalars(query).all()
    return [
        KnowledgeGapItem(
            concept=row.concept,
            severity=row.severity,  # type: ignore[arg-type]
            status=row.status,  # type: ignore[arg-type]
            suggested_remediation=row.suggested_remediation,
            skill_node_id=row.skill_node_id,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def _concept_slug(concept: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", concept.lower()).strip("-")
    return slug[:48] or "conceito"


def _remediation_item(item_id: str, gap: KnowledgeGap) -> dict[str, str]:
    return {
        "type": "task",
        "id": item_id,
        "title": f"Reforçar: {gap.concept}",
        "outcome": "Fechar a lacuna detectada no mock interview",
        "evidence_prompt": gap.suggested_remediation or f"Demonstre domínio de {gap.concept}",
        "source": "gap",
    }


def sync_remediation_tasks(
    session: Session,
    *,
    user_id: uuid.UUID,
    skill_node_id: str,
) -> None:
    """Reconcile remediation tasks on a node against its open high-severity gaps (HAC-69).

    Idempotent (stable id per concept), self-cleaning (drops tasks whose gap resolved),
    and preserves the node's existing tasks/references. Only mutates list-form evidence.
    """
    skill_row = session.scalar(
        select(UserSkillNodeRow).where(
            UserSkillNodeRow.user_id == user_id,
            UserSkillNodeRow.skill_node_id == skill_node_id,
        ),
    )
    if skill_row is None or isinstance(skill_row.evidence, dict):
        return

    high_gaps = session.scalars(
        select(KnowledgeGap).where(
            KnowledgeGap.user_id == user_id,
            KnowledgeGap.skill_node_id == skill_node_id,
            KnowledgeGap.status == "open",
            KnowledgeGap.severity == REMEDIATION_SEVERITY,
        ),
    ).all()
    desired = {f"{REMEDIATION_PREFIX}{_concept_slug(gap.concept)}": gap for gap in high_gaps}

    evidence = list(skill_row.evidence or [])
    kept: list[dict] = []
    seen: set[str] = set()
    for item in evidence:
        is_remediation = (
            isinstance(item, dict)
            and item.get("type") == "task"
            and str(item.get("id", "")).startswith(REMEDIATION_PREFIX)
        )
        if not is_remediation:
            kept.append(item)
            continue
        item_id = str(item.get("id"))
        if item_id in desired and item_id not in seen:
            kept.append(_remediation_item(item_id, desired[item_id]))
            seen.add(item_id)

    for item_id, gap in desired.items():
        if item_id not in seen:
            kept.append(_remediation_item(item_id, gap))
            seen.add(item_id)

    skill_row.evidence = kept


def _best_effort_learner_summary(
    session: Session,
    user_id: str,
    node_id: str,
) -> str | None:
    try:
        from career_forge.services.mock_interview_context import build_mock_interview_context

        _, learner = build_mock_interview_context(session, user_id=user_id, node_id=node_id)
        return learner.compact_summary() if learner is not None else None
    except Exception:
        return None


def classify_and_store_gaps(
    *,
    user_id: str,
    node_id: str,
    node_title: str,
    wrong_items: list[dict],
    correct_concepts: list[str],
) -> None:
    """Fire-and-forget background task: resolve correct concepts, classify + store gaps.

    Self-contained — opens its own DB session and never raises into the request.
    """
    items = [WrongAnswerItem.model_validate(item) for item in wrong_items]
    with SessionLocal() as session:
        try:
            user = _resolve_user(session, user_id)
            if user is None:
                return

            resolve_concepts(
                session,
                user_id=user.id,
                skill_node_id=node_id,
                concepts=correct_concepts,
            )

            if items:
                learner_summary = _best_effort_learner_summary(session, user_id, node_id)
                classification = classify_gaps(
                    node_title=node_title,
                    learner_summary=learner_summary,
                    wrong_items=items,
                )
                for draft in classification.gaps:
                    upsert_knowledge_gap(
                        session,
                        user_id=user.id,
                        skill_node_id=node_id,
                        draft=draft,
                    )

            # Flush so resolved/upserted gaps are visible before reconciling tasks (autoflush off).
            session.flush()
            sync_remediation_tasks(session, user_id=user.id, skill_node_id=node_id)

            session.commit()
        except Exception:
            session.rollback()
