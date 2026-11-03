"""Learner product note — the signed-in session posts, the server copies the email."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from career_forge.api.deps import ExternalId
from career_forge.db.session import get_db
from career_forge.schemas.learner_feedback import (
    LearnerFeedbackAccepted,
    LearnerFeedbackCreate,
)
from career_forge.services.learner_feedback import submit_learner_feedback

router = APIRouter()


@router.post("/feedback", response_model=LearnerFeedbackAccepted)
def post_learner_feedback(
    body: LearnerFeedbackCreate,
    request: Request,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> LearnerFeedbackAccepted:
    submit_learner_feedback(
        db,
        external_id=external_id,
        message=body.message,
        path=body.path,
        cookie_header=request.headers.get("cookie"),
    )
    return LearnerFeedbackAccepted()
