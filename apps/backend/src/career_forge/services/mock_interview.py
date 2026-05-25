"""Mock interview question generation — HAC-14."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.ai.graphs.validation import RUBRIC_GAPS
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.schemas.common import SkillStatus, ValidationStatus
from career_forge.schemas.mock_interview import (
    MockInterviewQuestion,
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
)
from career_forge.schemas.validation import ValidationResponse
from career_forge.services.roadmap import load_roadmap_catalog
from career_forge.services.validation import (
    QUESTION_HINTS,
    QUESTION_LABELS,
    QUESTION_TEMPLATES,
)

BASE_LABELS = QUESTION_LABELS
GAP_LABELS = ("lacuna 1", "lacuna 2")
SCENARIO_LABELS = ("cenário 1", "cenário 2")

GAP_TEMPLATES = (
    "Você mencionou dificuldade com: {criterion}. Como você corrigiria isso em um projeto real?",
    "Aprofunde o ponto fraco: {criterion}. O que você faria diferente na próxima tentativa?",
)

SCENARIO_TEMPLATES = (
    "Cenário prático: {criterion}. Descreva passo a passo como você resolveria.",
    "Imagine um colega travou em: {criterion}. Como você explicaria e guiaria a solução?",
)


def _get_catalog_node(node_id: str) -> dict[str, Any]:
    catalog = load_roadmap_catalog()
    for node in catalog["nodes"]:
        if node["id"] == node_id:
            return node
    msg = f"Unknown skill node: {node_id}"
    raise ValueError(msg)


def _pad_rubric(rubric: list[str], node_title: str, count: int) -> list[str]:
    padded = list(rubric)
    while len(padded) < count:
        padded.append(f"Demonstrar domínio prático de {node_title}")
    return padded


def build_mock_interview_questions(node_id: str) -> MockInterviewQuestionsResponse:
    """Generate 5–7 contextual mock interview questions from rubric, gaps, and outcomes."""
    node = _get_catalog_node(node_id)
    rubric = _pad_rubric(node.get("rubric") or [], node["title"], 3)
    outcomes: list[str] = node.get("outcomes") or []
    gap_criteria = RUBRIC_GAPS.get(node_id, [])[:2]
    while len(gap_criteria) < 2:
        gap_criteria.append(f"Evidência concreta sobre {node['title']}")

    questions: list[MockInterviewQuestion] = []

    for index in range(3):
        questions.append(
            MockInterviewQuestion(
                id=f"{node_id}-mi-q{index + 1}",
                index=index + 1,
                label=BASE_LABELS[index],
                prompt=QUESTION_TEMPLATES[index].format(criterion=rubric[index].rstrip(".")),
                hint=QUESTION_HINTS.get(BASE_LABELS[index]),
                rubric_criterion=rubric[index],
                phase="base",
            ),
        )

    for index in range(2):
        criterion = gap_criteria[index].rstrip(".")
        questions.append(
            MockInterviewQuestion(
                id=f"{node_id}-mi-q{index + 4}",
                index=index + 4,
                label=GAP_LABELS[index],
                prompt=GAP_TEMPLATES[index].format(criterion=criterion),
                hint="Foque em ação concreta — o que você faria de diferente?",
                rubric_criterion=criterion,
                phase="gap_probe",
            ),
        )

    scenario_sources = outcomes[:2] if len(outcomes) >= 2 else [
        f"Aplicar {node['title']} em um projeto real",
        f"Ensinar {node['title']} para um colega iniciante",
    ]

    for index, outcome in enumerate(scenario_sources):
        criterion = outcome.rstrip(".")
        questions.append(
            MockInterviewQuestion(
                id=f"{node_id}-mi-q{index + 6}",
                index=index + 6,
                label=SCENARIO_LABELS[index],
                prompt=SCENARIO_TEMPLATES[index].format(criterion=criterion),
                hint="Use um exemplo concreto de projeto ou endpoint.",
                rubric_criterion=criterion,
                phase="scenario",
            ),
        )

    return MockInterviewQuestionsResponse(
        node_id=node_id,
        node_title=node["title"],
        node_icon=node.get("icon") or "code",
        total_questions=len(questions),
        questions=questions,
    )


def persist_mock_interview_result(
    session: Session,
    payload: MockInterviewRequest,
    result: ValidationResponse,
) -> tuple[Validation, UserSkillNodeRow]:
    """Store mock interview attempt with full 5–7 Q/A and update user skill node."""
    from career_forge.services.validation import _resolve_user

    user = _resolve_user(session, payload.user_id)
    if user is None:
        user = User(
            external_id=payload.user_id,
            display_name=payload.user_id.replace("-", " ").title(),
            email=f"{payload.user_id}@demo.careerforge.local",
        )
        session.add(user)
        session.flush()

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

    question_payload = build_mock_interview_questions(payload.node_id)
    user_skill.status = new_status.value
    user_skill.mastery_score = result.score
    user_skill.evidence = {
        "strengths": result.strengths,
        "gaps": result.gaps,
        "next_action": result.next_action,
        "mock_interview": True,
    }

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
