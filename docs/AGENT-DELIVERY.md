# Agent delivery — triple QA gate

> **Navigation:** [← AGENTS.md](../AGENTS.md) · [STATUS.md](./STATUS.md) · [ROADMAP.md](./ROADMAP.md) · [end-task-workflow](../.cursor/rules/end-task-workflow.mdc)

Every implementation block (Linear issue, merge) must pass **three gates** before merge:

| Gate | Name | How | Pass |
|------|------|-----|------|
| **A** | Code evaluator | Readonly subagent | `SHIP` |
| **B** | Playwright QA | Playwright MCP | `PASS` |
| **C** | Agent verify | `make agent-verify` | `VERIFIED` |

**Merge rule:** `SHIP + PASS + VERIFIED`

**After merge:** follow [end-task-workflow](../.cursor/rules/end-task-workflow.mdc) — manually set Linear to Done.

---

## When to run

| Change | A | B | C |
|--------|---|---|---|
| Implementation PR | ✓ | ✓ | ✓ |
| API/DB only | ✓ | skip if no UI | ✓ |
| Docs-only | skip | skip | skip |
| `.cursor/` behavior | ✓ | if UI refs | optional |

---

## Execution order

1. Implement + tests
2. **Gate A + B in parallel**
3. **Gate C** when stack up (`make smoke`)
4. Merge locally
5. **End-task:** Linear → Done + update STATUS

Report:

```
Triple QA Gate: PASS | BLOCKED
- Evaluator: SHIP | FIX | SPLIT
- Playwright: PASS | FAIL
- Agent verify: VERIFIED | FAILED
```

---

## Gate A — Code evaluator

Readonly subagent with `git diff origin/main...HEAD` + tests.

Checklist: coupling, SRP, Pydantic contracts, meaningful tests, scope = single HAC issue.

Output: `SHIP | FIX | SPLIT`

---

## Gate B — Playwright MCP

Stack running. Verify demo flows with `data-testid` selectors (add as you build).

Career OS smoke paths (extend as UI lands):

1. Goal picker → onboarding
2. Forge timeline renders
3. Graph reveal
4. Validation flow

Also: `pnpm --filter web test:e2e` when present.

---

## Gate C — Agent verify

```bash
make smoke
make agent-verify
```

Extend `scripts/agent-verify.sh` for each new API/DB behavior.

Checks (grow over time): health, diagnosis, forge SSE, validation, skill graph state in Postgres.

---

## Failure recovery

| Result | Action |
|--------|--------|
| FIX/SPLIT | Fix, re-run gates |
| Playwright FAIL | Fix UI, re-run B (+ A if code changed) |
| Agent verify FAILED | Fix API/DB, re-run C |
| Skipped gate | Block merge |

---

*Career OS · HB01-2026*
