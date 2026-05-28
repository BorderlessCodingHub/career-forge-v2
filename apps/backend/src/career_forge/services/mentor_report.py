"""Mentor report aggregation — HAC-15."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID, load_demo_diagnosis
from career_forge.db.models.profile import Profile
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode as UserSkillNodeRow
from career_forge.db.models.validation import Validation
from career_forge.schemas.common import ValidationStatus
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.profile_diagnosis import diagnosis_response_from_profile
from career_forge.schemas.mentor_report import MentorReportResponse, MentorReportValidationEntry
from career_forge.services.roadmap import load_roadmap_catalog


def _resolve_user(session: Session, external_id: str) -> User | None:
    return session.scalar(select(User).where(User.external_id == external_id))


def _ensure_demo_user(session: Session, external_id: str) -> User:
    from scripts.seed import seed_demo_ana

    user = _resolve_user(session, external_id)
    if user is not None:
        return user
    if external_id == DEMO_ANA_EXTERNAL_ID:
        seed_demo_ana(session)
        user = _resolve_user(session, external_id)
        if user is not None:
            return user
    msg = f"User not found: {external_id}"
    raise ValueError(msg)


def _node_title_map() -> dict[str, str]:
    catalog = load_roadmap_catalog()
    return {node["id"]: node["title"] for node in catalog["nodes"]}


def _evidence_from_skill_row(row: UserSkillNodeRow | None) -> dict[str, Any]:
    if row is None or not isinstance(row.evidence, dict):
        return {}
    return row.evidence


def get_mentor_report(session: Session, user_id: str) -> MentorReportResponse:
    """Aggregate validation history into a mentor-facing report."""
    user = _ensure_demo_user(session, user_id)

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    diagnosis_raw = profile.diagnosis if profile and profile.diagnosis else load_demo_diagnosis()
    diagnosis = diagnosis_response_from_profile(diagnosis_raw)
    if diagnosis is None:
        diagnosis = DiagnosisResponse.model_validate(diagnosis_raw)

    catalog = load_roadmap_catalog()
    track_title = catalog.get("track", {}).get("title", "Backend Developer")
    goal = (profile.goal if profile and profile.goal else None) or diagnosis.profile.label

    skill_rows = session.scalars(
        select(UserSkillNodeRow).where(UserSkillNodeRow.user_id == user.id),
    ).all()
    skill_by_node = {row.skill_node_id: row for row in skill_rows}

    validations = session.scalars(
        select(Validation)
        .where(Validation.user_id == user.id)
        .order_by(Validation.created_at.asc()),
    ).all()

    titles = _node_title_map()
    entries: list[MentorReportValidationEntry] = []
    for row in validations:
        evidence = _evidence_from_skill_row(skill_by_node.get(row.skill_node_id))
        strengths = list(evidence.get("strengths") or [])
        gaps = list(evidence.get("gaps") or [])
        intervention = str(evidence.get("next_action") or "").strip()
        if not intervention and gaps:
            intervention = f"Revisar com o aluno: {gaps[0]}"

        status = ValidationStatus.APROVADO if row.passed else ValidationStatus.REVISAR
        entries.append(
            MentorReportValidationEntry(
                node_id=row.skill_node_id,
                node_title=titles.get(row.skill_node_id, row.skill_node_id),
                score=row.score,
                status=status,
                strengths=strengths,
                gaps=gaps,
                mentor_summary=row.feedback or "",
                recommended_intervention=intervention,
                validated_at=row.created_at,
            ),
        )

    return MentorReportResponse(
        user_id=user.external_id,
        display_name=user.display_name or user.external_id.replace("-", " ").title(),
        goal=goal,
        track_title=track_title,
        profile_label=diagnosis.profile.label,
        validations=entries,
        learner_gaps=list(diagnosis.gaps),
    )
