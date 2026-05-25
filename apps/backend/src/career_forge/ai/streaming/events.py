"""Backward-compatible re-export — prefer normalize + stream_events schemas."""

from career_forge.ai.streaming.normalize import normalize_langchain_event
from career_forge.schemas.stream_events import StreamEvent, dump_stream_event, parse_stream_event

__all__ = [
    "StreamEvent",
    "dump_stream_event",
    "normalize_langchain_event",
    "parse_stream_event",
]
