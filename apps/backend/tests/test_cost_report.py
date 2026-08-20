"""Unit tests — CAR-43 cost-report rollup (no LangSmith / DB)."""

from __future__ import annotations

from datetime import UTC, datetime

from career_forge.ai.run import GraphRun
from career_forge.services.cost_report import (
    build_cost_report,
    render_cost_report_json,
    render_cost_report_pretty,
)


def _run(
    *,
    graph_name: str,
    cost_usd: float,
    run_id: str,
    trace: str | None = None,
    created: datetime | None = None,
) -> GraphRun:
    return GraphRun(
        id=run_id,
        graph_name=graph_name,
        user_id="pedro-123",
        input={},
        actual_cost_usd=cost_usd,
        langsmith_trace_id=trace,
        created_at=created or datetime(2026, 8, 10, tzinfo=UTC),
    )


def test_build_cost_report_groups_by_graph_and_ranks_top_run() -> None:
    runs = [
        _run(graph_name="roadmap_forge", cost_usd=0.521, run_id="abc123", trace="01a01"),
        _run(graph_name="roadmap_forge", cost_usd=0.321, run_id="abc124"),
        _run(graph_name="tutor", cost_usd=0.156, run_id="t1"),
        _run(graph_name="diagnosis_interview", cost_usd=0.018, run_id="d1"),
        _run(graph_name="mock_interview", cost_usd=0.089, run_id="m1"),
        # other user ignored
        GraphRun(
            graph_name="tutor",
            user_id="other",
            input={},
            actual_cost_usd=9.99,
        ),
    ]
    report = build_cost_report(
        runs,
        user_id="pedro-123",
        since=datetime(2026, 8, 1, tzinfo=UTC),
        until=datetime(2026, 8, 31, tzinfo=UTC),
        fx_usd_brl=5.50,
    )

    assert report.run_count == 5
    assert report.rows[0].graph_name == "roadmap_forge"
    assert report.rows[0].runs == 2
    assert abs(report.rows[0].cost_usd - 0.842) < 1e-9
    assert abs(report.total_usd - 1.105) < 1e-9
    assert report.top_run is not None
    assert report.top_run.run_id == "abc123"
    assert report.top_run.langsmith_trace_id == "01a01"

    pretty = render_cost_report_pretty(report)
    assert "User: pedro-123" in pretty
    assert "roadmap_forge" in pretty
    assert "Top single run: roadmap_forge run abc123" in pretty

    payload = render_cost_report_json(report)
    assert '"user_id": "pedro-123"' in payload
    assert "roadmap_forge" in payload
