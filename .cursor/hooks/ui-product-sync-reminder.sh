#!/usr/bin/env bash
# Stop hook — remind agents to sync claude-design-docs after UI paradigm changes.
set +e

input=$(cat)
loop_count=0
if command -v python3 >/dev/null 2>&1; then
  loop_count=$(printf '%s' "$input" | python3 -c 'import json,sys; print(json.load(sys.stdin).get("loop_count", 0))' 2>/dev/null || echo 0)
fi
if [ "$loop_count" != "0" ]; then
  echo '{}'
  exit 0
fi

# Detect UI-related changes (staged, unstaged, or untracked)
ui_touched=0
if git rev-parse --git-dir >/dev/null 2>&1; then
  ui_files=$(git diff --name-only HEAD 2>/dev/null; git diff --name-only --cached 2>/dev/null; git ls-files --others --exclude-standard 2>/dev/null)
  if printf '%s\n' "$ui_files" | grep -qE '^(apps/frontend/|claude-design-docs/|.*tailwind\.config\.|.*\.css$)'; then
    ui_touched=1
  fi
fi

if [ "$ui_touched" = "1" ]; then
  MSG='UI files changed this session. If layout, tokens, routes, or component patterns shifted: update claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md (Implementation notes) and linked docs per ui-product-sync rule. Invoke skill: ui-product-sync.'
else
  MSG='If you changed UI paradigm (tokens, layout, flows, shared components): sync claude-design-docs/PRODUCT-SOURCE-OF-TRUTH.md per .cursor/rules/ui-product-sync.mdc.'
fi

if command -v python3 >/dev/null 2>&1; then
  MSG="$MSG" python3 - <<'PY'
import json, os
print(json.dumps({"followup_message": os.environ["MSG"]}))
PY
  exit 0
fi

escaped="${MSG//\\/\\\\}"
escaped="${escaped//\"/\\\"}"
printf '{"followup_message":"%s"}\n' "$escaped"
