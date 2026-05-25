# STATUS — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [CHECKPOINT](./CHECKPOINT.md) · [AGENTS.md](../AGENTS.md)

Last updated: **2026-05-25** · Last merge: **HAC-26** (backlog compliance audit — docs + Linear scope alignment)

---

## Parity matrix

| Area | Status | Notes |
|------|--------|-------|
| Agent harness | ✅ Done | AGENTS.md, rules, hooks, triple gate docs |
| Claude Design prototype | ⚠️ Partial sync | Artifact mode on `#roadmap` (HAC-25); pill diagnostic; uniform forge nodes; **drift:** split forge during stream, editable diagnosis `#result` |
| UX documentation (HAC-21 + HAC-25) | ✅ Done | UX-FLOW, SCREEN-INTENT, artifact mode, timeline-only forge spec |
| Borderless theming (HAC-23) | ✅ Done | BORDERLESS-THEMING, reference images, prototype CSS vars Phase 1 |
| Prototype server entry (HAC-24) | ✅ Done | `index.html` + legacy redirect; `prototype/README.md` |
| Backlog compliance (HAC-26) | ✅ Done | Docs + Linear HAC-5–18 aligned to Career Forge / HAC-21 UX |
| Monorepo apps/web + apps/api | ⬜ Todo | HAC-5 |
| Postgres schema + seed | ⬜ Todo | HAC-6 |
| AI JSON contracts | ⬜ Todo | HAC-7 |
| Identity onboarding + editable diagnosis | ⬜ Todo | HAC-8 |
| Live Roadmap Forge (timeline-only SSE) | ⬜ Todo | HAC-18 |
| Vertical roadmap UI — artifact mode | ⬜ Todo | HAC-9 |
| Mastery Validation | ⬜ Todo | HAC-10 |
| Adaptive Planning | ⬜ Todo | HAC-11 |

---

## Compliance audit summary (HAC-26)

| Area | Status |
|------|--------|
| Product name **Career Forge** in docs | ✅ |
| Stack Next.js + FastAPI + Postgres + LangGraph + LangSmith | ✅ (HAC-5 title fixed: was Supabase) |
| UX flow Goal → pills → editable diagnosis → forge → reveal → artifact | ✅ docs; ⚠️ prototype partial |
| Borderless theming + artifact steady state | ✅ docs + prototype partial |
| Linear HAC-5–18 scope vs canonical UX | ✅ updated |
| Linear project display name | ⚠️ still "Career OS" slug (rename optional) |
| Implementation (apps/web, apps/api) | ⬜ unchanged — out of audit scope |

---

## Current batch

**Batch 0 — Foundation** (parallel after HAC-19)

| Issue | Title | Owner | State |
|-------|-------|-------|-------|
| HAC-5 | Monorepo + deploy skeleton | — | Backlog |
| HAC-6 | Skill graph schema + seed | — | Backlog |
| HAC-7 | AI JSON contracts | — | Backlog |

**Batch 1 — First wow** (sequential)

HAC-8 → HAC-18 → HAC-9

---

## Demo readiness

| Scene | Ready |
|-------|-------|
| UI prototype (artifact mode + onboarding pills) | ⚠️ |
| UX docs + steady-state reference | ✅ |
| Live forge SSE (timeline-only) | ⬜ |
| Validation interview | ⬜ |
| End-to-end pitch | ⬜ |

---

## Blockers

- None

---

*Update this file after every merge (end-task workflow).*
