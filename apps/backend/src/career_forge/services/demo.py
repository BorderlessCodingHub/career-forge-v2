"""Demo bootstrap — hydrate Ana state for pitch mode."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID, load_demo_diagnosis
from career_forge.db.models.profile import Profile
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode
from career_forge.db.models.validation import Validation
from career_forge.schemas.demo import DemoAnaResponse, DemoValidationSummary
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.services.roadmap import get_user_roadmap


def get_demo_ana(session: Session) -> DemoAnaResponse:
    """Return Ana demo bundle — ensures seed exists if user missing."""
    from scripts.seed import seed_demo_ana

    user = session.scalar(select(User).where(User.external_id == DEMO_ANA_EXTERNAL_ID))
    if user is None:
        seed_demo_ana(session)
        user = session.scalar(select(User).where(User.external_id == DEMO_ANA_EXTERNAL_ID))
        if user is None:
            msg = "Failed to seed demo user Ana"
            raise RuntimeError(msg)

    profile = session.scalar(select(Profile).where(Profile.user_id == user.id))
    from career_forge.schemas.profile_diagnosis import diagnosis_response_from_profile

    diagnosis_raw = profile.diagnosis if profile else load_demo_diagnosis()
    diagnosis = diagnosis_response_from_profile(diagnosis_raw)
    if diagnosis is None:
        diagnosis = DiagnosisResponse.model_validate(diagnosis_raw)

    validations = session.scalars(
        select(Validation)
        .where(Validation.user_id == user.id)
        .order_by(Validation.created_at.asc()),
    ).all()

    validation_summaries = [
        DemoValidationSummary(
            node_id=row.skill_node_id,
            score=row.score,
            passed=row.passed,
            feedback=row.feedback,
        )
        for row in validations
    ]

    return DemoAnaResponse(
        user_id=DEMO_ANA_EXTERNAL_ID,
        display_name=user.display_name or "Ana",
        diagnosis=diagnosis,
        roadmap=get_user_roadmap(session, DEMO_ANA_EXTERNAL_ID),
        validations=validation_summaries,
        pitch_node_id="rest",
    )
