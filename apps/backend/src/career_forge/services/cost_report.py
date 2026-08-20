"""CAR-43 production cost report — rollup GraphRuns by graph_name (not CAR-7 gate)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Iterable, Sequence

from career_forge.ai.run import GraphRun
from career_forge.services.cost_gate_report import DEFAULT_FX_USD_BRL, to_brl


@dataclass(frozen=True)
class GraphCostRow:
    graph_name: str
    runs: int
    cost_usd: float
    cost_brl: float
    pct_total: float


@dataclass(frozen=True)
class TopRun:
    graph_name: str
    run_id: str
    cost_usd: float
    langsmith_trace_id: str | None = None


@dataclass
class CostReport:
    user_id: str
    since: datetime | None
    until: datetime | None
    rows: list[GraphCostRow] = field(default_factory=list)
    total_usd: float = 0.0
    total_brl: float = 0.0
    top_run: TopRun | None = None
    fx_usd_brl: float = DEFAULT_FX_USD_BRL
    run_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["since"] = self.since.isoformat() if self.since else None
        payload["until"] = self.until.isoformat() if self.until else None
        return payload


def _run_cost_usd(run: GraphRun) -> float:
    if run.actual_cost_usd is not None:
        return float(run.actual_cost_usd)
    return 0.0


def build_cost_report(
    runs: Sequence[GraphRun],
    *,
    user_id: str,
    since: datetime | None = None,
    until: datetime | None = None,
    fx_usd_brl: float = DEFAULT_FX_USD_BRL,
) -> CostReport:
    """Aggregate completed-ish runs by graph_name for a student period."""
    filtered = [r for r in runs if r.user_id == user_id]
    if since is not None:
        filtered = [r for r in filtered if r.created_at >= since]
    if until is not None:
        filtered = [r for r in filtered if r.created_at <= until]

    by_graph: dict[str, list[GraphRun]] = {}
    for run in filtered:
        by_graph.setdefault(run.graph_name, []).append(run)

    totals: list[tuple[str, int, float]] = []
    for graph_name, group in by_graph.items():
        cost = sum(_run_cost_usd(r) for r in group)
        totals.append((graph_name, len(group), cost))

    total_usd = sum(cost for _, _, cost in totals)
    rows: list[GraphCostRow] = []
    for graph_name, count, cost_usd in sorted(totals, key=lambda item: item[2], reverse=True):
        pct = (cost_usd / total_usd * 100.0) if total_usd > 0 else 0.0
        rows.append(
            GraphCostRow(
                graph_name=graph_name,
                runs=count,
                cost_usd=cost_usd,
                cost_brl=to_brl(cost_usd, fx_usd_brl),
                pct_total=pct,
            )
        )

    top: TopRun | None = None
    if filtered:
        richest = max(filtered, key=_run_cost_usd)
        top = TopRun(
            graph_name=richest.graph_name,
            run_id=richest.id,
            cost_usd=_run_cost_usd(richest),
            langsmith_trace_id=richest.langsmith_trace_id,
        )

    return CostReport(
        user_id=user_id,
        since=since,
        until=until,
        rows=rows,
        total_usd=total_usd,
        total_brl=to_brl(total_usd, fx_usd_brl),
        top_run=top,
        fx_usd_brl=fx_usd_brl,
        run_count=len(filtered),
    )


def render_cost_report_pretty(report: CostReport) -> str:
    since_s = report.since.date().isoformat() if report.since else "…"
    until_s = report.until.date().isoformat() if report.until else "…"
    lines = [
        f"User: {report.user_id} · Period: {since_s} → {until_s}",
        "",
        f"| {'graph_name':<20} | {'runs':>4} | {'cost_usd':>8} | {'cost_brl':>8} | {'% total':>7} |",
        f"|{'-' * 22}|{'-' * 6}|{'-' * 10}|{'-' * 10}|{'-' * 9}|",
    ]
    for row in report.rows:
        lines.append(
            f"| {row.graph_name:<20} | {row.runs:>4} | ${row.cost_usd:>7.3f} | "
            f"R${row.cost_brl:>6.2f} | {row.pct_total:>6.0f}% |"
        )
    lines.append("")
    lines.append(
        f"Total: ${report.total_usd:.3f} / R${report.total_brl:.2f} "
        f"across {report.run_count} runs (FX={report.fx_usd_brl:.2f})"
    )
    if report.top_run is not None:
        top = report.top_run
        trace = top.langsmith_trace_id or "—"
        lines.append(
            f"Top single run: {top.graph_name} run {top.run_id} — "
            f"${top.cost_usd:.3f} (trace: {trace})"
        )
    return "\n".join(lines) + "\n"


def render_cost_report_json(report: CostReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"


def query_graph_runs_for_report(
    *,
    user_id: str,
    since: datetime | None,
    until: datetime | None,
) -> list[GraphRun]:
    """Load GraphRuns from Postgres for cost-report CLI."""
    from career_forge.db.models.graph_run import GraphRunRecord
    from career_forge.db.session import SessionLocal
    from career_forge.db.stores.postgres_graph_run import record_to_graph_run

    db = SessionLocal()
    try:
        q = db.query(GraphRunRecord).filter(GraphRunRecord.user_id == user_id)
        if since is not None:
            q = q.filter(GraphRunRecord.created_at >= since)
        if until is not None:
            q = q.filter(GraphRunRecord.created_at <= until)
        records = q.order_by(GraphRunRecord.created_at.asc()).all()
        return [record_to_graph_run(r) for r in records]
    finally:
        db.close()


def enrich_costs_from_langsmith(runs: Iterable[GraphRun]) -> None:
    """Optional: fill missing actual_cost_usd from LangSmith when trace id exists.

    Best-effort — never raises; leaves proxy/zeros when API unavailable.
    """
    client = None
    try:
        from langsmith import Client

        client = Client()
    except Exception:  # noqa: BLE001
        return

    for run in runs:
        if run.actual_cost_usd is not None or not run.langsmith_trace_id:
            continue
        try:
            remote = client.read_run(run.langsmith_trace_id)
        except Exception:  # noqa: BLE001
            continue
        total_tokens = getattr(remote, "total_tokens", None)
        total_cost = getattr(remote, "total_cost", None)
        if total_cost is not None:
            run.actual_cost_usd = float(total_cost)
        if isinstance(getattr(remote, "extra", None), dict):
            usage = remote.extra.get("token_usage") or remote.extra.get("usage_metadata")
            if isinstance(usage, dict):
                run.token_usage = usage
        elif total_tokens is not None and run.token_usage is None:
            run.token_usage = {"unknown": {"total_tokens": int(total_tokens)}}
