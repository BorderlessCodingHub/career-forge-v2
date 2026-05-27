"""SSE adapter — typed StreamEvent → HTTP text/event-stream."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from career_forge.schemas.stream_events import StreamEvent, dump_stream_event


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
