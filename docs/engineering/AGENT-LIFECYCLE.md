# Agent lifecycle — Career Forge

> **Navigation:** [AGENTS.md](../../AGENTS.md) · [ROADMAP](../ROADMAP.md) · [SPRINT-BOARD](../SPRINT-BOARD.md) · [AGENT-DELIVERY](../AGENT-DELIVERY.md)

Engineering lifecycle for hackathon agents working on **HAC-XX** issues.

---

## Flow overview

```
Entrada → Planejamento → Implementação → Triple QA → Saída
```

| Phase | Flowchart | Artifacts |
|-------|-----------|-----------|
| Session entry | [lifecycle-session-planning.png](./lifecycle-session-planning.png) | AGENTS.md, ROADMAP, STATUS, CHECKPOINT |
| Planning | same | P/S/B classification, parallel dispatch |
| Implementation + QA + Exit | [lifecycle-implementation-qa-exit.png](./lifecycle-implementation-qa-exit.png) | branch, triple gate, end-task |

---

## 1. Entrada da sessão

**Trigger:** `sessionStart` hook → agent reads context in order:

1. [AGENTS.md](../../AGENTS.md) — index + Task template
2. [docs/ROADMAP.md](../ROADMAP.md) — current sprint / batch
3. [docs/SPRINT-BOARD.md](../SPRINT-BOARD.md) — [P]/[S] classification, parallel groups
4. [docs/STATUS.md](../STATUS.md) — parity matrix, last merge
5. [docs/CHECKPOINT.md](../CHECKPOINT.md) — product north star, demo script

**Rule:** Never start coding before reading all five core docs.

---

## 2. Planejamento

**Rule:** [linear-delivery-workflow](../../.cursor/rules/linear-delivery-workflow.mdc)

Classify each issue in the current batch:

| Class | Meaning | Action |
|-------|---------|--------|
| **P** | Parallel-safe | Launch Task subagent |
| **S** | Sequential | Queue after dependency |
| **B** | Blocker | Resolve first |

**Rule (mandatory):** [parallel-dispatch](../../.cursor/rules/parallel-dispatch.mdc)

When **2+ issues** are class **P** with satisfied dependencies, the parent agent **MUST** launch Task subagents in **ONE message** (parallel). Never serialize parallel-safe work.

Reference: [lifecycle-session-planning.png](./lifecycle-session-planning.png)

---

## 3. Implementação

Per issue:

```bash
git checkout main && git pull origin main
# start-task: Linear → In Progress
git checkout -b HAC-XX-title-slug
```

| Area | Path |
|------|------|
| Frontend | `apps/frontend/src/` — Next.js + TypeScript + Tailwind |
| Backend | `apps/backend/src/career_forge/` — FastAPI + LangGraph + Pydantic |
| Structure reference | [REPO-STRUCTURE.md](./REPO-STRUCTURE.md) |
| Shared contracts | Pydantic models, OpenAPI |

**Discipline:** One issue = one branch = one merge (200–500 LOC target).

---

## 4. Triple QA

Run before merge. Full spec: [AGENT-DELIVERY.md](../AGENT-DELIVERY.md)

| Gate | Skill / rule | Pass |
|------|--------------|------|
| A — Evaluator | [dual-qa-gate skill](../../.cursor/skills/dual-qa-gate/SKILL.md) + [agent-delivery-gate](../../.cursor/rules/agent-delivery-gate.mdc) | `SHIP` |
| B — Playwright | dual-qa-gate (Playwright MCP) | `PASS` |
| C — Agent verify | [agent-verify skill](../../.cursor/skills/agent-verify/SKILL.md) | `VERIFIED` |

```bash
make smoke
make agent-verify   # → VERIFIED
```

**Merge only when:** `SHIP + PASS + VERIFIED`

Reference: [lifecycle-implementation-qa-exit.png](./lifecycle-implementation-qa-exit.png)

---

## 5. Saída

**Rule:** [end-session-smoke](../../.cursor/rules/end-session-smoke.mdc) — run `make smoke` before ending session.

**Hook:** `stop` → remind end-task if issue was in progress.

**Rule:** [end-task-workflow](../../.cursor/rules/end-task-workflow.mdc)

After merge:

1. Linear MCP `save_issue` → **Done** (manual — no GitHub integration)
2. Update [STATUS.md](../STATUS.md) — parity matrix, last merge
3. Update [ROADMAP.md](../ROADMAP.md) — checkbox
4. Merge to `main` and push

---

## 6. Self-critique before merge

Before marking an issue Done, agents MUST run a structural self-critique (HAC-31+):

1. **Duplicate scan** — no parallel `database.py` vs `db/session.py`; no duplicate schema/utils modules
2. **Structure compliance** — tree matches [REPO-STRUCTURE.md](./REPO-STRUCTURE.md)
3. **No orphan files** — new code lives under domain folders (`api/`, `schemas/`, `graphs/`, `components/`, etc.)
4. **No legacy paths** — zero references to `apps/api` or `apps/web`
5. **Smoke green** — `make smoke` passes

Document any intentional deviations in the PR/commit message.

---

## Issue ID convention

All hackathon issues use **`HAC-XX`** prefix (team `hackaton-q1`).

Branch format: `HAC-XX-title-slug` (lowercase, hyphens).

---

## Subagent Task template

```
Repo: HB01-2026_soft-push. Base: origin/main (pull latest).

Read AGENTS.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md.
Scope: single issue HAC-XX only.

Branch: HAC-XX-title-slug
Acceptance: <from Linear get_issue>

Before merge: triple gate — SHIP + PASS + VERIFIED.
After merge: end-task (Linear Done + STATUS + ROADMAP).
Report: merge summary, gate verdicts, blockers.
```

---

*Career Forge · HB01-2026 · Programadores Sem Pátria*
