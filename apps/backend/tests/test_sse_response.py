"""SSE response helpers — anti-buffer headers and connected comment."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

import pytest

from career_forge.ai.streaming.sse import (
    SSE_CONNECTED_COMMENT,
    SSE_HEADERS,
    SSE_KEEPALIVE_COMMENT,
    sse_connected_body,
    sse_response,
)


async def _lines(*chunks: str) -> AsyncIterator[str]:
    for chunk in chunks:
        yield chunk


@pytest.mark.asyncio
async def test_sse_connected_body_yields_connected_comment_first() -> None:
    chunks: list[str] = []
    async for line in sse_connected_body(_lines("event: ping\n\n")):
        chunks.append(line)

    assert chunks[0] == SSE_CONNECTED_COMMENT
    assert chunks[1] == "event: ping\n\n"


@pytest.mark.asyncio
async def test_sse_connected_body_emits_keepalive_while_upstream_is_idle(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("career_forge.ai.streaming.sse.SSE_KEEPALIVE_SEC", 0.02)

    async def _delayed() -> AsyncIterator[str]:
        await asyncio.sleep(0.05)
        yield "event: ping\n\n"

    chunks: list[str] = []
    async for line in sse_connected_body(_delayed()):
        chunks.append(line)

    assert chunks[0] == SSE_CONNECTED_COMMENT
    assert SSE_KEEPALIVE_COMMENT in chunks
    assert chunks[-1] == "event: ping\n\n"


def test_sse_response_sets_anti_buffer_headers() -> None:
    response = sse_response(_lines("event: ping\n\n"))

    assert response.media_type == "text/event-stream; charset=utf-8"
    assert response.headers["cache-control"] == SSE_HEADERS["Cache-Control"]
    assert response.headers["x-accel-buffering"] == SSE_HEADERS["X-Accel-Buffering"]
    assert response.headers["connection"] == SSE_HEADERS["Connection"]
