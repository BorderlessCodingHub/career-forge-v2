"""Mock interview HTTP routes — HAC-14, HAC-65 MCQ."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.tools.mock_interview_mcq import generate_mcq_mock_interview
from career_forge.api.deps import EmailExternalId
from career_forge.db.session import get_db
from career_forge.schemas.mock_interview import (
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
    MockInterviewRunResponse,
)
from career_forge.services import assessment_flow
from career_forge.services import mock_interview as mock_interview_service
from career_forge.services.mock_interview_context import build_mock_interview_context
from career_forge.services.roadmap import resolve_skill_node_catalog_entry

router = APIRouter()


@router.get("/questions", response_model=MockInterviewQuestionsResponse)
async def get_mock_interview_questions(
    external_id: EmailExternalId,
    node_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> MockInterviewQuestionsResponse:
    try:
        study_block, learner = build_mock_interview_context(
            db, user_id=external_id, node_id=node_id
        )
        node = resolve_skill_node_catalog_entry(db, node_id)
        return await generate_mcq_mock_interview(
            user_id=external_id,
            node_id=node_id,
            study_block=study_block,
            learner=learner,
            session_db=db,
            node_icon=node.get("icon") or "code",
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=MockInterviewRunResponse)
async def run_mock_interview(
    body: MockInterviewRequest,
    external_id: EmailExternalId,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MockInterviewRunResponse:
    """Run mock interview loop — orchestrated by assessment_flow (MCQ or legacy)."""
    try:
        return await assessment_flow.run_mock_interview(
            db,
            body.model_copy(update={"user_id": external_id}),
            background_tasks,
        )
    except mock_interview_service.McqSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
