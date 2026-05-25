# ROADMAP — Career Forge

> **Navigation:** [STATUS](./STATUS.md) · [CHECKPOINT](./CHECKPOINT.md) · [Linear project](https://linear.app/hackas-borderless/project/career-os-soft-push-b0fb1f68c110)

Execution order for hackathon week. **One issue = one branch = one merge.**

Branch format: `HAC-XX-title-slug` (git hygiene). Linear status: **manual** via [end-task-workflow](../.cursor/rules/end-task-workflow.mdc).

---

## Batch 0 — Foundation ✅ partial

- [x] **HAC-19** — Engineering lifecycle + agent harness
- [x] **HAC-20** — UI product source of truth docs + sync rule/hook
- [x] **HAC-21** — UX paradigm doc update (editable diagnosis + forge redesign)
- [x] **HAC-22** — Rename product to Career Forge (docs, prototype, harness)
- [x] **HAC-20** — UI product source of truth + sync rule/hook
- [ ] **HAC-5** — Monorepo Next.js + FastAPI + Postgres + deploy
- [ ] **HAC-6** — Skill graph schema + roadmap.json seed
- [ ] **HAC-7** — Pydantic + LangGraph state contracts

**Parallel:** HAC-5, HAC-6, HAC-7 after HAC-19 (no cross-deps)

---

## Batch 1 — First AI wow

- [ ] **HAC-8** — Identity Engine (onboarding diagnóstico + **editable diagnosis** screen)
- [ ] **HAC-18** — Live Roadmap Forge (LangGraph SSE + animation reveal) ⭐
- [ ] **HAC-9** — Vertical roadmap UI (steady state + optional AI sidebar)

**Sequential:** HAC-8 → HAC-18 → HAC-9

> **HAC-21 scope note:** Forge UI is **timeline-only during stream** (no graph preview). Reveal animates into **vertical roadmap.sh-style layout**. HAC-9 owns steady-state roadmap + optional AI sidebar — not legacy skill-graph dashboard. See [UX-FLOW.md](../claude-design-docs/UX-FLOW.md).

---

## Batch 2 — Mastery loop

- [ ] **HAC-10** — AI Mastery Validation
- [ ] **HAC-11** — Adaptive Planning
- [ ] **HAC-12** — Demo mode + seed Ana

**Sequential:** HAC-10 → HAC-11 → HAC-12

---

## Batch 3 — Stretch (P1)

- [ ] **HAC-13** — Contextual Mentor
- [ ] **HAC-14** — Mock Interview Loop
- [ ] **HAC-15** — Relatório mentor

---

## Batch 4 — P2

- [ ] **HAC-16** — CV from Evidence

---

## Subagent prompt template

```
Repo: HB01-2026_soft-push. Read AGENTS.md → ROADMAP → STATUS → CHECKPOINT.
Issue: HAC-XX only. Branch: HAC-XX-slug.
Triple gate before merge. End-task after merge.
```

---

## Linear hygiene

- Start issue: `save_issue` state `In Progress`
- Finish issue: **end-task-workflow** → `Done` + STATUS.md + checkbox here

---

*Source of truth for agents — keep in sync with Linear.*
