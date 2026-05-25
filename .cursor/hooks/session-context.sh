#!/usr/bin/env bash
set +e
read -r _input || true
CONTEXT='Career Forge hackathon repo. Read AGENTS.md → ROADMAP → SPRINT-BOARD → STATUS → CHECKPOINT. Linear status is MANUAL — use end-task-workflow after merge.'
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
