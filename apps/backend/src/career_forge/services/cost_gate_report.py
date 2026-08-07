"""CAR-7 cost-gate helpers — pricing, stats, markdown report.

Token usage is captured via LangChain ``UsageMetadataCallbackHandler``.
USD costs use documented OpenAI list prices; BRL uses a fixed FX rate.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any

# OpenAI list prices USD / 1M tokens (docs 2026-07 — gpt-5.4 family + nano).
# Keys match model name prefixes (longest match wins).
MODEL_PRICING_USD_PER_1M: dict[str, dict[str, float]] = {
    "gpt-5.4-mini": {"input": 0.75, "cached_input": 0.075, "output": 4.50},
    "gpt-5.4-nano": {"input": 0.20, "cached_input": 0.02, "output": 1.25},
    "gpt-5.4": {"input": 2.50, "cached_input": 0.25, "output": 15.00},
    "gpt-4.1-nano": {"input": 0.10, "cached_input": 0.025, "output": 0.40},
    "gpt-4.1-mini": {"input": 0.40, "cached_input": 0.10, "output": 1.60},
    "gpt-4.1": {"input": 2.00, "cached_input": 0.50, "output": 8.00},
}

DEFAULT_FX_USD_BRL = 5.50
HARD_BUDGET_BRL = 500.0
APPROVAL_CEILING_BRL = 700.0
DEFAULT_BUFFER = 1.10


@dataclass
class RunCostRecord:
    run_id: str
    graph_name: str
    goal_id: str | None
    status: str
    duration_sec: float
    exclude_reason: str | None
    usage_by_model: dict[str, dict[str, Any]] = field(default_factory=dict)
    cost_usd: float = 0.0
    cost_brl: float = 0.0
    error: str | None = None


def normalize_model_key(model_name: str) -> str:
    name = model_name.strip().lower()
    # Prefer longest prefix match so gpt-5.4-mini beats gpt-5.4.
    candidates = sorted(MODEL_PRICING_USD_PER_1M.keys(), key=len, reverse=True)
    for key in candidates:
        if name == key or name.startswith(f"{key}-") or name.startswith(key):
            return key
    return name


def cost_usd_from_usage(usage_by_model: dict[str, dict[str, Any]]) -> float:
    """Sum USD from LangChain usage_metadata-shaped dicts."""
    total = 0.0
    for model_name, usage in usage_by_model.items():
        key = normalize_model_key(model_name)
        prices = MODEL_PRICING_USD_PER_1M.get(key)
        if prices is None:
            # Unknown model — treat all tokens as expensive gpt-5.4 input/output.
            prices = MODEL_PRICING_USD_PER_1M["gpt-5.4"]
        input_tokens = int(usage.get("input_tokens") or 0)
        output_tokens = int(usage.get("output_tokens") or 0)
        details = usage.get("input_token_details") or {}
        cached = int(details.get("cache_read") or 0)
        billed_input = max(input_tokens - cached, 0)
        total += billed_input / 1_000_000 * prices["input"]
        total += cached / 1_000_000 * prices["cached_input"]
        total += output_tokens / 1_000_000 * prices["output"]
    return total


def to_brl(usd: float, fx: float = DEFAULT_FX_USD_BRL) -> float:
    return usd * fx


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    if len(values) == 1:
        return values[0]
    ordered = sorted(values)
    if p <= 0:
        return ordered[0]
    if p >= 100:
        return ordered[-1]
    # Nearest-rank (inclusive) — stable for small N gate samples.
    rank = math.ceil(p / 100 * len(ordered)) - 1
    return ordered[max(0, min(rank, len(ordered) - 1))]


def summarize_costs(records: list[RunCostRecord]) -> dict[str, Any]:
    completed = [r for r in records if r.status == "completed"]
    by_graph: dict[str, list[RunCostRecord]] = {}
    by_goal: dict[str, list[RunCostRecord]] = {}
    for rec in completed:
        by_graph.setdefault(rec.graph_name, []).append(rec)
        goal = rec.goal_id or "_none"
        by_goal.setdefault(goal, []).append(rec)

    def _bucket(rows: list[RunCostRecord]) -> dict[str, Any]:
        costs = [r.cost_brl for r in rows]
        return {
            "n": len(rows),
            "mean_brl": statistics.fmean(costs) if costs else 0.0,
            "p95_brl": percentile(costs, 95),
            "max_brl": max(costs) if costs else 0.0,
            "sum_brl": sum(costs),
            "mean_usd": statistics.fmean([r.cost_usd for r in rows]) if rows else 0.0,
            "p95_usd": percentile([r.cost_usd for r in rows], 95) if rows else 0.0,
        }

    return {
        "total_runs": len(records),
        "completed": len(completed),
        "failed": len(records) - len(completed),
        "overall": _bucket(completed),
        "by_graph": {name: _bucket(rows) for name, rows in sorted(by_graph.items())},
        "by_goal": {name: _bucket(rows) for name, rows in sorted(by_goal.items())},
        "forge": _bucket(by_graph.get("roadmap_forge", [])),
    }


def project_monthly_spend_brl(
    *,
    forge_p95_brl: float,
    diagnosis_p95_brl: float,
    other_p95_brl: float,
    students: int,
    forges_per_user: int,
    diagnosis_runs_per_user: int,
    other_runs_per_user: int,
    buffer: float = DEFAULT_BUFFER,
) -> dict[str, float]:
    per_user = (
        forges_per_user * forge_p95_brl
        + diagnosis_runs_per_user * diagnosis_p95_brl
        + other_runs_per_user * other_p95_brl
    )
    raw = students * per_user
    buffered = raw * buffer
    return {
        "per_user_brl": per_user,
        "raw_brl": raw,
        "buffered_brl": buffered,
        "buffer": buffer,
    }


def render_report(
    *,
    records: list[RunCostRecord],
    summary: dict[str, Any],
    projection: dict[str, float],
    fx: float,
    hard_budget: float,
    approval_ceiling: float,
    assumptions: dict[str, Any],
    pricing_note: str,
    batch_id: str,
    generated_at: datetime | None = None,
    report_title: str = "Career Forge — F1 cost gate report (CAR-7)",
    method_extra: str | None = None,
) -> str:
    stamp = (generated_at or datetime.now(UTC)).strftime("%Y-%m-%d %H:%M UTC")
    forge = summary["forge"]
    buffered = projection["buffered_brl"]
    if buffered <= hard_budget:
        verdict = "GO — projected P95 spend ≤ hard stop R$500"
    elif buffered <= approval_ceiling:
        verdict = "CONDITIONAL — between hard stop R$500 and approval ceiling R$700 (Yuri call)"
    else:
        verdict = "NO-GO — projected P95 spend > approval ceiling R$700"

    lines: list[str] = [
        f"# {report_title}",
        "",
        f"> Generated: **{stamp}** · batch `{batch_id}`",
        f"> FX: **1 USD = {fx:.2f} BRL** (fixed for this report)",
        f"> Hard stop: **R${hard_budget:.0f}/mo** · Approval ceiling: **R${approval_ceiling:.0f}/mo**",
        "",
        "## Verdict (for Yuri)",
        "",
        f"**{verdict}**",
        "",
        f"- Projected monthly (buffered): **R${buffered:.2f}**",
        f"- Per-user P95 mix: **R${projection['per_user_brl']:.2f}**",
        "",
        "## Method",
        "",
        "- Synthetic GraphRuns with `input._cost.synthetic_gate = true` (excluded from student pool).",
        "- Token usage via LangChain `UsageMetadataCallbackHandler` (preferred when LangSmith is unavailable;",
        "  same token→USD math when LangSmith ingest is healthy).",
        "- Diagnosis samples are **start-phase only** (cheap); full multi-turn CTRR would cost more —",
        "  forge P95 still dominates the monthly projection under the per-user forge cap.",
        "- `validation` / `mentor` graphs are currently deterministic (near-zero LLM cost).",
        f"- {pricing_note}",
        f"- Buffer on projection: **{projection['buffer']:.0%}** (matches `COST_BUFFER_FACTOR`).",
    ]
    if method_extra:
        lines.append(f"- {method_extra}")
    lines.extend(
        [
            "",
            "## Assumptions (pilot projection)",
            "",
        ]
    )
    for key, value in assumptions.items():
        lines.append(f"- `{key}`: {value}")

    lines.extend(
        [
            "",
            "## Forge summary (`roadmap_forge`)",
            "",
            f"| Metric | Value |",
            f"|--------|-------|",
            f"| N completed | {forge['n']} |",
            f"| Mean BRL | R${forge['mean_brl']:.4f} |",
            f"| **P95 BRL** | **R${forge['p95_brl']:.4f}** |",
            f"| Max BRL | R${forge['max_brl']:.4f} |",
            f"| Mean USD | ${forge['mean_usd']:.4f} |",
            f"| P95 USD | ${forge['p95_usd']:.4f} |",
            "",
            "## By graph_name",
            "",
            "| graph_name | n | mean BRL | P95 BRL | max BRL |",
            "|------------|---|----------|---------|---------|",
        ]
    )
    for name, bucket in summary["by_graph"].items():
        lines.append(
            f"| `{name}` | {bucket['n']} | R${bucket['mean_brl']:.4f} | "
            f"R${bucket['p95_brl']:.4f} | R${bucket['max_brl']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## By goal (completed runs)",
            "",
            "| goal_id | n | mean BRL | P95 BRL | max BRL |",
            "|---------|---|----------|---------|---------|",
        ]
    )
    for name, bucket in summary["by_goal"].items():
        lines.append(
            f"| `{name}` | {bucket['n']} | R${bucket['mean_brl']:.4f} | "
            f"R${bucket['p95_brl']:.4f} | R${bucket['max_brl']:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Recommended env after approval",
            "",
            "```bash",
            f"COST_P95_BRL_PER_RUN={forge['p95_brl']:.4f}",
            f"COST_BUFFER_FACTOR={projection['buffer']:.2f}",
            f"COST_FX_USD_BRL={fx:.2f}",
            "MONTHLY_API_BUDGET_BRL=500",
            "FORGE_CAP_PER_USER_MONTH=2",
            "```",
            "",
            "## Run ledger (completed + failed)",
            "",
            "| run_id | graph | goal | status | BRL | sec |",
            "|--------|-------|------|--------|-----|-----|",
        ]
    )
    for rec in records:
        lines.append(
            f"| `{rec.run_id[:8]}` | `{rec.graph_name}` | `{rec.goal_id or '-'}` | "
            f"{rec.status} | R${rec.cost_brl:.4f} | {rec.duration_sec:.1f} |"
        )

    lines.extend(["", "---", "", "_CAR-7 synthetic cost gate — no real students._", ""])
    return "\n".join(lines)


def records_to_jsonable(records: list[RunCostRecord]) -> list[dict[str, Any]]:
    return [asdict(r) for r in records]
