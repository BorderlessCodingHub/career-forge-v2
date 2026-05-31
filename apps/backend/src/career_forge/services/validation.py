"""Validation persistence and question generation — HAC-10."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.db.repositories.user import ensure_user
from career_forge.schemas.common import SkillStatus, ValidationStatus
from career_forge.schemas.validation import (
    ValidationQuestion,
    ValidationQuestionsResponse,
    ValidationRequest,
    ValidationResponse,
)
from career_forge.services.assessment_rubric import (
    QUESTION_HINTS,
    QUESTION_LABELS,
    QUESTION_TEMPLATES,
)
from career_forge.services.roadmap import get_skill_node_context, merge_validation_evidence


def build_validation_questions(
    node_id: str,
    session: Session | None = None,
) -> ValidationQuestionsResponse:
    """Generate three interview questions from the rubric of a catalog or
    persisted AI-generated StudyPlan node (HAC-64)."""
    node = get_skill_node_context(session, node_id)
    rubric: list[str] = node.get("rubric") or []
    while len(rubric) < 3:
        rubric.append(f"Demonstrar domínio prático de {node['title']}")

    questions = [
        ValidationQuestion(
            id=f"{node_id}-q{index + 1}",
            index=index + 1,
            label=QUESTION_LABELS[index],
            prompt=QUESTION_TEMPLATES[index].format(criterion=rubric[index].rstrip(".")),
            hint=QUESTION_HINTS.get(QUESTION_LABELS[index]),
            rubric_criterion=rubric[index],
        )
        for index in range(3)
    ]

    return ValidationQuestionsResponse(
        node_id=node_id,
        node_title=node["title"],
        node_icon=node.get("icon") or "code",
        questions=questions,
    )


def persist_validation_result(
    session: Session,
    payload: ValidationRequest,
    result: ValidationResponse,
) -> tuple[Validation, UserSkillNodeRow]:
    """Store validation attempt and update user skill node status."""
    user = ensure_user(session, payload.user_id)

    user_skill = session.scalar(
        select(UserSkillNodeRow).where(
            UserSkillNodeRow.user_id == user.id,
            UserSkillNodeRow.skill_node_id == payload.node_id,
        ),
    )
    if user_skill is None:
        user_skill = UserSkillNodeRow(
            user_id=user.id,
            skill_node_id=payload.node_id,
            status=SkillStatus.EM_ESTUDO.value,
            mastery_score=0,
        )
        session.add(user_skill)
        session.flush()

    passed = result.status == ValidationStatus.APROVADO
    new_status = SkillStatus.APROVADO if passed else SkillStatus.REVISAR

    question_payload = build_validation_questions(payload.node_id, session)
    user_skill.status = new_status.value
    user_skill.mastery_score = result.score
    user_skill.evidence = merge_validation_evidence(
        user_skill.evidence,
        strengths=result.strengths,
        gaps=result.gaps,
        next_action=result.next_action,
    )

    validation = Validation(
        user_id=user.id,
        skill_node_id=payload.node_id,
        user_skill_node_id=user_skill.id,
        score=result.score,
        passed=passed,
        feedback=result.mentor_summary,
        questions=[question.model_dump() for question in question_payload.questions],
        answers=[answer.model_dump() for answer in payload.answers],
    )
    session.add(validation)
    session.commit()
    session.refresh(validation)
    session.refresh(user_skill)
    return validation, user_skill
