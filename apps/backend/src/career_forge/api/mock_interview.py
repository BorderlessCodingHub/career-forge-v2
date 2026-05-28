"""Mock interview HTTP routes — HAC-14."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.db.session import get_db
from career_forge.schemas.mock_interview import (
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
    MockInterviewRunResponse,
)
from career_forge.schemas.validation import ValidationResponse
from career_forge.services import mock_interview as mock_interview_service
from career_forge.services import planning as planning_service

router = APIRouter()


def _extract_validation(output: dict[str, Any] | None) -> ValidationResponse:
    if output is None:
        msg = "Mock interview graph completed without output"
        raise ValueError(msg)

    if output.get("type") == "graph_complete" and isinstance(output.get("output"), dict):
        return ValidationResponse.model_validate(output["output"])

    return ValidationResponse.model_validate(output)


@router.get("/questions", response_model=MockInterviewQuestionsResponse)
def get_mock_interview_questions(
    node_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> MockInterviewQuestionsResponse:
    try:
        return mock_interview_service.build_mock_interview_questions(node_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=MockInterviewRunResponse)
async def run_mock_interview(
    body: MockInterviewRequest,
    db: Session = Depends(get_db),
) -> MockInterviewRunResponse:
    """Run mock interview loop — evaluate 5–7 answers and recalibrate trail."""
    if not body.rubric:
        try:
            questions = mock_interview_service.build_mock_interview_questions(body.node_id, db)
            body = body.model_copy(
                update={"rubric": [question.rubric_criterion for question in questions.questions]},
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    store = get_graph_run_store()
    run = GraphRun(
        graph_name="mock_interview",
        user_id=body.user_id,
        input=body.model_dump(),
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    validation = _extract_validation(result.run.output)

    node_status = validation.status.value
    mastery_score = validation.score
    plan_update = None
    graph_patch = None
    roadmap = None

    persist_payload = body
    try:
        _, user_skill = mock_interview_service.persist_mock_interview_result(
            db, persist_payload, validation,
        )
        node_status = user_skill.status
        mastery_score = user_skill.mastery_score
    except Exception:
        db.rollback()

    try:
        roadmap, graph_patch, plan_update = planning_service.recalibrate_after_validation(
            db,
            body.user_id,
            body.node_id,
            body.node_title,
            validation,
        )
    except Exception:
        db.rollback()
        roadmap, graph_patch, plan_update = planning_service.recalibrate_from_catalog(
            body.node_id,
            body.node_title,
            validation,
        )

    return MockInterviewRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        validation=validation,
        node_id=body.node_id,
        node_status=node_status,
        mastery_score=mastery_score,
        plan_update=plan_update,
        graph_patch=graph_patch,
        roadmap=roadmap,
    )
