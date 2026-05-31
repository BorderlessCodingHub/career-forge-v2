"""Assessment run orchestration — validation + mock interview (HAC-79).

Owns the GraphRun → executor → unwrap → persist → recalibrate → response
pipeline that the thin API routes delegate to, keeping business logic out of
the transport layer. Both flows share the persist/recalibrate tail via the
private helpers below.
"""

from __future__ import annotations

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import (
    GraphRun,
    GraphRunResult,
    get_graph_run_store,
    unwrap_graph_output,
)
from career_forge.schemas.mock_interview import MockInterviewRequest, MockInterviewRunResponse
from career_forge.schemas.validation import (
    ValidationRequest,
    ValidationResponse,
    ValidationRunResponse,
)
from career_forge.services import knowledge_gaps as knowledge_gaps_service
from career_forge.services import mock_interview as mock_interview_service
from career_forge.services import planning as planning_service
from career_forge.services import validation as validation_service
from career_forge.services.mock_interview_session import (
    MockInterviewSessionRecord,
    consume_mock_interview_session,
)


async def _execute_graph(
    graph_name: str,
    body: ValidationRequest | MockInterviewRequest,
) -> tuple[str, str, list[dict], ValidationResponse]:
    """Run a deterministic assessment graph; return run metadata + validation."""
    store = get_graph_run_store()
    run = GraphRun(graph_name=graph_name, user_id=body.user_id, input=body.model_dump())
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    validation = unwrap_graph_output(result.run.output, ValidationResponse)
    return result.run.id, result.run.status, result.events, validation


def _persist(db: Session, persist_call) -> tuple[str | None, int | None]:
    """Persist an attempt; on failure roll back and signal no status override."""
    try:
        _, user_skill = persist_call()
    except Exception:
        db.rollback()
        return None, None
    return user_skill.status, user_skill.mastery_score


def _recalibrate(
    db: Session,
    body: ValidationRequest | MockInterviewRequest,
    validation: ValidationResponse,
):
    """Adaptive recalibration with catalog fallback when Postgres is unavailable."""
    try:
        return planning_service.recalibrate_after_validation(
            db,
            body.user_id,
            body.node_id,
            body.node_title,
            validation,
        )
    except Exception:
        db.rollback()
        return planning_service.recalibrate_from_catalog(
            body.node_id,
            body.node_title,
            validation,
        )


def _schedule_gap_capture(
    background_tasks: BackgroundTasks,
    mcq_session: MockInterviewSessionRecord,
    body: MockInterviewRequest,
) -> None:
    """Capture gabarito → concept mapping and classify gaps off the critical path."""
    wrong_items, correct_concepts = knowledge_gaps_service.build_gap_capture(mcq_session, body)
    background_tasks.add_task(
        knowledge_gaps_service.classify_and_store_gaps,
        user_id=body.user_id,
        node_id=body.node_id,
        node_title=body.node_title,
        wrong_items=[item.model_dump() for item in wrong_items],
        correct_concepts=correct_concepts,
    )


async def run_validation(db: Session, body: ValidationRequest) -> ValidationRunResponse:
    """Validation interview: backfill rubric → run graph → persist → recalibrate."""
    if not body.rubric:
        questions = validation_service.build_validation_questions(body.node_id, db)
        body = body.model_copy(
            update={"rubric": [question.rubric_criterion for question in questions.questions]},
        )

    run_id, status, events, validation = await _execute_graph("validation", body)

    node_status, mastery_score = validation.status.value, validation.score
    persisted_status, persisted_score = _persist(
        db,
        lambda: validation_service.persist_validation_result(db, body, validation),
    )
    if persisted_status is not None:
        node_status, mastery_score = persisted_status, persisted_score

    roadmap, graph_patch, plan_update = _recalibrate(db, body, validation)

    return ValidationRunResponse(
        run_id=run_id,
        status=status,
        events=events,
        validation=validation,
        node_id=body.node_id,
        node_status=node_status,
        mastery_score=mastery_score,
        plan_update=plan_update,
        graph_patch=graph_patch,
        roadmap=roadmap,
    )


async def run_mock_interview(
    db: Session,
    body: MockInterviewRequest,
    background_tasks: BackgroundTasks,
) -> MockInterviewRunResponse:
    """Mock interview: MCQ gabarito (default) or legacy open-text graph, then
    persist → gap capture → recalibrate."""
    run_id: str | None = None
    events: list[dict] = []
    status = "completed"
    stored_questions: list[dict] | None = None
    mcq_session: MockInterviewSessionRecord | None = None

    if body.session_id:
        validation, mcq_session = mock_interview_service.evaluate_mcq_session(body)
        stored_questions = mcq_session.questions_public
        if not body.rubric:
            body = body.model_copy(update={"rubric": mcq_session.rubric})
    else:
        if not body.rubric:
            questions = mock_interview_service.build_mock_interview_questions(body.node_id, db)
            body = body.model_copy(
                update={"rubric": [question.rubric_criterion for question in questions.questions]},
            )
        run_id, status, events, validation = await _execute_graph("mock_interview", body)

    node_status, mastery_score = validation.status.value, validation.score
    persisted_status, persisted_score = _persist(
        db,
        lambda: mock_interview_service.persist_mock_interview_result(
            db,
            body,
            validation,
            stored_questions=stored_questions,
        ),
    )
    if persisted_status is not None:
        node_status, mastery_score = persisted_status, persisted_score

    if mcq_session is not None:
        _schedule_gap_capture(background_tasks, mcq_session, body)
        consume_mock_interview_session(mcq_session.session_id)

    roadmap, graph_patch, plan_update = _recalibrate(db, body, validation)

    return MockInterviewRunResponse(
        run_id=run_id,
        status=status,
        events=events,
        validation=validation,
        node_id=body.node_id,
        node_status=node_status,
        mastery_score=mastery_score,
        plan_update=plan_update,
        graph_patch=graph_patch,
        roadmap=roadmap,
    )
