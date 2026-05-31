"""Validation persistence and question generation — HAC-10."""

from __future__ import annotations

from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.schemas.validation import (
    ValidationQuestion,
    ValidationQuestionsResponse,
    ValidationRequest,
    ValidationResponse,
)
from career_forge.services.assessment_persistence import persist_assessment_result
from career_forge.services.assessment_rubric import (
    QUESTION_HINTS,
    QUESTION_LABELS,
    QUESTION_TEMPLATES,
)
from career_forge.services.roadmap import get_skill_node_context


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
    question_payload = build_validation_questions(payload.node_id, session)
    return persist_assessment_result(
        session,
        user_id=payload.user_id,
        node_id=payload.node_id,
        result=result,
        questions=[question.model_dump() for question in question_payload.questions],
        answers=[answer.model_dump() for answer in payload.answers],
        mock_interview=False,
    )
