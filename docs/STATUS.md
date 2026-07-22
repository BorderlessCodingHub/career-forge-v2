# STATUS — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Roadmap:** [ROADMAP.md](./ROADMAP.md) · **Checkpoint:** [CHECKPOINT.md](./CHECKPOINT.md)

Last updated: **2026-07-22** · Last merge: **CAR-6** ([PR #4](https://github.com/BorderlessCodingHub/career-forge-v2/pull/4) · `3d03659`)  
Linear: [Career Forge V2](https://linear.app/career-forge-v2) · Project: [Phase 1 — Infra + cost gate](https://linear.app/career-forge-v2/project/phase-1-infra-cost-gate-7ea0a33e6ef7)

---

## v1 (hackathon) — complete

Borderless BASE hackathon motor shipped (diagnosis CTRR → forge SSE → validation → adaptive loop). Historical parity matrix and sprint board live under [archive/](./archive/).

---

## Current phase — F1 Infra + cost gate

| Track | Item | Status |
|-------|------|--------|
| A | CAR-5 Goals + seeds (LLM tracks) | Done |
| A | CAR-6 Cost instrumentation | Done |
| A | CAR-7 Synthetic cost gate + Yuri report | Todo (unblocked — CAR-5 ✅ + CAR-6 ✅) |
| A | CAR-8 Must-have node drafts | Todo |
| B | CAR-9 Labs nginx `/career-forge` | Backlog (Brunno / domain) |

**Cost gate:** not run yet · Hard stop R$500/mo · Approval ceiling R$700 · **No students until Yuri approves**

---

## Parity matrix (v2-relevant)

| Area | Status | Notes |
|------|--------|-------|
| LangGraph motor (diagnosis → forge → validation) | ✅ Keep | Untouched by design (V2-PLAN) |
| AI execution (GraphExecutor / Factory) | ✅ Keep | See engineering/AI-EXECUTION.md |
| Diagnosis CTRR (ADR-001) | ✅ Keep | Recalibrate prompts in F2; soft gate |
| Labs deploy path | ⚠️ Partial | App deploy OK; nginx path pending (CAR-9) |
| 4 LLM goals + catalog seeds | ✅ Done | CAR-5 — `data/catalog/` ×4 tracks |
| Cost pool + per-user cap | ✅ Done | CAR-6 — CostGuard + usage_monthly + 429 kill-switch |
| English-first | ⬜ F2 | |
| Platform auth (`borderless-api`) | ⬜ F3 | |
| Rebrand + landing `/career-forge` | ⬜ F3 | |
| BASE/PSP pilots | ⬜ F3 | After gate + F2 + auth |

---

## Blockers / externals

| Item | Owner | Status |
|------|-------|--------|
| nginx path + domain pointing | Brunno | Open (CAR-9) |
| Org `borderlesscodinghub` access | Pedro / Yuri | Partial OK |

---

## After each CAR merge

1. Update **Last merge** line above
2. Flip the matching ROADMAP checkbox / STATUS row
3. Linear issue → Done (manual — no GitHub↔Linear automation)
