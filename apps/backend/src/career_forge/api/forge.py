"""Forge HTTP routes — sync collect + SSE stream via GraphExecutor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.ai.streaming.sse import format_sse
from career_forge.db.session import get_db
from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.services.forge_persistence import persist_graph_ready
from career_forge.services.profile_diagnosis import load_forge_motor_input

router = APIRouter()


class ForgeRunRequest(BaseModel):
    user_id: str = Field(default="demo-ana")
    diagnosis: DiagnosisResponse | None = None
    input: dict[str, Any] = Field(default_factory=dict)


class ForgeRunResponse(BaseModel):
    run_id: str
    status: str
    events: list[dict[str, Any]]
    output: dict[str, Any] | None = None


def _build_forge_input(
    body: ForgeRunRequest,
    motor_input: dict[str, Any] | None,
) -> dict[str, Any]:
    if body.diagnosis is not None:
        merged = {"diagnosis": body.diagnosis.model_dump(mode="json")}
    elif motor_input is not None:
        merged = dict(motor_input)
    else:
        raise HTTPException(
            status_code=422,
            detail="diagnosis is required when no confirmed profile exists for user_id",
        )
    merged.update(body.input)
    return merged


@router.post("", response_model=ForgeRunResponse, status_code=202)
async def forge_run(
    body: ForgeRunRequest,
    db: Session = Depends(get_db),
) -> ForgeRunResponse:
    """Enqueue roadmap forge run — client streams via GET /forge/{run_id}/stream."""
    motor_input: dict[str, Any] | None = None
    if body.diagnosis is None:
        motor_input = load_forge_motor_input(db, body.user_id)

    store = get_graph_run_store()
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id=body.user_id,
        input=_build_forge_input(body, motor_input),
    )
    store.save(run)

    return ForgeRunResponse(
        run_id=run.id,
        status=run.status,
        events=[],
        output=None,
    )


@router.get("/{run_id}/stream")
async def forge_stream(run_id: str) -> StreamingResponse:
    """Stream forge events for an existing run via GraphExecutor (SSE)."""
    store = get_graph_run_store()
    run = store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"GraphRun {run_id} not found")

    executor = get_graph_executor()
    event_iter = await executor.execute(run, stream=True)
    assert not isinstance(event_iter, GraphRunResult)

    async def sse_body():
        graph_ready_event: dict[str, Any] | None = None
        async for event in event_iter:
            if isinstance(event, dict) and event.get("type") == "graph_ready":
                graph_ready_event = event
            yield format_sse(event)
        persist_graph_ready(run.user_id, graph_ready_event)

    return StreamingResponse(sse_body(), media_type="text/event-stream")
