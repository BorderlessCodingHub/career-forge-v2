"""Forge SSE HTTP routes — HAC-18."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from career_forge.streaming.forge_stream import stream_forge_events

router = APIRouter()


@router.get("/stream")
def forge_stream() -> StreamingResponse:
    return StreamingResponse(stream_forge_events(), media_type="text/event-stream")
