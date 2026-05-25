"""Persist astream_events v2 stream into GraphRun records."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from career_forge.ai.run import GraphRun


def record_raw_event(run: GraphRun, lc_event: dict[str, Any]) -> None:
    run.raw_events.append(lc_event)


def record_normalized_event(run: GraphRun, event: dict[str, Any]) -> None:
    run.normalized_events.append(event)


def finalize_run(
    run: GraphRun,
    *,
    output: dict[str, Any] | None = None,
    error: str | None = None,
) -> None:
    now = datetime.now(UTC)
    run.updated_at = now
    run.completed_at = now
    if error:
        run.status = "failed"
        run.error = error
    else:
        run.status = "completed"
        run.output = output
        if output is None and run.normalized_events:
            last = run.normalized_events[-1]
            if last.get("type") in ("graph_ready", "graph_complete"):
                run.output = last
