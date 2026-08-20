"""Tests for LangSmith trace metadata (CAR-42)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.ai.run import GraphRun
from career_forge.ai.tools.gap_classifier import OpenAiGapClassifier
from career_forge.ai.tools.tutor_llm import OpenAiTutor, TutorReplyDraft
from career_forge.ai.tracing import (
    TRACE_INPUT_KEY,
    build_trace_config,
    llm_trace_context,
    llm_trace_context_from_run,
    parse_trace_from_input,
    require_trace_from_input,
    with_trace_input,
)
from career_forge.config import settings
from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID


def test_build_trace_config_from_graph_run() -> None:
    run = GraphRun(
        graph_name="tutor",
        user_id="student-1",
        input={"node_id": "node-a", "goal_id": "rag-engineer"},
    )
    config = build_trace_config(run)

    assert config["run_name"] == "tutor"
    assert config["metadata"]["user_id"] == "student-1"
    assert config["metadata"]["graph_name"] == "tutor"
    assert config["metadata"]["graph_run_id"] == run.id
    assert config["metadata"]["node_id"] == "node-a"
    assert config["metadata"]["goal_id"] == "rag-engineer"
    assert config["metadata"]["environment"] == (settings.env.strip().lower() or "production")
    assert config["metadata"]["billable"] is True
    assert config["metadata"]["exclude_reason"] is None
    assert "graph:tutor" in config["tags"]
    assert "user:student-1" in config["tags"]
    assert f"env:{config['metadata']['environment']}" in config["tags"]


def test_demo_ana_marked_not_billable() -> None:
    run = GraphRun(
        graph_name="tutor",
        user_id=DEMO_ANA_EXTERNAL_ID,
        input={"message": "hello"},
    )
    config = build_trace_config(run)

    assert config["metadata"]["billable"] is False
    assert config["metadata"]["exclude_reason"] == "demo"


def test_trace_operation_tag_and_metadata() -> None:
    ctx = llm_trace_context(
        user_id="student-2",
        graph_name="roadmap_forge",
        run_input={"goal_id": "agent-engineer"},
        operation="planner",
    )
    config = build_trace_config(ctx)

    assert config["run_name"] == "roadmap_forge"
    assert config["metadata"]["operation"] == "planner"
    assert "op:planner" in config["tags"]


def test_with_trace_input_roundtrip() -> None:
    run = GraphRun(
        graph_name="tutor",
        user_id="student-3",
        input={"node_id": "n1", "message": "test"},
    )
    enriched = with_trace_input(run)
    assert TRACE_INPUT_KEY in enriched.input

    parsed = parse_trace_from_input(enriched.input)
    assert parsed is not None
    assert parsed.user_id == "student-3"
    assert parsed.graph_name == "tutor"
    assert parsed.graph_run_id == run.id
    assert parsed.run_input is not None
    assert parsed.run_input.get("node_id") == "n1"


def test_parse_trace_from_input_warns_on_malformed(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("WARNING")
    assert parse_trace_from_input({TRACE_INPUT_KEY: "not-a-dict"}) is None
    assert "Invalid _trace" in caplog.text


def test_require_trace_from_input_synthesizes_when_missing(
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level("WARNING")
    trace = require_trace_from_input(
        {"user_id": "student-5", "node_id": "n3"},
        graph_name="tutor",
    )
    assert trace.user_id == "student-5"
    assert trace.graph_name == "tutor"
    assert trace.run_input is not None
    assert trace.run_input.get("node_id") == "n3"
    assert "Missing _trace" in caplog.text


def test_structured_tool_client_forwards_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    class FakeStructured:
        def invoke(self, messages, config=None):
            captured["config"] = config
            return {"reply": "ok", "used_concepts": ["venv"]}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    client = StructuredToolClient(
        model_env="TUTOR_MODEL",
        default_model="gpt-5.4-mini",
        api_key="test-key",
    )
    monkeypatch.setattr(client, "_chat", MagicMock())
    monkeypatch.setattr(
        client._chat,
        "with_structured_output",
        lambda *args, **kwargs: FakeStructured(),
    )

    trace = llm_trace_context_from_run(
        GraphRun(graph_name="tutor", user_id="student-4", input={"node_id": "n2"}),
    )
    client.invoke(
        system="sys",
        user="usr",
        schema=TutorReplyDraft,
        trace=trace,
    )

    assert captured["config"] is not None
    assert captured["config"]["run_name"] == "tutor"
    assert captured["config"]["metadata"]["user_id"] == "student-4"


def test_tutor_forwards_trace_via_client(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    class FakeStructured:
        def invoke(self, messages, config=None):
            captured["config"] = config
            return {"reply": "ok", "used_concepts": ["venv"]}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    tutor = OpenAiTutor(api_key="test-key")
    monkeypatch.setattr(tutor._client, "_chat", MagicMock())
    monkeypatch.setattr(
        tutor._client._chat,
        "with_structured_output",
        lambda *args, **kwargs: FakeStructured(),
    )

    trace = llm_trace_context_from_run(
        GraphRun(graph_name="tutor", user_id="student-4", input={"node_id": "n2"}),
    )
    tutor._invoke(
        message="What is venv?",
        history=[],
        context=MagicMock(
            node_title="Chapter",
            node_id="n2",
            key_concepts=["venv"],
            references=[],
            open_gaps=[],
        ),
        trace=trace,
    )

    assert captured["config"]["run_name"] == "tutor"


def test_gap_classifier_forwards_trace_and_operation(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict = {}

    class FakeStructured:
        def invoke(self, messages, config=None):
            captured["config"] = config
            return {"gaps": []}

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    classifier = OpenAiGapClassifier(api_key="test-key")
    monkeypatch.setattr(classifier._client, "_chat", MagicMock())
    monkeypatch.setattr(
        classifier._client._chat,
        "with_structured_output",
        lambda *args, **kwargs: FakeStructured(),
    )

    trace = llm_trace_context(
        user_id="student-6",
        graph_name="gap_classifier",
        run_input={"node_id": "n4"},
    )
    classifier._invoke(
        node_title="Chapter",
        learner_summary=None,
        wrong_items=[],
        trace=trace,
    )

    assert captured["config"]["run_name"] == "gap_classifier"
    assert captured["config"]["metadata"]["operation"] == "gap_classify"
    assert "op:gap_classify" in captured["config"]["tags"]
