"""Forge HTTP routes — sync collect + SSE stream via GraphExecutor."""

from __future__ import annotations

from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from career_forge.ai.executor import get_graph_executor
from career_forge.ai.run import GraphRun, GraphRunResult, get_graph_run_store
from career_forge.ai.streaming.sse import format_sse, sse_connected_body, sse_response
from career_forge.api.deps import ExternalId
from career_forge.auth.stream_tickets import (
    decode_forge_stream_ticket,
    mint_forge_stream_ticket,
    stream_ticket_ttl_seconds,
)
from career_forge.db.session import get_db
from career_forge.schemas.forge import (
    ForgeRunRequest,
    ForgeRunResponse,
    ForgeStreamTicketResponse,
)
from career_forge.services.cost_guard import get_cost_guard
from career_forge.services.forge_persistence import extract_goal_id, persist_graph_ready
from career_forge.services.lean_forge import apply_lean_forge_input
from career_forge.services.profile_diagnosis import load_forge_motor_input

router = APIRouter()


def _build_forge_input(
    body: ForgeRunRequest,
    motor_input: dict[str, Any] | None,
) -> dict[str, Any]:
    if body.diagnosis is not None:
        merged = {"diagnosis": body.diagnosis.model_dump(mode="json")}
        if body.input.get("goal_id"):
            merged["goal_id"] = body.input["goal_id"]
    elif motor_input is not None:
        merged = dict(motor_input)
    else:
        raise HTTPException(
            status_code=422,
            detail="diagnosis is required when no confirmed profile exists for user_id",
        )
    merged.update(body.input)
    return apply_lean_forge_input(merged)


def _require_owned_run(run_id: str, external_id: str) -> GraphRun:
    store = get_graph_run_store()
    run = store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"GraphRun {run_id} not found")
    if run.user_id != external_id:
        raise HTTPException(status_code=403, detail="Forge run belongs to another user")
    return run


def _validate_stream_ticket(run_id: str, ticket: str | None) -> GraphRun:
    if not ticket:
        raise HTTPException(status_code=401, detail="Missing or invalid stream ticket")
    try:
        claims = decode_forge_stream_ticket(ticket)
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(status_code=401, detail="Missing or invalid stream ticket") from None
    if claims["run_id"] != run_id:
        raise HTTPException(status_code=401, detail="Missing or invalid stream ticket")
    store = get_graph_run_store()
    run = store.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail=f"GraphRun {run_id} not found")
    if run.user_id != claims["sub"]:
        raise HTTPException(status_code=401, detail="Missing or invalid stream ticket")
    return run


@router.post("", response_model=ForgeRunResponse, status_code=202)
@router.post("/runs", response_model=ForgeRunResponse, status_code=202)
async def forge_run(
    body: ForgeRunRequest,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> ForgeRunResponse:
    """Enqueue roadmap forge run — client streams via GET /forge/{run_id}/stream.

    ``POST /forge/runs`` is preferred behind Next.js (App Router page occupies ``/forge``).
    ``POST /forge`` remains for direct API / tests.

    Identity comes from Bearer ``sub`` (ADR-003); body ``user_id`` is ignored.
    """
    motor_input: dict[str, Any] | None = None
    if body.diagnosis is None:
        motor_input = load_forge_motor_input(db, external_id)

    store = get_graph_run_store()
    run = GraphRun(
        graph_name="roadmap_forge",
        user_id=external_id,
        input=_build_forge_input(body, motor_input),
    )
    # Fail fast before enqueue (same gate as GraphExecutor).
    get_cost_guard().check(run)
    store.save(run)

    return ForgeRunResponse(
        run_id=run.id,
        status=run.status,
        events=[],
        output=None,
    )


@router.post("/{run_id}/stream-ticket", response_model=ForgeStreamTicketResponse)
async def forge_stream_ticket(
    run_id: str,
    external_id: ExternalId,
) -> ForgeStreamTicketResponse:
    """Mint a short-lived ticket for EventSource-compatible SSE (CAR-26)."""
    _require_owned_run(run_id, external_id)
    ticket = mint_forge_stream_ticket(external_id, run_id)
    return ForgeStreamTicketResponse(
        ticket=ticket,
        expires_in=stream_ticket_ttl_seconds(),
    )


@router.get("/{run_id}/stream")
async def forge_stream(
    run_id: str,
    ticket: str | None = Query(default=None),
) -> StreamingResponse:
    """Stream forge events for an existing run via GraphExecutor (SSE).

    Requires ``?ticket=`` from ``POST /forge/{run_id}/stream-ticket`` (CAR-26).
    Path remains Bearer-exempt so EventSource / query-ticket clients work.
    """
    run = _validate_stream_ticket(run_id, ticket)

    executor = get_graph_executor()
    event_iter = await executor.execute(run, stream=True)
    assert not isinstance(event_iter, GraphRunResult)

    async def sse_body():
        graph_ready_event: dict[str, Any] | None = None
        async for event in event_iter:
            if isinstance(event, dict) and event.get("type") == "graph_ready":
                graph_ready_event = event
            yield format_sse(event)
        goal_id = extract_goal_id(run.input if isinstance(run.input, dict) else None)
        persist_graph_ready(
            run.user_id,
            graph_ready_event,
            graph_run_id=run.id,
            goal_id=goal_id,
        )

    return sse_response(sse_connected_body(sse_body()))
