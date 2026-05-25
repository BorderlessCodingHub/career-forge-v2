# STATUS — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [SPRINT-BOARD](./SPRINT-BOARD.md) · [CHECKPOINT](./CHECKPOINT.md) · [AGENTS.md](../AGENTS.md)

Last updated: **2026-05-25** · Last merge: **HAC-10**

---

## Parity matrix

| Area | Status | Notes |
|------|--------|-------|
| Agent harness | ✅ Done | AGENTS.md, rules, hooks, triple gate docs |
| Agent lifecycle + sprint board | ✅ Done | HAC-30 — AGENT-LIFECYCLE, SPRINT-BOARD, parallel-dispatch |
| Professional repo scaffold | ✅ Done | HAC-31 — `apps/backend` + `apps/frontend`, REPO-STRUCTURE.md |
| Claude Design prototype | ⚠️ Partial sync | Artifact mode (HAC-25); pill diagnostic; drift on forge stream |
| UX documentation | ✅ Done | UX-FLOW, SCREEN-INTENT, artifact mode spec |
| Borderless theming (HAC-23) | ✅ Done | BORDERLESS-THEMING, prototype CSS vars, Tailwind tokens in frontend |
| Backlog compliance (HAC-26) | ✅ Done | Docs + Linear HAC-5–18 aligned |
| Linear sprint milestones | ✅ Done | Sprint 1–5 milestones + deps (HAC-30) |
| Monorepo apps/frontend + apps/backend | ✅ Done | HAC-5 + HAC-31 — domain-oriented layers |
| Postgres schema + seed | ✅ Done | HAC-6 — models, Alembic, roadmap.json, seed Ana |
| AI JSON contracts | ✅ Done | HAC-7 — Pydantic schemas + fixtures migrated to `career_forge/schemas/` |
| AI execution layer scaffold | ✅ Done | HAC-32 — `career_forge/ai/`, GraphRun, GraphExecutor, AgentFactory |
| Identity onboarding + editable diagnosis | ✅ Done | HAC-8 — goal picker, pill rounds, POST /diagnosis via GraphExecutor |
| Live Roadmap Forge (timeline-only SSE) | ✅ Done | HAC-18 — forge graph + SSE timeline + reveal |
| Vertical roadmap UI — artifact mode | ✅ Done | HAC-9 — GET /roadmap, vertical spine, node drawer |
| Mastery Validation | ✅ Done | HAC-10 — validation graph, /validate interview UI, score ring |
| Adaptive Planning | ⬜ Todo | HAC-11 — next |

---

## Current sprint

**Sprint 4 — Mastery loop** (sequential **[S]**)

| Issue | Title | Class | State |
|-------|-------|-------|-------|
| **HAC-10** | Mastery Validation | S | **Done** |
| HAC-11 | Adaptive Planning | S | **Next** |
| HAC-12 | Demo mode + seed Ana | S | Todo |

Sprint 3 complete (HAC-9). **Dispatch:** HAC-11 ([EXECUTION-FLOW](./engineering/EXECUTION-FLOW.md)).

---

## Arthur sync decisions (2026-05-25)

| Decision | Status |
|----------|--------|
| MVP funcional ~quinta 2026-05-29 | ✅ Milestones set |
| Pitch 7 min demo ao vivo | ✅ HAC-12 scoped |
| Arthur → frontend TS; backend FastAPI | ✅ HAC-5 updated |
| Parallel Sprint 1 (HAC-5/6/7) | ✅ Labels + rule |
| Won't-do: gamificação, auto-posts, horas/dia | ✅ HAC-27–29 Cancelled |

Full doc: [decisions/2026-05-25-sync-arthur.md](./decisions/2026-05-25-sync-arthur.md)

---

## Demo readiness

| Scene | Ready |
|-------|-------|
| UI prototype (artifact mode + onboarding pills) | ⚠️ |
| Onboarding flow wired to API | ✅ |
| UX docs + steady-state reference | ✅ |
| Sprint board + agent lifecycle | ✅ |
| Professional monorepo scaffold | ✅ |
| Live forge SSE (timeline-only) | ✅ |
| Vertical roadmap steady state | ✅ |
| Mastery validation interview | ✅ |
| End-to-end pitch | ⬜ |

---

## Blockers

- Confirmação formal participação Arthur (pendente da call)

---

*Update this file after every merge (end-task workflow).*
