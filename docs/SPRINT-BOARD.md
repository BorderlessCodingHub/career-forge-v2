# SPRINT BOARD — Career Forge

> **Navigation:** [ROADMAP](./ROADMAP.md) · [STATUS](./STATUS.md) · [decisions/2026-05-25-sync-arthur](./decisions/2026-05-25-sync-arthur.md) · [Linear project](https://linear.app/hackas-borderless/project/career-forge-soft-push-b0fb1f68c110)

Hackathon week target: **2026-06-01** · MVP funcional: **~2026-05-29 (quinta)**

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

## Sprint 1 — Foundation

**Goal:** Monorepo deployável + skill graph seed + contratos IA.  
**Target:** 2026-05-27  
**Parallel group [P]:** HAC-5, HAC-6, HAC-7

| Issue | Title | Class | Deps |
|-------|-------|-------|------|
| **HAC-5** [P] | Monorepo Next.js + FastAPI + Postgres + deploy | P | HAC-19 ✅ |
| **HAC-6** [P] | Skill graph schema + roadmap.json seed | P | HAC-19 ✅ |
| **HAC-7** [P] | Pydantic + LangGraph state contracts | P | HAC-19 ✅ |

> **Dispatch rule:** Launch 3 Task subagents in ONE message ([parallel-dispatch](../.cursor/rules/parallel-dispatch.mdc))

**Team note (Arthur sync):** Arthur → frontend TS; backend Python shared.

---

## Sprint 2 — Identity + Forge (core wow)

**Goal:** Onboarding diagnóstico editável → Live Roadmap Forge SSE → primeiro wow ao vivo.  
**Target:** 2026-05-29 (MVP milestone)

| Issue | Title | Class | Deps |
|-------|-------|-------|------|
| **HAC-8** | Identity Engine — goal, pills, editable diagnosis | S | HAC-5, HAC-6, HAC-7 |
| **HAC-18** | Live Roadmap Forge — LangGraph SSE + timeline reveal | S | HAC-8 |
| *(HAC-9)* | *(Sprint 3 — steady artifact UI)* | — | HAC-18 |

**Sequential chain:** HAC-8 → HAC-18

---

## Sprint 3 — Artifact UI

**Goal:** Trilha vertical estilo roadmap.sh em artifact mode (steady state pós-forge).  
**Target:** 2026-05-30

| Issue | Title | Class | Deps |
|-------|-------|-------|------|
| **HAC-9** | Vertical roadmap UI — artifact mode steady state | S | HAC-18 |

---

## Sprint 4 — Mastery loop

**Goal:** Validar aprendizado → trilha reage → demo mode Ana para pitch 7 min.  
**Target:** 2026-05-31

| Issue | Title | Class | Deps |
|-------|-------|-------|------|
| **HAC-10** | AI Mastery Validation — entrevista + score | S | HAC-9 |
| **HAC-11** | Adaptive Planning — trilha reativa | S | HAC-10 |
| **HAC-12** | Demo mode + seed user Ana | S | HAC-11 |

**Sequential chain:** HAC-10 → HAC-11 → HAC-12

---

## Sprint 5 — Stretch P1

**Goal:** Mentor contextual, mock interview loop, relatório mentor — parallel where possible.  
**Target:** 2026-06-01

| Issue | Title | Class | Deps |
|-------|-------|-------|------|
| **HAC-13** [P] | Contextual Mentor — chat com memória | P | HAC-12 |
| **HAC-14** [P] | Mock Interview Loop — recalibra trilha | P | HAC-12 |
| **HAC-15** [P] | Relatório para mentor | P | HAC-10 |

> HAC-13/14/15 can run in parallel after Sprint 4 demo core is stable.

---

## Backlog / Won't do

### P2 (if time)

| Issue | Title |
|-------|-------|
| HAC-16 | CV from Evidence |
| HAC-17 | Claude Design HTML handoff (largely superseded by prototype) |

### Cancelled — Arthur sync 2026-05-25

| Issue | Title | Reason |
|-------|-------|--------|
| HAC-28 | Gamificação — streak + níveis | Não é motor do produto |
| HAC-29 | Auto-posts de progresso | Social feed — fora do demo |
| HAC-30 | Onboarding horas/dia pacing | Defer pós-MVP quinta |

---

## Fit vs No-fit (Arthur sync)

| Feature | Fit? | Sprint / Issue |
|---------|------|----------------|
| Diagnóstico contextual por objetivo | ✅ FIT | HAC-8 |
| Live forge com streaming + pesquisa | ✅ FIT | HAC-18 |
| Mock interview pós-tópico | ✅ FIT | HAC-10, HAC-14 |
| Trilha adaptativa pós-falha | ✅ FIT | HAC-11 |
| Chat integrado contextual | ✅ FIT | HAC-13 |
| Backend especializado (space tech etc.) | ✅ FIT | HAC-6 seed + HAC-8 |
| Frontend TS (Arthur) + Backend FastAPI | ✅ FIT | HAC-5 |
| MVP quinta-feira | ✅ FIT | Milestones 1–4 |
| Pitch 7 min demo ao vivo | ✅ FIT | HAC-12 |
| GitHub-style contribution streak | ❌ NO FIT | HAC-28 |
| Níveis aprendiz → global | ❌ NO FIT | HAC-28 |
| Posts automáticos de progresso | ❌ NO FIT | HAC-29 |
| Horas/dia no onboarding | ❌ DEFER | HAC-30 |
| Múltiplas trilhas completas | ❌ NO FIT | CHECKPOINT |
| Auth enterprise | ❌ NO FIT | CHECKPOINT |

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
