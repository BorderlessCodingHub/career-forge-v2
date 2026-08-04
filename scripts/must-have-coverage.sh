#!/usr/bin/env bash
# CAR-17 — must-have coverage harness (deterministic smokes, no OpenAI).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/apps/backend"
export PYTHONPATH="${PYTHONPATH:-}:src"
echo "== must-have coverage (CAR-17) =="
python - <<'PY'
from __future__ import annotations

import json
from pathlib import Path

from career_forge.services.lean_forge import load_must_have_ids
from career_forge.services.must_have_coverage import (
    DEFAULT_COVERAGE_PASS_BAR,
    coverage_for_goal,
)

FIXTURES = Path("tests/fixtures/must_have_coverage")
GOALS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")
failed = 0

print(f"pass_bar={DEFAULT_COVERAGE_PASS_BAR:.0%} (pre-inject, normal forge)")
for goal in GOALS:
    must = load_must_have_ids(goal)
    path = FIXTURES / f"{goal}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    result = coverage_for_goal(goal, payload["forged_node_ids"])
    status = "PASS" if result.passed else "FAIL"
    if not result.passed:
        failed += 1
    print(
        f"  {goal}: {result.coverage:.0%} "
        f"({len(result.hit_ids)}/{len(must)}) [{status}] "
        f"missing={result.missing_ids}"
    )

if failed:
    raise SystemExit(f"must-have coverage FAILED ({failed} goal(s))")
print("MUST-HAVE COVERAGE OK")
PY
