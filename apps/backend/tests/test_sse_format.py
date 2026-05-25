"""SSE wire format tests."""

from __future__ import annotations

import json

from career_forge.ai.streaming.sse import format_sse
from career_forge.schemas.stream_events import InterviewStatusEvent


def test_format_sse_emits_event_and_data_lines() -> None:
    wire = format_sse(InterviewStatusEvent(phase="judging"))

    assert wire.startswith("event: interview_status\n")
    assert "data: " in wire
    assert wire.endswith("\n\n")

    data_line = next(line for line in wire.split("\n") if line.startswith("data: "))
    payload = json.loads(data_line.removeprefix("data: "))
    assert payload["type"] == "interview_status"
    assert payload["phase"] == "judging"


def test_format_sse_dict_uses_type_as_event_name() -> None:
    wire = format_sse({"type": "error", "message": "boom"})
    assert wire.startswith("event: error\n")
    payload = json.loads(wire.split("\n")[1].removeprefix("data: "))
    assert payload["message"] == "boom"
