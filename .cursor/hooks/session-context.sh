#!/usr/bin/env bash
set +e
read -r _input || true
CONTEXT='Career Forge v2 (Borderless Labs). Read AGENTS.md → V2-PLAN → ROADMAP → STATUS → CHECKPOINT. Diagnosis/onboarding AI: read docs/decisions/ADR-001-adaptive-diagnosis-ctrr.md + docs/product/DIAGNOSIS-INTERVIEW.md. Linear team CAR — status is MANUAL — use end-task-workflow after merge.'
if command -v python3 >/dev/null 2>&1; then
  CONTEXT="$CONTEXT" python3 - <<'PY'
import json, os
print(json.dumps({"additional_context": os.environ["CONTEXT"]}))
PY
  exit 0
fi
escaped="${CONTEXT//\\/\\\\}"
escaped="${escaped//\"/\\\"}"
printf '{"additional_context":"%s"}\n' "$escaped"
