"""Tests for LangChain v2 stream event typing and normalization."""

from __future__ import annotations

import pytest

from career_forge.ai.streaming.langchain_events import (
    LANGCHAIN_GRAPH_EVENT_NAMES,
    LANGCHAIN_STANDARD_EVENT_NAMES,
    emit_chain_end,
    emit_chain_start,
    emit_chain_stream,
    emit_chain_error,
    parse_langchain_event,
)
from career_forge.ai.streaming.normalize import normalize_langchain_event
from career_forge.schemas.forge import ForgeErrorEvent
from career_forge.schemas.stream_events import (
    GraphCompleteEvent,
    GraphProgressEvent,
    InterviewStatusEvent,
    MappingDimensionEvent,
)


def test_langchain_standard_event_catalog_matches_docs() -> None:
    assert "on_chain_stream" in LANGCHAIN_STANDARD_EVENT_NAMES
    assert "on_chat_model_stream" in LANGCHAIN_STANDARD_EVENT_NAMES
    assert "on_custom_event" in LANGCHAIN_STANDARD_EVENT_NAMES
    assert "on_chain_error" in LANGCHAIN_GRAPH_EVENT_NAMES


def test_emit_and_parse_chain_stream_roundtrip() -> None:
    raw = emit_chain_stream(
        "diagnosis_interview",
        "run-1",
        {"type": "interview_status", "phase": "judging"},
    )
    parsed = parse_langchain_event(raw)
    assert parsed["event"] == "on_chain_stream"
    assert parsed["data"]["chunk"]["phase"] == "judging"


def test_normalize_diagnosis_interview_stream_events() -> None:
    status = normalize_langchain_event(
        emit_chain_stream(
            "diagnosis_interview",
            "run-1",
            {"type": "interview_status", "phase": "judging"},
        ),
        "diagnosis_interview",
    )
    assert isinstance(status, InterviewStatusEvent)
    assert status.phase == "judging"

    mapping = normalize_langchain_event(
        emit_chain_stream(
            "diagnosis_interview",
            "run-1",
            {
                "type": "mapping_dimension",
                "item": {
                    "rubric_key": "motivation_goal",
                    "label": "Objetivo",
                    "description": "Por que esse caminho",
                    "confidence": 0.5,
                    "saturated": False,
                    "status": "needs_clarification",
                    "note": "",
                },
                "index": 0,
                "total": 5,
            },
        ),
        "diagnosis_interview",
    )
    assert isinstance(mapping, MappingDimensionEvent)

    complete = normalize_langchain_event(
        emit_chain_end(
            "diagnosis_interview",
            "run-1",
            output={"status": "asking", "session_id": "s1", "questions": []},
        ),
        "diagnosis_interview",
    )
    assert isinstance(complete, GraphCompleteEvent)
    assert complete.graph_name == "diagnosis_interview"


def test_normalize_default_graph_progress_and_error() -> None:
    progress = normalize_langchain_event(
        emit_chain_stream(
            "diagnosis",
            "run-1",
            {"type": "progress", "step": "analyze_signals", "message": "ok"},
        ),
        "diagnosis",
    )
    assert isinstance(progress, GraphProgressEvent)

    error = normalize_langchain_event(
        emit_chain_error("diagnosis_interview", "run-1", "boom"),
        "diagnosis_interview",
    )
    assert isinstance(error, ForgeErrorEvent)
    assert error.message == "boom"


def test_parse_langchain_event_rejects_unknown_event() -> None:
    with pytest.raises(ValueError, match="unsupported LangChain stream event"):
        parse_langchain_event({"event": "on_unknown", "name": "x", "run_id": "1", "data": {}})


def test_chain_start_has_no_client_event() -> None:
    assert (
        normalize_langchain_event(
            emit_chain_start("roadmap_forge", "run-1"),
            "roadmap_forge",
        )
        is None
    )
