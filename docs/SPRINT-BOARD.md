# SPRINT BOARD — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [STATUS](./STATUS.md) · [decisions/2026-05-25-sync-arthur](./decisions/2026-05-25-sync-arthur.md) · [Linear project](https://linear.app/hackas-borderless/project/career-forge-soft-push-b0fb1f68c110)

Hackathon week target: **2026-06-01** · Functional MVP: **~2026-05-29 (Thursday)**

Branch format: `HAC-XX-title-slug` · Linear status: **manual** ([end-task-workflow](../.cursor/rules/end-task-workflow.mdc))

---

## Sprint 0 — Harness & prototype ✅

**Goal:** Agent lifecycle, docs, Claude Design prototype aligned to Career Forge UX.

| Issue | Title | Status |
|-------|-------|--------|
| HAC-19 | Engineering lifecycle + agent harness | ✅ Done |
| HAC-20 | UI product source of truth | ✅ Done |
| HAC-21 | UX paradigm (editable diagnosis + forge) | ✅ Done |
| HAC-22 | Rename → Career Forge | ✅ Done |
| HAC-23 | Borderless UI theming | ✅ Done |
| HAC-24 | Prototype onboarding pills + 404 | ✅ Done |
| HAC-25 | Prototype artifact mode | ✅ Done |
| HAC-26 | Backlog compliance audit | ✅ Done |

**Deps:** none (foundation for all sprints)

---

## Sprint 1 — Foundation ✅

**Goal:** Deployable monorepo + skill graph seed + AI contracts.  
**Target:** 2026-05-27  
**Parallel group [P]:** HAC-5, HAC-6, HAC-7 — **done**

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-5** [P] | Monorepo Next.js + FastAPI + Postgres + deploy | P | HAC-19 ✅ | ✅ |
| **HAC-6** [P] | Skill graph schema + roadmap.json seed | P | HAC-19 ✅ | ✅ |
| **HAC-7** [P] | Pydantic + LangGraph state contracts | P | HAC-19 ✅ | ✅ |
| HAC-31 | Professional scaffold restructure | — | HAC-5 | ✅ |
| HAC-32 | AI layer — GraphRun, GraphExecutor, AgentFactory | — | HAC-7 | ✅ |

> **Dispatch rule:** Launch 3 Task subagents in ONE message ([parallel-dispatch](../.cursor/rules/parallel-dispatch.mdc)) — **completed**

**Team note (Arthur sync):** Arthur → frontend TS; backend Python shared.

---

## Sprint 2 — Identity + Forge (core wow) ✅

**Goal:** Editable onboarding diagnosis → Live Roadmap Forge SSE → first live wow.  
**Target:** 2026-05-29 (MVP milestone)

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-8** | Identity Engine — goal, pills, editable diagnosis | S | HAC-5, HAC-6, HAC-7 | ✅ |
| **HAC-18** | Live Roadmap Forge — LangGraph SSE + timeline reveal | S | HAC-8 | ✅ |
| *(HAC-9)* | *(Sprint 3 — steady artifact UI)* | — | HAC-18 | ✅ |

**Sequential chain:** HAC-8 → HAC-18

---

## Sprint 3 — Artifact UI ✅

**Goal:** Vertical roadmap.sh-style roadmap in artifact mode (post-forge steady state).  
**Target:** 2026-05-30

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-9** | Vertical roadmap UI — artifact mode steady state | S | HAC-18 | ✅ |

---

## Sprint 4 — Mastery loop ✅

**Goal:** Validate learning → roadmap reacts → demo mode Ana for 7-min pitch.  
**Target:** 2026-05-31

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-10** | AI Mastery Validation — interview + score | S | HAC-9 | ✅ |
| **HAC-11** | Adaptive Planning — reactive roadmap | S | HAC-10 | ✅ |
| **HAC-12** | Demo mode + seed user Ana | S | HAC-11 | ✅ |

**Sequential chain:** HAC-10 → HAC-11 → HAC-12

---

## Sprint 5 — Stretch P1 ✅

