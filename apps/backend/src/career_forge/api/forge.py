"""Forge HTTP routes — sync collect + SSE stream via GraphExecutor."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.ai.streaming.sse import events_to_sse

router = APIRouter()


class ForgeRunRequest(BaseModel):
    user_id: str = Field(default="demo-ana")
    input: dict[str, Any] = Field(default_factory=dict)


class ForgeRunResponse(BaseModel):
    run_id: str
    status: str
    events: list[dict[str, Any]]
    output: dict[str, Any] | None = None


@router.post("", response_model=ForgeRunResponse)
async def forge_run(body: ForgeRunRequest) -> ForgeRunResponse:
    """Start roadmap forge — collect full result (no SSE to client)."""
    store = get_graph_run_store()
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id=body.user_id,
        input=body.input,
    )
    store.save(run)

    executor = get_graph_executor()
    result = await executor.execute(run, stream=False)
    assert isinstance(result.run, GraphRun)

    return ForgeRunResponse(
        run_id=result.run.id,
        status=result.run.status,
        events=result.events,
        output=result.run.output,
    )


@router.get("/stream")
async def forge_stream_demo() -> StreamingResponse:
    """Demo SSE endpoint — creates ephemeral run and streams mock forge events."""
    run = GraphRun(graph_name="roadmap_forge", user_id="demo-ana")
    executor = get_graph_executor()
    event_iter = await executor.execute(run, stream=True)
    assert not isinstance(event_iter, GraphRunResult)

    async def sse_body():
        async for line in events_to_sse(event_iter):
            yield line

    return StreamingResponse(sse_body(), media_type="text/event-stream")


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
        async for line in events_to_sse(event_iter):
            yield line

    return StreamingResponse(sse_body(), media_type="text/event-stream")
