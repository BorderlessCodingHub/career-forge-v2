"""SSE adapter — typed StreamEvent → HTTP text/event-stream."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from fastapi.responses import StreamingResponse

from career_forge.schemas.stream_events import StreamEvent, dump_stream_event

SSE_HEADERS: dict[str, str] = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

SSE_CONNECTED_COMMENT = ": connected\n\n"


def format_sse(event: StreamEvent | dict[str, Any]) -> str:
    """Format a domain event as SSE with explicit event name + JSON payload."""
    payload = dump_stream_event(event) if not isinstance(event, dict) else event
    event_name = str(payload.get("type", "message"))
    data = json.dumps(payload, ensure_ascii=False)
    return f"event: {event_name}\ndata: {data}\n\n"


async def events_to_sse(
    events: AsyncIterator[dict[str, Any] | StreamEvent],
) -> AsyncIterator[str]:
    """Pipe normalized executor events into SSE wire format."""
    async for event in events:
        yield format_sse(event)


async def sse_connected_body(
    events: AsyncIterator[str],
) -> AsyncIterator[str]:
    """Yield an immediate SSE comment so proxies flush before slow upstream work."""
    yield SSE_CONNECTED_COMMENT
    async for chunk in events:
        yield chunk


def sse_response(body: AsyncIterator[str]) -> StreamingResponse:
    """StreamingResponse with anti-buffer headers for Cloudflare / reverse proxies."""
    return StreamingResponse(
        body,
        media_type="text/event-stream; charset=utf-8",
        headers=dict(SSE_HEADERS),
    )
