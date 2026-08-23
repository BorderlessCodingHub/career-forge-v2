"""Mentor report endpoints — HAC-15."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from career_forge.api.deps import EmailExternalId
from career_forge.db.session import get_db
from career_forge.schemas.mentor_report import MentorReportResponse
from career_forge.services.mentor_report import get_mentor_report

router = APIRouter()


@router.get("", response_model=MentorReportResponse)
def mentor_report(
    external_id: EmailExternalId,
    session: Session = Depends(get_db),
) -> MentorReportResponse:
    """Return aggregated learning evidence for Borderless mentors."""
    try:
        return get_mentor_report(session, external_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
