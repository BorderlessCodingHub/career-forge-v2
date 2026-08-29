"""SSE adapter — typed StreamEvent → HTTP text/event-stream."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from fastapi.responses import StreamingResponse

from career_forge.schemas.stream_events import StreamEvent, dump_stream_event

SSE_HEADERS: dict[str, str] = {
    "Cache-Control": "no-cache, no-transform",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}

SSE_CONNECTED_COMMENT = ": connected\n\n"
SSE_KEEPALIVE_COMMENT = ": keepalive\n\n"
# Next.js rewrite proxy defaults to 30s; Cloudflare idle is often ~100s.
SSE_KEEPALIVE_SEC = 15.0


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
    """Immediate comment + periodic keepalive so proxies do not idle-close SSE."""
    yield SSE_CONNECTED_COMMENT
    queue: asyncio.Queue[str | BaseException | None] = asyncio.Queue()

    async def _pump() -> None:
        try:
            async for chunk in events:
                await queue.put(chunk)
            await queue.put(None)
        except BaseException as exc:
            await queue.put(exc)

    task = asyncio.create_task(_pump())
    try:
        while True:
            try:
                item = await asyncio.wait_for(queue.get(), timeout=SSE_KEEPALIVE_SEC)
            except TimeoutError:
                yield SSE_KEEPALIVE_COMMENT
                continue
            if item is None:
                break
            if isinstance(item, BaseException):
                raise item
            yield item
    finally:
        if not task.done():
            task.cancel()
            with suppress(asyncio.CancelledError, Exception):
                await task


def sse_response(body: AsyncIterator[str]) -> StreamingResponse:
    """StreamingResponse with anti-buffer headers for Cloudflare / reverse proxies."""
    return StreamingResponse(
        body,
        media_type="text/event-stream; charset=utf-8",
        headers=dict(SSE_HEADERS),
    )
