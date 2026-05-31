"""Mock interview HTTP routes — HAC-14, HAC-65 MCQ."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.ai.tools.mock_interview_mcq import generate_mcq_mock_interview
from career_forge.db.session import get_db
from career_forge.schemas.mock_interview import (
    MockInterviewQuestionsResponse,
    MockInterviewRequest,
    MockInterviewRunResponse,
)
from career_forge.schemas.validation import ValidationResponse
from career_forge.services import knowledge_gaps as knowledge_gaps_service
from career_forge.services import mock_interview as mock_interview_service
from career_forge.services import planning as planning_service
from career_forge.services.mock_interview_context import build_mock_interview_context
from career_forge.services.mock_interview_session import consume_mock_interview_session
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
    """Run mock interview loop — MCQ gabarito or legacy open-text graph."""
    run_id: str | None = None
    events: list[dict] = []
    run_status = "completed"
    stored_questions: list[dict] | None = None
    mcq_session = None

    if body.session_id:
        try:
            validation, mcq_session = mock_interview_service.evaluate_mcq_session(body)
            stored_questions = mcq_session.questions_public
            if not body.rubric:
                body = body.model_copy(update={"rubric": mcq_session.rubric})
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
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
        run_id = run.id

        executor = get_graph_executor()
        result = await executor.execute(run, stream=False)
        assert isinstance(result, GraphRunResult)
        run_status = result.run.status
        events = result.events
        validation = unwrap_graph_output(result.run.output, ValidationResponse)

    node_status = validation.status.value
    mastery_score = validation.score
    plan_update = None
    graph_patch = None
    roadmap = None

    try:
        _, user_skill = mock_interview_service.persist_mock_interview_result(
            db,
            body,
            validation,
            stored_questions=stored_questions,
        )
        node_status = user_skill.status
        mastery_score = user_skill.mastery_score
    except Exception:
        db.rollback()

    if mcq_session is not None:
        # Capture gabarito → concept mapping while the session is still alive, then
        # classify gaps off the critical path (fire-and-forget). HAC-67 adaptive memory.
        wrong_items, correct_concepts = knowledge_gaps_service.build_gap_capture(
            mcq_session,
            body,
        )
        background_tasks.add_task(
            knowledge_gaps_service.classify_and_store_gaps,
            user_id=body.user_id,
            node_id=body.node_id,
            node_title=body.node_title,
            wrong_items=[item.model_dump() for item in wrong_items],
            correct_concepts=correct_concepts,
        )
        consume_mock_interview_session(mcq_session.session_id)

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
        run_id=run_id,
        status=run_status,
        events=events,
        validation=validation,
        node_id=body.node_id,
        node_status=node_status,
        mastery_score=mastery_score,
        plan_update=plan_update,
        graph_patch=graph_patch,
        roadmap=roadmap,
    )
