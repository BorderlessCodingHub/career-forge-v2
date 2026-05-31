"""Mock interview HTTP routes — HAC-14, HAC-65 MCQ."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.tools.mock_interview_mcq import generate_mcq_mock_interview
from career_forge.db.session import get_db
from career_forge.schemas.mock_interview import (
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
    MockInterviewRunResponse,
)
from career_forge.services import assessment_flow
from career_forge.services import mock_interview as mock_interview_service
from career_forge.services.mock_interview_context import build_mock_interview_context
from career_forge.services.roadmap import get_skill_node_context

router = APIRouter()


@router.get("/questions", response_model=MockInterviewQuestionsResponse)
async def get_mock_interview_questions(
    node_id: str = Query(..., min_length=1),
    user_id: str = Query("demo-ana", min_length=1),
    db: Session = Depends(get_db),
) -> MockInterviewQuestionsResponse:
    try:
        study_block, learner = build_mock_interview_context(db, user_id=user_id, node_id=node_id)
        node = get_skill_node_context(db, node_id)
        return await generate_mcq_mock_interview(
            user_id=user_id,
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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> MockInterviewRunResponse:
    """Run mock interview loop — orchestrated by assessment_flow (MCQ or legacy)."""
    try:
        return await assessment_flow.run_mock_interview(db, body, background_tasks)
    except mock_interview_service.McqSessionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