**Goal:** Contextual mentor, mock interview loop, mentor report — parallel where possible.  
**Target:** 2026-06-01

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-13** [P] | Contextual Mentor — chat with memory | P | HAC-12 | ✅ |
| **HAC-14** [P] | Mock Interview Loop — recalibrates roadmap | P | HAC-12 | ✅ |
| **HAC-15** [P] | Report for mentor | P | HAC-10 | ✅ |

> HAC-13/14/15 can run in parallel after Sprint 4 demo core is stable.

---

## Sprint 6 — Adaptive diagnosis interview (P0 post-MVP) ✅

**Goal:** Make Screen 2 fully LLM-driven with CTRR Interviewer/Judge loop and production guardrails.

| Issue | Title | Class | Deps | Status |
|-------|-------|-------|------|--------|
| **HAC-33** | CV ingest MVP | — | HAC-42..44 (parallel path) | ✅ |
| **HAC-42** | CTRR schemas + contracts | S | Sprint 5 complete | ✅ |
| **HAC-43** | `diagnosis_interview` graph | S | HAC-42 | ✅ |
| **HAC-44** | Session API + Postgres | S | HAC-43 | ✅ |
| **HAC-45** | Frontend adaptive diagnosis UI | S | HAC-44 | ✅ |
| **HAC-46** | Guardrails + fallback | S | HAC-45 | ✅ |
| **HAC-47** | Polish + observability harness | S | HAC-46 | ✅ |

**Sequential chain:** HAC-42 → HAC-43 → HAC-44 → HAC-45 → HAC-46 → HAC-47 (HAC-33 parallel support)

---

## Ops hardening (post-MVP) ✅

| Issue | Scope | Status |
|-------|-------|--------|
| **HAC-50** | VPS production deploy hardening (GHCR namespace, CI Dockerfile paths, nginx envsubst safety, curl health check) | ✅ |

## Backlog / Won't do

### P2 (if time)

| Issue | Title |
|-------|-------|
| HAC-16 | CV from Evidence |
| HAC-17 | Claude Design HTML handoff (largely superseded by prototype) |

### Cancelled — Arthur sync 2026-05-25

| Issue | Title | Reason |
|-------|-------|--------|
| HAC-28 | Gamification — streak + levels | Not a product driver |
| HAC-29 | Progress auto-posts | Social feed — out of demo scope |
| HAC-30 | Onboarding hours/day pacing | Defer post-MVP Thursday |

---

## Fit vs No-fit (Arthur sync)

| Feature | Fit? | Sprint / Issue |
|---------|------|----------------|
| Contextual diagnosis by goal | ✅ FIT | HAC-8 |
| Live forge with streaming + research | ✅ FIT | HAC-18 |
| Post-topic mock interview | ✅ FIT | HAC-10, HAC-14 |
| Adaptive roadmap after failure | ✅ FIT | HAC-11 |
| Integrated contextual chat | ✅ FIT | HAC-13 |
| Specialized backend (space tech etc.) | ✅ FIT | HAC-6 seed + HAC-8 |
| Frontend TS (Arthur) + Backend FastAPI | ✅ FIT | HAC-5 |
| MVP Thursday | ✅ FIT | Milestones 1–4 |
| 7-min live demo pitch | ✅ FIT | HAC-12 |
| GitHub-style contribution streak | ❌ NO FIT | HAC-28 |
| Levels: apprentice → global | ❌ NO FIT | HAC-28 |
| Automatic progress posts | ❌ NO FIT | HAC-29 |
| Hours/day in onboarding | ❌ DEFER | HAC-30 |
| Multiple complete roadmaps | ❌ NO FIT | CHECKPOINT |
| Enterprise auth | ❌ NO FIT | CHECKPOINT |

---

## Parallel dispatch quick reference

```
Sprint 1:  [P] HAC-5 + HAC-6 + HAC-7  →  ONE message, 3 subagents
Sprint 2:  [S] HAC-8 → HAC-18
Sprint 3:  [S] HAC-9
Sprint 4:  [S] HAC-10 → HAC-11 → HAC-12
Sprint 5:  [P] HAC-13 + HAC-14 + HAC-15  →  ONE message when deps OK
```

Lifecycle: [engineering/AGENT-LIFECYCLE.md](./engineering/AGENT-LIFECYCLE.md)

---

*Source of truth for sprint planning — sync with Linear milestones.*
