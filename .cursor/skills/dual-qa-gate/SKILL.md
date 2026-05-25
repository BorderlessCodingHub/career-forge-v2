---
name: dual-qa-gate
description: Mandatory pre-merge triple gate for Career OS — code evaluator, Playwright MCP, agent verify. Use before every merge.
---

# Triple QA Gate

Canonical: [docs/AGENT-DELIVERY.md](../../docs/AGENT-DELIVERY.md)

After merge: [end-task-workflow](../../.cursor/rules/end-task-workflow.mdc)

## Context

1. AGENTS.md → ROADMAP → STATUS → CHECKPOINT
2. Stack: `make smoke`

## Gate A — Evaluator (readonly)

- `git diff origin/main...HEAD`
- Tests + typecheck
- Scope = single HAC issue

Output: `SHIP | FIX | SPLIT`

## Gate B — Playwright MCP

Verify Career OS flows with `data-testid` (extend as UI ships):

1. Goal picker loads
2. Forge timeline streams (or mock replay)
3. Graph reveal
4. Validation screen

Output: `PASS | FAIL`

## Gate C — Agent verify

```bash
make agent-verify
```

Output: `VERIFIED | FAILED`

## Merge rule

| Evaluator | Playwright | Verify | Action |
|-----------|------------|--------|--------|
| SHIP | PASS | VERIFIED | Merge + end-task |
| else | — | — | Fix, re-run |

Report combined status to user before merge.
