"""Validation HTTP routes — HAC-10."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.api.deps import ExternalId
from career_forge.db.session import get_db
from career_forge.schemas.validation import (
    ValidationQuestionsResponse,
    ValidationRequest,
    ValidationRunResponse,
)
from career_forge.services import assessment_flow
from career_forge.services import validation as validation_service

router = APIRouter()


@router.get("/questions", response_model=ValidationQuestionsResponse)
def get_validation_questions(
    external_id: ExternalId,
    node_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> ValidationQuestionsResponse:
    _ = external_id  # Bearer required; questions are catalog-scoped
    try:
        return validation_service.build_validation_questions(node_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=ValidationRunResponse)
async def run_validation(
    body: ValidationRequest,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> ValidationRunResponse:
    """Run mastery interview evaluation — orchestrated by assessment_flow."""
    try:
        return await assessment_flow.run_validation(
            db,
            body.model_copy(update={"user_id": external_id}),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
