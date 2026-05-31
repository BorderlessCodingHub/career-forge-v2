"""Persist confirmed diagnosis to profiles — forge motor input loader (HAC-52)."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.profile import Profile
from career_forge.db.models.user import User
from career_forge.errors import ProfileNotFoundError
from career_forge.schemas.profile_diagnosis import (
    DiagnosisConfirmRequest,
    DiagnosisConfirmResponse,
    DiagnosisMotorIntake,
    ProfileDiagnosisRecord,
    parse_profile_diagnosis,
)


def resolve_or_create_user(
    session: Session,
    external_id: str,
    *,
    display_name: str | None = None,
) -> User:
    user = session.scalar(select(User).where(User.external_id == external_id))
    if user is not None:
        if display_name and user.display_name != display_name:
            user.display_name = display_name
        return user

    user = User(
        external_id=external_id,
        display_name=display_name or external_id,
    )
    session.add(user)
    session.flush()
    return user


def confirm_diagnosis(
    session: Session,
    body: DiagnosisConfirmRequest,
) -> DiagnosisConfirmResponse:
    user = resolve_or_create_user(
        session,
        body.user_id,
        display_name=body.display_name,
    )
    intake = DiagnosisMotorIntake(
        goal_id=body.goal_id,
        motivation=body.motivation,
        years_xp=body.years_xp,
        cv=body.cv,
        answers=body.answers,
        cv_signals=body.cv_signals,
    )
    record = ProfileDiagnosisRecord(diagnosis=body.diagnosis, intake=intake)
    track_id = body.diagnosis.profile.track_id

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None:
        profile = Profile(
            user_id=user.id,
            track_id=track_id,
            goal=body.goal_id,
            motivation=body.motivation,
            diagnosis=record.model_dump(mode="json"),
        )
        session.add(profile)
    else:
        profile.track_id = track_id
        profile.goal = body.goal_id
        profile.motivation = body.motivation
        profile.diagnosis = record.model_dump(mode="json")

    session.commit()
    session.refresh(profile)

    return DiagnosisConfirmResponse(
        user_id=body.user_id,
        profile_id=str(profile.id),
    )


def load_forge_motor_input(session: Session, external_id: str) -> dict[str, Any]:
    """Build forge GraphRun input from persisted profile."""
    user = session.scalar(select(User).where(User.external_id == external_id))
    if user is None:
        raise ProfileNotFoundError(f"User {external_id!r} not found")

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    if profile is None or profile.diagnosis is None:
        raise ProfileNotFoundError(f"No confirmed diagnosis for user {external_id!r}")

    record = parse_profile_diagnosis(profile.diagnosis)
    if record is None:
        raise ProfileNotFoundError(f"No confirmed diagnosis for user {external_id!r}")

    intake = record.intake.model_dump(mode="json")
    return {
        "diagnosis": record.diagnosis.model_dump(mode="json"),
        "goal_id": intake["goal_id"],
        "motivation": intake["motivation"],
        "years_xp": intake.get("years_xp"),
        "cv": intake.get("cv"),
        "answers": intake.get("answers") or {},
        "cv_signals": intake.get("cv_signals"),
    }
