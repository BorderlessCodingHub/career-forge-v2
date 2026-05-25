"""Forge SSE stream adapter — bridge LangGraph → HTTP (HAC-18)."""

from collections.abc import AsyncIterator

from career_forge.streaming.events import format_sse


async def stream_forge_events() -> AsyncIterator[str]:
    """Placeholder forge stream; yields nothing until HAC-18."""
    if False:  # pragma: no cover
        yield format_sse({"type": "error", "message": "not implemented"})
