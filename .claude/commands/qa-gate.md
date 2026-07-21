# Triple QA Gate — Pre-merge verification

Mandatory before any merge to main. Three gates must pass: **SHIP + PASS + VERIFIED**.

## Gate A — Code Evaluator (readonly)

1. Run `git diff main...HEAD` to review all changes
2. Evaluate:
   - Scope: changes address single CAR-XX issue only
   - Structure: follows REPO-STRUCTURE.md conventions
   - No duplicate modules, orphan files, or legacy paths
   - AI layer: no per-graph streaming, uses GraphExecutor only
   - No secrets committed
3. Verdict: **SHIP** (clean) / **FIX** (issues found) / **SPLIT** (too broad)

## Gate B — UI Testing

1. If changes touch frontend (`apps/frontend/`):
   - Verify demo flows work: goal picker → diagnosis → forge → roadmap → validation
   - Check responsive behavior, no broken layouts
   - Test error states
2. If no UI changes: **SKIP** (auto PASS)
3. Verdict: **PASS** / **FAIL**

## Gate C — Agent Verify

1. Run `make agent-verify`
2. Checks: project structure, API `/health`, Postgres connection
3. Verdict: **VERIFIED** / **FAILED**

## Execution order

1. Gates A + B — run in parallel
2. Gate C — run after A+B pass
3. If all pass: proceed to merge
4. If any fail: fix issues and re-run failed gates

## After all gates pass

```
git checkout main && git pull origin main
git merge --no-ff CAR-XX-title-slug
git push origin main
```

Then run `/project:end-task`.

## Skip rules

- API/DB only (no UI): skip Gate B
- Docs-only changes: skip all gates
- .claude/ or .cursor/ config: Gate A only
