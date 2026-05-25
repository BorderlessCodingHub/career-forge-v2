# ROADMAP — Career Forge

> **Navigation:** [SPRINT-BOARD](./SPRINT-BOARD.md) · [STATUS](./STATUS.md) · [CHECKPOINT](./CHECKPOINT.md) · [Linear project — Career Forge](https://linear.app/hackas-borderless/project/career-forge-soft-push-b0fb1f68c110)

Execution order for hackathon week. **One issue = one branch = one merge.**

Branch format: `HAC-XX-title-slug` (git hygiene). Linear status: **manual** via [end-task-workflow](../.cursor/rules/end-task-workflow.mdc).

**MVP target (Arthur sync):** ~2026-05-29 (quinta) · **Pitch:** 7 min demo ao vivo

Full sprint board: [SPRINT-BOARD.md](./SPRINT-BOARD.md) · Agent lifecycle: [engineering/AGENT-LIFECYCLE.md](./engineering/AGENT-LIFECYCLE.md)

---

## Sprint 0 — Harness & prototype ✅

- [x] **HAC-19** — Engineering lifecycle + agent harness
- [x] **HAC-20** — UI product source of truth docs + sync rule/hook
- [x] **HAC-21** — UX paradigm doc update (editable diagnosis + forge redesign)
- [x] **HAC-22** — Rename product to Career Forge (docs, prototype, harness)
- [x] **HAC-23** — Borderless UI theming guidance (docs, references, prototype CSS Phase 1)
- [x] **HAC-24** — Prototype onboarding pills, minimal goal, vertical graph, 404 fix
- [x] **HAC-25** — Prototype artifact mode: steady trail canvas, node drawer, uniform forge nodes
- [x] **HAC-26** — Backlog compliance audit (docs + Linear HAC-5–18 alignment)
- [x] **HAC-30** — Arthur sync — sprint roadmap + agent lifecycle

---

## Sprint 1 — Foundation **[P] parallel**

**Target:** 2026-05-27 · **Dispatch:** [parallel-dispatch](../.cursor/rules/parallel-dispatch.mdc)

- [ ] **HAC-5** [P] — Monorepo Next.js + FastAPI + Postgres + deploy
- [ ] **HAC-6** [P] — Skill graph schema + roadmap.json seed
- [ ] **HAC-7** [P] — Pydantic + LangGraph state contracts

**Parallel:** HAC-5, HAC-6, HAC-7 after HAC-19 (no cross-deps)

---

## Sprint 2 — Identity + Forge (core wow)

**Target:** 2026-05-29 (MVP)

- [ ] **HAC-8** — Identity Engine (onboarding diagnóstico + **editable diagnosis** screen)
- [ ] **HAC-18** — Live Roadmap Forge (LangGraph SSE + animation reveal) ⭐

**Sequential:** HAC-8 → HAC-18

> Forge UI is **timeline-only during stream** (no graph preview). Reveal animates into **vertical roadmap.sh-style layout**. See [UX-FLOW.md](../claude-design-docs/UX-FLOW.md).

---

## Sprint 3 — Artifact UI

**Target:** 2026-05-30

- [ ] **HAC-9** — Vertical roadmap UI (steady state + optional AI sidebar)

**Sequential:** HAC-18 → HAC-9

---

## Sprint 4 — Mastery loop

**Target:** 2026-05-31

- [ ] **HAC-10** — AI Mastery Validation
- [ ] **HAC-11** — Adaptive Planning
- [ ] **HAC-12** — Demo mode + seed Ana

**Sequential:** HAC-10 → HAC-11 → HAC-12

---

## Sprint 5 — Stretch P1 **[P] where possible**

**Target:** 2026-06-01

- [ ] **HAC-13** [P] — Contextual Mentor
- [ ] **HAC-14** [P] — Mock Interview Loop
- [ ] **HAC-15** [P] — Relatório mentor

**Parallel:** HAC-13, HAC-14, HAC-15 after HAC-12 (HAC-15 also needs HAC-10)

---

## Backlog / Won't do

| Issue | Title | Status |
|-------|-------|--------|
| HAC-16 | CV from Evidence (P2) | Backlog |
| HAC-17 | Claude Design HTML handoff | Backlog |
| HAC-28 | Gamificação streak + níveis | Cancelled |
| HAC-29 | Auto-posts de progresso | Cancelled |
| HAC-30 | Onboarding horas/dia pacing | Cancelled |

Decisions: [decisions/2026-05-25-sync-arthur.md](./decisions/2026-05-25-sync-arthur.md)

---

## Subagent prompt template

```
Repo: HB01-2026_soft-push. Read AGENTS.md → ROADMAP → SPRINT-BOARD → STATUS → CHECKPOINT.
Issue: HAC-XX only. Branch: HAC-XX-slug.
Triple gate before merge. End-task after merge.
If batch is [P]: parent launches parallel Tasks in ONE message.
```

---

## Linear hygiene

- Start issue: `save_issue` state `In Progress`
- Finish issue: **end-task-workflow** → `Done` + STATUS.md + checkbox here
- Milestones: Sprint 1–5 on Linear project

---

*Source of truth for agents — keep in sync with Linear.*
