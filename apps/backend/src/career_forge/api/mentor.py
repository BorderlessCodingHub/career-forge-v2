"""Contextual mentor HTTP routes — HAC-13."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import (
    GraphRun,
    GraphRunResult,
    get_graph_run_store,
    unwrap_graph_output,
)
from career_forge.db.session import get_db
from career_forge.schemas.mentor import (
    MentorContextSnapshot,
    MentorRequest,
    MentorResponse,
    MentorRunResponse,
)
from career_forge.services import mentor as mentor_service

router = APIRouter()


@router.get("/context", response_model=MentorContextSnapshot)
def get_mentor_context(
    user_id: str = Query(default="demo-ana"),
    node_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> MentorContextSnapshot:
    """Return learner memory snapshot for mentor UI bootstrap."""
    return mentor_service.load_mentor_context(db, user_id, node_id)


@router.post("", response_model=MentorRunResponse)
async def chat_with_mentor(
    body: MentorRequest,
    db: Session = Depends(get_db),
) -> MentorRunResponse:
    """Run contextual mentor chat — collect via GraphExecutor."""
    context = mentor_service.load_mentor_context(db, body.user_id, body.node_id)

    store = get_graph_run_store()
    run = GraphRun(
        graph_name="mentor",
        user_id=body.user_id,
        input={
            **body.model_dump(),
            "context_snapshot": context.model_dump(),
        },
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    mentor = unwrap_graph_output(result.run.output, MentorResponse)

    return MentorRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        mentor=mentor,
    )
