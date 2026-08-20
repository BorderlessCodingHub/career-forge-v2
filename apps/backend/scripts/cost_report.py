"""Production cost report CLI (CAR-43) — Postgres GraphRuns × optional LangSmith.

Complements CAR-7 ``cost_gate.py`` (synthetic gate). This script rolls up real
student spend from ``graph_runs``.

Usage (repo root)::

    ./scripts/cost-report.sh --user pedro-123 --since 2026-08-01 --format pretty
    ./scripts/cost-report.sh --user pedro-123 --since 2026-08-01T00:00:00Z --format json
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from career_forge.services.cost_gate_report import DEFAULT_FX_USD_BRL
from career_forge.services.cost_report import (
    build_cost_report,
    enrich_costs_from_langsmith,
    query_graph_runs_for_report,
    render_cost_report_json,
    render_cost_report_pretty,
)


def _parse_when(raw: str | None) -> datetime | None:
    if not raw:
        return None
    text = raw.strip()
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        # date-only → start/end of day handled by caller for until; here midnight UTC
        return datetime.fromisoformat(f"{text}T00:00:00+00:00")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="CAR-43 production cost report from graph_runs")
    p.add_argument("--user", required=True, help="external user_id / student id")
    p.add_argument("--since", default=None, help="ISO date or datetime (inclusive)")
    p.add_argument("--until", default=None, help="ISO date or datetime (inclusive)")
    p.add_argument(
        "--format",
        choices=("pretty", "json"),
        default="pretty",
        help="output format (default: pretty)",
    )
    p.add_argument(
        "--fx",
        type=float,
        default=float(os.getenv("COST_FX_USD_BRL", str(DEFAULT_FX_USD_BRL))),
        help="USD→BRL FX rate",
    )
    p.add_argument(
        "--enrich-langsmith",
        action="store_true",
        default=None,
        help="fill missing actual_cost_usd from LangSmith (default: on when LANGSMITH_API_KEY set)",
    )
    p.add_argument(
        "--no-enrich-langsmith",
        action="store_true",
        help="skip LangSmith enrichment even if API key is set",
    )
    args = p.parse_args(argv)

    since = _parse_when(args.since)
    until = _parse_when(args.until)
    if until is not None and args.until and len(args.until.strip()) == 10:
        until = until.replace(hour=23, minute=59, second=59)

    runs = query_graph_runs_for_report(user_id=args.user, since=since, until=until)
    should_enrich = (
        False
        if args.no_enrich_langsmith
        else True
        if args.enrich_langsmith
        else bool(os.getenv("LANGSMITH_API_KEY", "").strip())
    )
    if should_enrich:
        enrich_costs_from_langsmith(runs)

    report = build_cost_report(
        runs,
        user_id=args.user,
        since=since,
        until=until,
        fx_usd_brl=args.fx,
    )
    if args.format == "json":
        sys.stdout.write(render_cost_report_json(report))
    else:
        sys.stdout.write(render_cost_report_pretty(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
