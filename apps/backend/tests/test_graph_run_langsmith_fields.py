"""CAR-43 — GraphRun LangSmith link fields round-trip via store."""

from __future__ import annotations

from career_forge.ai.run import GraphRun, InMemoryGraphRunStore


def test_graph_run_persists_langsmith_link_fields() -> None:
    store = InMemoryGraphRunStore()
    run = GraphRun(
        graph_name="tutor",
        user_id="student-1",
        input={"node_id": "n1"},
        langsmith_trace_id="01abc-trace",
        actual_cost_usd=0.042,
        token_usage={
            "gpt-4.1-nano": {
                "input_tokens": 100,
                "output_tokens": 20,
            }
        },
    )
    store.save(run)

    loaded = store.get(run.id)
    assert loaded is not None
    assert loaded.langsmith_trace_id == "01abc-trace"
    assert loaded.actual_cost_usd == 0.042
    assert loaded.token_usage == {
        "gpt-4.1-nano": {"input_tokens": 100, "output_tokens": 20}
    }


def test_graph_run_langsmith_fields_default_none() -> None:
    run = GraphRun(graph_name="roadmap_forge", user_id="u1", input={})
    assert run.langsmith_trace_id is None
    assert run.actual_cost_usd is None
    assert run.token_usage is None
