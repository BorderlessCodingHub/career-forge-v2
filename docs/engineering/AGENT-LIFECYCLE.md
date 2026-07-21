# Agent lifecycle — Career Forge v2

> **Navigation:** [AGENTS.md](../../AGENTS.md) · [V2-PLAN](../V2-PLAN.md) · [ROADMAP](../ROADMAP.md) · [AGENT-DELIVERY](../AGENT-DELIVERY.md)

Engineering lifecycle for agents working on **CAR-XX** issues (Linear team Career Forge V2).

---

## Flow overview

```
Entry → Planning → Implementation → Triple QA → Exit
```

| Phase | Flowchart | Artifacts |
|-------|-----------|-----------|
| Session entry | [lifecycle-session-planning.png](./lifecycle-session-planning.png) | AGENTS.md, V2-PLAN, ROADMAP, STATUS, CHECKPOINT |
| Planning | same | P/S/B classification, parallel dispatch |
| Implementation + QA + Exit | [lifecycle-implementation-qa-exit.png](./lifecycle-implementation-qa-exit.png) | branch, triple gate, end-task |

---

## 1. Session entry

**Trigger:** `sessionStart` hook → agent reads context in order:

1. [AGENTS.md](../../AGENTS.md) — index + Task template
2. [docs/V2-PLAN.md](../V2-PLAN.md) — phases + locked decisions
3. [docs/ROADMAP.md](../ROADMAP.md) — current phase / CAR issues / [P][S][B]
4. [docs/STATUS.md](../STATUS.md) — parity matrix, last merge
5. [docs/CHECKPOINT.md](../CHECKPOINT.md) — product north star, demo script

**Rule:** Never start coding before reading the core docs above.

---

## 2. Planning

**Rule:** [linear-delivery-workflow](../../.cursor/rules/linear-delivery-workflow.mdc)

Classify each issue in the current batch (from ROADMAP / V2-PLAN):

| Class | Meaning | Action |
|-------|---------|--------|
| **P** | Parallel-safe | Launch Task subagent |
| **S** | Sequential | Queue after dependency |
| **B** | Blocker | Resolve first |

**Rule (mandatory):** [parallel-dispatch](../../.cursor/rules/parallel-dispatch.mdc)

When **2+ issues** are class **P** with satisfied dependencies, the parent agent **MUST** launch Task subagents in **ONE message** (parallel). Never serialize parallel-safe work.

Example F1 Track A: CAR-5, CAR-6, CAR-8 are **[P]** after deps satisfied; CAR-7 is **[S]** after CAR-5+CAR-6.

Reference: [lifecycle-session-planning.png](./lifecycle-session-planning.png)

---

## 3. Implementation

Per issue:

```bash
git checkout main && git pull origin main
# start-task: Linear → In Progress
git checkout -b CAR-XX-title-slug
```

| Area | Path |
|------|------|
| Frontend | `apps/frontend/` — Next.js + TypeScript + Tailwind |
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

## 5. Exit

**Rule:** [end-session-smoke](../../.cursor/rules/end-session-smoke.mdc) — run `make smoke` before ending session.

**Hook:** `stop` → remind end-task if issue was in progress.

**Rule:** [end-task-workflow](../../.cursor/rules/end-task-workflow.mdc)

After merge:

1. Linear MCP `save_issue` → **Done** (manual — no GitHub integration)
2. Update [STATUS.md](../STATUS.md) — parity matrix, last merge
3. Update [ROADMAP.md](../ROADMAP.md) — checkbox / issue row
4. Merge to `main` and push

---

## 6. Self-critique before merge

Before marking an issue Done, agents MUST run a structural self-critique:

1. **Duplicate scan** — no parallel `database.py` vs `db/session.py`; no duplicate schema/utils modules
2. **Structure compliance** — tree matches [REPO-STRUCTURE.md](./REPO-STRUCTURE.md)
3. **No orphan files** — new code lives under domain folders (`api/`, `schemas/`, `graphs/`, `components/`, etc.)
4. **No legacy paths** — zero references to `apps/api` or `apps/web`
5. **Smoke green** — `make smoke` passes

Document any intentional deviations in the PR/commit message.

---

## Issue ID convention

v2 issues use **`CAR-XX`** (team Career Forge V2).

Branch format: `CAR-XX-title-slug` (lowercase, hyphens; no username prefix).

---

## Subagent Task template

```
Repo: career-forge-v2. Base: origin/main (pull latest).

Read AGENTS.md → docs/V2-PLAN.md → docs/ROADMAP.md → docs/STATUS.md → docs/CHECKPOINT.md.
Scope: single issue CAR-XX only.

Branch: CAR-XX-title-slug
Acceptance: <from Linear get_issue>

Before merge: triple gate — SHIP + PASS + VERIFIED.
After merge: end-task (Linear Done + STATUS + ROADMAP).
Report: merge summary, gate verdicts, blockers.
```

---

*Career Forge v2 · Borderless Labs*
