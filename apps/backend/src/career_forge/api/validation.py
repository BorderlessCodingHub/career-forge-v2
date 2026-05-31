"""Validation HTTP routes — HAC-10."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import (
    GraphRun,
    GraphRunResult,
    get_graph_run_store,
    unwrap_graph_output,
)
from career_forge.db.session import get_db
from career_forge.schemas.validation import (
    ValidationQuestionsResponse,
    ValidationRequest,
    ValidationResponse,
    ValidationRunResponse,
)
from career_forge.services import planning as planning_service
from career_forge.services import validation as validation_service

router = APIRouter()


@router.get("/questions", response_model=ValidationQuestionsResponse)
def get_validation_questions(
    node_id: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> ValidationQuestionsResponse:
    try:
        return validation_service.build_validation_questions(node_id, db)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("", response_model=ValidationRunResponse)
async def run_validation(
    body: ValidationRequest,
    db: Session = Depends(get_db),
) -> ValidationRunResponse:
    """Run mastery interview evaluation — collect via GraphExecutor."""
    if not body.rubric:
        try:
            questions = validation_service.build_validation_questions(body.node_id, db)
            body = body.model_copy(
                update={"rubric": [question.rubric_criterion for question in questions.questions]},
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    store = get_graph_run_store()
    run = GraphRun(
        graph_name="validation",
        user_id=body.user_id,
        input=body.model_dump(),
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    validation = unwrap_graph_output(result.run.output, ValidationResponse)

    node_status = validation.status.value
    mastery_score = validation.score
    plan_update = None
    graph_patch = None
    roadmap = None

    try:
        _, user_skill = validation_service.persist_validation_result(db, body, validation)
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

    return ValidationRunResponse(
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
