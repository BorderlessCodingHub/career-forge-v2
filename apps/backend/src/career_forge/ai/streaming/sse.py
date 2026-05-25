"""SSE adapter — GraphExecutor normalized events → HTTP text/event-stream."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

from career_forge.schemas.forge import RoadmapForgeEvent


def format_sse(event: RoadmapForgeEvent | dict[str, Any]) -> str:
    """Format a domain event as a single SSE data line."""
    payload = event.model_dump() if hasattr(event, "model_dump") else event
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


async def events_to_sse(
    events: AsyncIterator[dict[str, Any]],
) -> AsyncIterator[str]:
    """Pipe normalized executor events into SSE wire format."""
    async for event in events:
        yield format_sse(event)
