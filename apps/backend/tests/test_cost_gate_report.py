"""Unit tests for CAR-7 cost gate report helpers (no LLM)."""

from __future__ import annotations

import pytest

from career_forge.services.cost_gate_report import (
    RunCostRecord,
    cost_usd_from_usage,
    normalize_model_key,
    percentile,
    project_monthly_spend_brl,
    render_report,
    summarize_costs,
    to_brl,
)


def test_normalize_prefers_mini_over_base() -> None:
    assert normalize_model_key("gpt-5.4-mini-2026-03-17") == "gpt-5.4-mini"
    assert normalize_model_key("gpt-5.4-2026-03-05") == "gpt-5.4"


def test_cost_usd_accounts_for_cache() -> None:
    usage = {
        "gpt-5.4-2026-03-05": {
            "input_tokens": 10_000,
            "output_tokens": 1_000,
            "input_token_details": {"cache_read": 4_000},
        }
    }
    # billed input 6000 * 2.50/1e6 + cache 4000 * 0.25/1e6 + out 1000 * 15/1e6
    expected = 6000 * 2.50 / 1e6 + 4000 * 0.25 / 1e6 + 1000 * 15.0 / 1e6
    assert cost_usd_from_usage(usage) == pytest.approx(expected)


def test_percentile_p95() -> None:
    values = [float(i) for i in range(1, 21)]
    assert percentile(values, 95) == 19.0


def test_summarize_and_projection() -> None:
    records = [
        RunCostRecord(
            run_id="a",
            graph_name="roadmap_forge",
            goal_id="rag-engineer",
            status="completed",
            duration_sec=1.0,
            exclude_reason="synthetic_gate",
            cost_usd=0.1,
            cost_brl=0.55,
        ),
        RunCostRecord(
            run_id="b",
            graph_name="roadmap_forge",
            goal_id="agent-engineer",
            status="completed",
            duration_sec=1.0,
            exclude_reason="synthetic_gate",
            cost_usd=0.2,
            cost_brl=1.10,
        ),
        RunCostRecord(
            run_id="c",
            graph_name="diagnosis_interview",
            goal_id="rag-engineer",
            status="completed",
            duration_sec=1.0,
            exclude_reason="synthetic_gate",
            cost_usd=0.01,
            cost_brl=0.055,
        ),
    ]
    summary = summarize_costs(records)
    assert summary["forge"]["n"] == 2
    assert summary["forge"]["p95_brl"] == 1.10
    projection = project_monthly_spend_brl(
        forge_p95_brl=1.10,
        diagnosis_p95_brl=0.055,
        other_p95_brl=0.0,
        students=30,
        forges_per_user=2,
        diagnosis_runs_per_user=4,
        other_runs_per_user=0,
        buffer=1.10,
    )
    # per user = 2*1.10 + 4*0.055 = 2.42; *30 = 72.6; *1.1 = 79.86
    assert abs(projection["buffered_brl"] - 79.86) < 1e-6
    md = render_report(
        records=records,
        summary=summary,
        projection=projection,
        fx=5.5,
        hard_budget=500,
        approval_ceiling=700,
        assumptions={"students": 30},
        pricing_note="test prices",
        batch_id="test",
    )
    assert "GO —" in md
    assert "roadmap_forge" in md
    assert to_brl(1.0, 5.5) == 5.5
