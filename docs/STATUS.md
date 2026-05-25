# STATUS — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [SPRINT-BOARD](./SPRINT-BOARD.md) · [CHECKPOINT](./CHECKPOINT.md) · [AGENTS.md](../AGENTS.md)

Last updated: **2026-05-25** · Last merge: **HAC-30** (Arthur sync — sprint roadmap + agent lifecycle)

---

## Parity matrix

| Area | Status | Notes |
|------|--------|-------|
| Agent harness | ✅ Done | AGENTS.md, rules, hooks, triple gate docs |
| Agent lifecycle + sprint board | ✅ Done | HAC-30 — AGENT-LIFECYCLE, SPRINT-BOARD, parallel-dispatch |
| Claude Design prototype | ⚠️ Partial sync | Artifact mode (HAC-25); pill diagnostic; drift on forge stream |
| UX documentation | ✅ Done | UX-FLOW, SCREEN-INTENT, artifact mode spec |
| Borderless theming (HAC-23) | ✅ Done | BORDERLESS-THEMING, prototype CSS vars |
| Backlog compliance (HAC-26) | ✅ Done | Docs + Linear HAC-5–18 aligned |
| Linear sprint milestones | ✅ Done | Sprint 1–5 milestones + deps (HAC-30) |
| Monorepo apps/web + apps/api | ⬜ Todo | HAC-5 — Arthur sync: Arthur → frontend TS |
| Postgres schema + seed | ⬜ Todo | HAC-6 |
| AI JSON contracts | ⬜ Todo | HAC-7 |
| Identity onboarding + editable diagnosis | ⬜ Todo | HAC-8 |
| Live Roadmap Forge (timeline-only SSE) | ⬜ Todo | HAC-18 — MVP target quinta 2026-05-29 |
| Vertical roadmap UI — artifact mode | ⬜ Todo | HAC-9 |
| Mastery Validation | ⬜ Todo | HAC-10 — pitch focus mock interview |
| Adaptive Planning | ⬜ Todo | HAC-11 |

---

## Current sprint

**Sprint 1 — Foundation** (parallel **[P]**)

| Issue | Title | Owner | State |
|-------|-------|-------|-------|
| HAC-5 [P] | Monorepo + deploy skeleton | Arthur (FE) / shared | Backlog |
| HAC-6 [P] | Skill graph schema + seed | — | Backlog |
| HAC-7 [P] | AI JSON contracts | — | Backlog |
| HAC-30 | Arthur sync — sprint roadmap + lifecycle | Matheus | Done |

**Dispatch:** Launch HAC-5/6/7 in ONE message when HAC-30 merges ([parallel-dispatch](../.cursor/rules/parallel-dispatch.mdc))

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
| UX docs + steady-state reference | ✅ |
| Sprint board + agent lifecycle | ✅ |
| Live forge SSE (timeline-only) | ⬜ |
| Validation interview | ⬜ |
| End-to-end pitch | ⬜ |

---

## Blockers

- Confirmação formal participação Arthur (pendente da call)

---

*Update this file after every merge (end-task workflow).*
