"""CAR-18 — Pedro scoring pass helper.

Default: refresh coverage math from frozen ``forged_node_ids`` (no OpenAI).
``--live``: run ``roadmap_forge`` via GraphExecutor and rewrite the snapshot.

Usage::

    python -m scripts.golden_run --case rag-engineer__mid
    python -m scripts.golden_run --all
    python -m scripts.golden_run --case rag-engineer__mid --live
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from career_forge.paths import golden_cases_dir  # noqa: E402
from career_forge.services.golden_cases import (  # noqa: E402
    GOALS,
    PERSONAS,
    check_case,
    load_golden_case,
)
from career_forge.services.lean_forge import apply_lean_forge_input  # noqa: E402
from career_forge.services.must_have_coverage import (  # noqa: E402
    coverage_for_goal,
    forged_node_ids,
)
from career_forge.services.soft_gate import soft_gate_cutoff  # noqa: E402


def _case_paths(case: str | None, all_cases: bool) -> list[Path]:
    root = golden_cases_dir()
    if all_cases:
        return [
            root / f"{goal}__{persona}.json"
            for goal in GOALS
            for persona in PERSONAS
        ]
    if not case:
        raise SystemExit("pass --case CASE_ID or --all")
    path = root / f"{case}.json"
    if not path.is_file():
        raise SystemExit(f"missing fixture: {path}")
    return [path]


def _refresh_coverage(payload: dict[str, Any]) -> dict[str, Any]:
    forged = payload["snapshot"]["forged_node_ids"]
    result = coverage_for_goal(payload["goal_id"], forged)
    snapshot = dict(payload["snapshot"])
    snapshot["pre_inject_coverage"] = round(result.coverage, 4)
    out = dict(payload)
    out["snapshot"] = snapshot
    return out


def _extract_graph_ids_from_events(events: list[dict[str, Any]]) -> list[str]:
    for event in reversed(events):
        if event.get("type") != "graph_ready":
            continue
        graph = event.get("graph") or event.get("nodes")
        if isinstance(graph, list) and graph:
            return forged_node_ids(graph)
    return []


async def _live_forge(payload: dict[str, Any]) -> list[str]:
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("--live requires OPENAI_API_KEY")

    from career_forge.ai.executor import GraphExecutor
    from career_forge.ai.run import GraphRun, InMemoryGraphRunStore
    from career_forge.services.cost_guard import CostGuard, InMemoryUsageStore

    diagnosis = payload["diagnosis"]
    forge_input = apply_lean_forge_input(
        {
            "diagnosis": diagnosis,
            "goal_id": payload["goal_id"],
            "motivation": payload.get("blurb") or f"golden {payload['case_id']}",
            "years_xp": "1-3",
            "_cost": {"synthetic_gate": True, "label": f"golden:{payload['case_id']}"},
        },
    )

    store = InMemoryGraphRunStore()
    executor = GraphExecutor(store=store, cost_guard=CostGuard(store=InMemoryUsageStore()))
    run = GraphRun(
        id=str(uuid.uuid4()),
        graph_name="roadmap_forge",
        input=forge_input,
        user_id=f"golden-{payload['case_id']}",
        billable=False,
        exclude_reason="golden-case",
    )
    collected = await executor.execute(run, stream=False)
    from career_forge.ai.run import GraphRunResult

    if not isinstance(collected, GraphRunResult):
        raise SystemExit(f"unexpected executor result type: {type(collected).__name__}")
    ids = _extract_graph_ids_from_events(list(collected.events))
    if not ids:
        raise SystemExit(
            f"live forge produced no graph_ready nodes for {payload['case_id']}",
        )
    return ids


def _write_case(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


async def _run_one(path: Path, *, live: bool) -> None:
    case = load_golden_case(path)
    payload = dict(case.payload)
    if live:
        forged = await _live_forge(payload)
        snapshot = dict(payload["snapshot"])
        snapshot["forged_node_ids"] = forged
        snapshot["source"] = "live-forge"
        snapshot["scored_at"] = datetime.now(UTC).isoformat()
        payload["snapshot"] = snapshot
        payload = _refresh_coverage(payload)
    else:
        payload = _refresh_coverage(payload)

    _write_case(path, payload)
    updated = load_golden_case(path)
    check = check_case(updated, cutoff=soft_gate_cutoff())
    status = "PASS" if check.ok else "FAIL"
    print(f"  {status} {updated.case_id} coverage={payload['snapshot']['pre_inject_coverage']}")
    if not check.ok:
        for err in check.errors:
            print(f"         - {err}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CAR-18 golden-run (Pedro scoring helper)")
    parser.add_argument("--case", help="case_id e.g. rag-engineer__mid")
    parser.add_argument("--all", action="store_true", help="Run all 16 cases")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Call roadmap_forge with OpenAI and rewrite forged_node_ids",
    )
    args = parser.parse_args(argv)

    paths = _case_paths(args.case, args.all)
    print(f"== golden-run (CAR-18) live={args.live} ==")

    async def _runner() -> None:
        for path in paths:
            await _run_one(path, live=args.live)

    asyncio.run(_runner())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
