"""Validation HTTP routes — HAC-10."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.db.session import get_db
from career_forge.schemas.validation import (
    ValidationQuestionsResponse,
    ValidationRequest,
    ValidationResponse,
    ValidationRunResponse,
)
from career_forge.services import validation as validation_service

router = APIRouter()


def _extract_validation(output: dict[str, Any] | None) -> ValidationResponse:
    if output is None:
        msg = "Validation graph completed without output"
        raise ValueError(msg)

    if output.get("type") == "graph_complete" and isinstance(output.get("output"), dict):
        return ValidationResponse.model_validate(output["output"])

    return ValidationResponse.model_validate(output)


@router.get("/questions", response_model=ValidationQuestionsResponse)
def get_validation_questions(
    node_id: str = Query(..., min_length=1),
) -> ValidationQuestionsResponse:
    try:
        return validation_service.build_validation_questions(node_id)
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
            questions = validation_service.build_validation_questions(body.node_id)
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

    validation = _extract_validation(result.run.output)

    try:
        _, user_skill = validation_service.persist_validation_result(db, body, validation)
        node_status = user_skill.status
        mastery_score = user_skill.mastery_score
    except Exception:
        db.rollback()
        node_status = validation.status.value
        mastery_score = validation.score

    return ValidationRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        validation=validation,
        node_id=body.node_id,
        node_status=node_status,
        mastery_score=mastery_score,
    )
