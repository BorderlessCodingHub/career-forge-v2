"""Mock interview question generation — HAC-14."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.mock_interview import (
    MockInterviewQuestion,
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
)
from career_forge.schemas.validation import ValidationResponse
from career_forge.services.assessment_persistence import persist_assessment_result
from career_forge.services.assessment_rubric import (
    PASS_THRESHOLD,
    QUESTION_HINTS,
    QUESTION_LABELS,
    QUESTION_TEMPLATES,
    RUBRIC_GAPS,
)
from career_forge.services.mock_interview_session import (
    MockInterviewSessionRecord,
    consume_mock_interview_session,
    get_mock_interview_session,
)
from career_forge.services.roadmap import get_skill_node_context

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


def _pad_rubric(rubric: list[str], node_title: str, count: int) -> list[str]:
    padded = list(rubric)
    while len(padded) < count:
        padded.append(f"Demonstrar domínio prático de {node_title}")
    return padded


def _gap_criteria_for(node: dict[str, Any], raw_rubric: list[str]) -> list[str]:
    """Gap-probe criteria: static rubric gaps, then extra StudyPlan rubric items,
    then a generic fallback. Keeps generated nodes (no static gaps) contextual.
    """
    criteria = list(RUBRIC_GAPS.get(node["id"], []))[:2]
    for extra in raw_rubric[3:]:
        if len(criteria) >= 2:
            break
        criteria.append(extra)
    while len(criteria) < 2:
        criteria.append(f"Evidência concreta sobre {node['title']}")
    return criteria


def build_mock_interview_questions(
    node_id: str,
    session: Session | None = None,
) -> MockInterviewQuestionsResponse:
    """Generate 5–7 contextual mock interview questions from rubric, gaps, and outcomes.

    Resolves catalog nodes and persisted AI-generated StudyPlan nodes (HAC-64),
    where the rubric maps to per-task evidence prompts and outcomes to task results.
    """
    node = get_skill_node_context(session, node_id)
    raw_rubric: list[str] = node.get("rubric") or []
    rubric = _pad_rubric(raw_rubric, node["title"], 3)
    outcomes: list[str] = node.get("outcomes") or []
    gap_criteria = _gap_criteria_for(node, raw_rubric)

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
    *,
    stored_questions: list[dict] | None = None,
) -> tuple[Validation, UserSkillNodeRow]:
    """Store mock interview attempt with full 5–7 Q/A and update user skill node."""
    question_rows = stored_questions or [
        question.model_dump()
        for question in build_mock_interview_questions(payload.node_id, session).questions
    ]
    return persist_assessment_result(
        session,
        user_id=payload.user_id,
        node_id=payload.node_id,
        result=result,
        questions=question_rows,
        answers=[answer.model_dump() for answer in payload.answers],
        mock_interview=True,
    )


def evaluate_mcq_session(payload: MockInterviewRequest) -> tuple[ValidationResponse, MockInterviewSessionRecord]:
    """Score MCQ answers deterministically against server-side gabarito (HAC-65)."""
    if not payload.session_id:
        msg = "session_id is required for MCQ mock interview"
        raise ValueError(msg)

    session = get_mock_interview_session(payload.session_id)
    if session.user_id != payload.user_id or session.node_id != payload.node_id:
        msg = "Mock interview session does not match user/node"
        raise ValueError(msg)

    answers_by_id = {
        answer.question_id: answer.answer.strip().upper()
        for answer in payload.answers
    }
    total = len(session.answer_key)
    correct_count = 0
    gaps: list[str] = []
    strengths: list[str] = []

    for index, (question_id, expected) in enumerate(session.answer_key.items()):
        selected = answers_by_id.get(question_id, "")
        if selected not in {"A", "B", "C", "D"}:
            gaps.append(f"Sem resposta válida para {question_id}")
            continue
        criterion = session.rubric[index] if index < len(session.rubric) else question_id
        if selected == expected:
            correct_count += 1
            strengths.append(f"Acertou: {criterion[:72]}")
        else:
            gaps.append(f"Errou ({criterion[:72]}): marcou {selected}, gabarito {expected}")

    score = round(100 * correct_count / max(total, 1))
    status = ValidationStatus.APROVADO if score >= PASS_THRESHOLD else ValidationStatus.REVISAR

    if not strengths:
        strengths.append(f"Completou o mock interview MCQ de {payload.node_title}")

    if not gaps and status == ValidationStatus.REVISAR:
        gaps.append(f"Score {score}/100 abaixo do threshold — revise o bloco {payload.node_title}")

    next_action = (
        f"Revise as lacunas de {payload.node_title} e refaça o mock interview."
        if status == ValidationStatus.REVISAR
        else f"Mastery validado em {payload.node_title} — avance para o próximo bloco."
    )

    mentor_summary = (
        f"Mock interview MCQ de {payload.node_title} — "
        f"{correct_count}/{total} acertos, score {score}/100 ({status.value}). "
    )
    if gaps:
        mentor_summary += f"Lacunas: {'; '.join(gaps[:3])}. "
    if strengths:
        mentor_summary += f"Acertos: {strengths[0]}. "
    mentor_summary += next_action

    validation = ValidationResponse(
        score=score,
        status=status,
        strengths=strengths[:4],
        gaps=gaps[:5],
        next_action=next_action,
        mentor_summary=mentor_summary,
    )
    return validation, session
