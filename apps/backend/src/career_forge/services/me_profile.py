"""Bearer principal profile + optional email store (CAR-29)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.profile import Profile
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user, get_by_external_id
from career_forge.errors import ConflictError
from career_forge.schemas.me_profile import MeProfileResponse
from career_forge.schemas.profile_diagnosis import parse_profile_diagnosis
from career_forge.services.soft_gate import enrich_diagnosis_soft_gate

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"


def get_me_profile(session: Session, external_id: str) -> MeProfileResponse:
    user = get_by_external_id(session, external_id)
    if user is None:
        return MeProfileResponse(external_id=external_id)

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    record = parse_profile_diagnosis(profile.diagnosis) if profile else None
    diagnosis = (
        enrich_diagnosis_soft_gate(record.diagnosis) if record is not None else None
    )
    return MeProfileResponse(
        external_id=external_id,
        email=_public_email(user.email),
        membership_label=user.membership_label,
        membership_entitled=bool(user.membership_entitled),
        has_diagnosis=record is not None,
        diagnosis=diagnosis,
        intake=record.intake if record else None,
    )


def update_me_email(session: Session, external_id: str, email: str) -> str:
    """Store optional recovery email. Replaces synthetic demo emails safely."""
    user = ensure_user(session, external_id)

    other = session.scalar(
        select(User).where(User.email == email, User.id != user.id),
    )
    if other is not None:
        raise ConflictError("email already in use")

    user.email = email
    session.commit()
    session.refresh(user)
    return email


def _public_email(email: str | None) -> str | None:
    """Hide synthetic demo emails from clients (treat as unset)."""
    if not email or email.endswith(_DEMO_EMAIL_SUFFIX):
        return None
    return email
