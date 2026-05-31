"""Shared persistence for rubric assessments — validation + mock interview (HAC-78).

`persist_validation_result` and `persist_mock_interview_result` previously
duplicated ~70 LOC of identical persistence (resolve user → upsert
UserSkillNode → status/mastery → merge evidence → insert Validation). Both now
delegate to `persist_assessment_result`; the only behavioural difference is the
`mock_interview` evidence flag and the stored question shape (supplied by the
caller).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.db.repositories.user import ensure_user
from career_forge.schemas.common import SkillStatus, ValidationStatus
from career_forge.schemas.validation import ValidationResponse
from career_forge.services.roadmap import merge_validation_evidence


def persist_assessment_result(
    session: Session,
    *,
    user_id: str,
    node_id: str,
    result: ValidationResponse,
    questions: list[dict],
    answers: list[dict],
    mock_interview: bool = False,
) -> tuple[Validation, UserSkillNodeRow]:
    """Persist a rubric assessment attempt and update the user skill node.

    Single source for the shared upsert → evidence → insert body used by both
    validation and mock interview. ``questions``/``answers`` are the JSON rows
    to store; ``mock_interview`` tags the evidence summary.
    """
    user = ensure_user(session, user_id)

    user_skill = session.scalar(
        select(UserSkillNodeRow).where(
            UserSkillNodeRow.user_id == user.id,
            UserSkillNodeRow.skill_node_id == node_id,
        ),
    )
    if user_skill is None:
        user_skill = UserSkillNodeRow(
            user_id=user.id,
            skill_node_id=node_id,
            status=SkillStatus.EM_ESTUDO.value,
            mastery_score=0,
        )
        session.add(user_skill)
        session.flush()

    passed = result.status == ValidationStatus.APROVADO
    new_status = SkillStatus.APROVADO if passed else SkillStatus.REVISAR

    user_skill.status = new_status.value
    user_skill.mastery_score = result.score
    user_skill.evidence = merge_validation_evidence(
        user_skill.evidence,
        strengths=result.strengths,
        gaps=result.gaps,
        next_action=result.next_action,
        mock_interview=mock_interview,
    )

    validation = Validation(
        user_id=user.id,
        skill_node_id=node_id,
        user_skill_node_id=user_skill.id,
        score=result.score,
        passed=passed,
        feedback=result.mentor_summary,
        questions=questions,
        answers=answers,
    )
    session.add(validation)
    session.commit()
    session.refresh(validation)
    session.refresh(user_skill)
    return validation, user_skill
