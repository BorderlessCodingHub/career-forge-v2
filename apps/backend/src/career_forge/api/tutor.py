"""Chapter Q&A tutor HTTP routes — HAC-71."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.tracing import with_trace_input
from career_forge.ai.run import (
    GraphRun,
    GraphRunResult,
    get_graph_run_store,
    unwrap_graph_output,
)
from career_forge.api.deps import EmailExternalId
from career_forge.db.session import get_db
from career_forge.schemas.tutor import (
    TutorContext,
    TutorRequest,
    TutorResponse,
    TutorRunResponse,
)
from career_forge.services import tutor as tutor_service

router = APIRouter()


@router.get("/context", response_model=TutorContext)
def get_tutor_context(
    external_id: EmailExternalId,
    node_id: str | None = Query(default=None),
    node_title: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> TutorContext:
    """Chapter grounding (key_concepts + references + open gaps) for tutor UI bootstrap."""
    return tutor_service.load_tutor_context(db, external_id, node_id, node_title)


@router.post("", response_model=TutorRunResponse)
async def chat_with_tutor(
    body: TutorRequest,
    external_id: EmailExternalId,
    db: Session = Depends(get_db),
) -> TutorRunResponse:
    """Run chapter Q&A tutor — collect via GraphExecutor."""
    payload = body.model_copy(update={"user_id": external_id})
    context = tutor_service.load_tutor_context(
        db, external_id, payload.node_id, payload.node_title
    )

    store = get_graph_run_store()
    run = with_trace_input(
        GraphRun(
            graph_name="tutor",
            user_id=external_id,
            input={**payload.model_dump(), "context_snapshot": context.model_dump()},
        )
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result, GraphRunResult)

    tutor = unwrap_graph_output(result.run.output, TutorResponse)

    return TutorRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        tutor=tutor,
    )
