# STATUS — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Roadmap:** [ROADMAP.md](./ROADMAP.md) · **Checkpoint:** [CHECKPOINT.md](./CHECKPOINT.md)

Last updated: **2026-07-31** · Last merge: **CAR-24** · prior **CAR-23** · **CAR-8**  
Linear: [Career Forge V2](https://linear.app/career-forge-v2) · F1: [Phase 1 — Infra + cost gate](https://linear.app/career-forge-v2/project/phase-1-infra-cost-gate-7ea0a33e6ef7) · F2: [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3)

**Deploy:** Auto-deploy on `main` (CAR-13). Bake `API_INTERNAL_URL` at frontend build (CAR-19). Forge enqueue via `POST /forge/runs` to avoid App Router page 405 (CAR-20).

---

## v1 (hackathon) — complete

Borderless BASE hackathon motor shipped (diagnosis CTRR → forge SSE → validation → adaptive loop). Historical parity matrix and sprint board live under [archive/](./archive/).

---

## Current phase — F1 Infra + cost gate

| Track | Item | Status |
|-------|------|--------|
| A | CAR-5 Goals + seeds (LLM tracks) | Done |
| A | CAR-6 Cost instrumentation | Done |
| A | CAR-7 Synthetic cost gate + Yuri report | Done — report `docs/reports/2026-07-24-cost-gate.md` · **GO** (R$72.53 projected ≪ R$500) · awaiting Yuri sign-off |
| A | CAR-8 Must-have node drafts | Done — `docs/product/must-haves/` ×4 · Linear comment for Yuri · **awaiting sign-off or silence baseline** |
| B | CAR-9 Labs path `/career-forge` | Done — reverse proxy (not host nginx) |
| B | CAR-21 Labs forge SSE stream | Backlog — broken after path OK |
| — | CAR-13 Re-enable auto-deploy on push to `main` | Done — `push: branches: [main]` restored in deploy.yml |
| — | CAR-19 Bake `API_INTERNAL_URL` into frontend image | Done — Labs `/career-forge/health` rewrite fixed |
| — | CAR-20 `POST /forge/runs` (avoid `/forge` page 405) | Done — Labs verified (API JSON, not Next 405) |

**Cost gate:** run 2026-07-24 · Forge P95 **R$1.10** · Hard stop R$500/mo · Approval ceiling R$700 · **No students until Yuri approves**

---

## Phase 2 backlog (created 2026-07-25)

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| CAR-14 | CTRR prompts + light validation align | [S] | Backlog |
| CAR-15 | Soft gate + lean prune + warnings | [S] | Backlog (blocked by CAR-14) |
| CAR-16 | English-first hard cutover | [P] | Backlog |
| CAR-17 | Must-have forge + ≥70% harness | [S] | Backlog (blocked by CAR-8 sign-off/silence + CAR-15) |
| CAR-18 | 16 golden cases + Yuri spot-check | [S] | Backlog (blocked by CAR-14…17) |

Grill decisions: [V2-PLAN.md](./V2-PLAN.md) § Fase 2. Internal work (CAR-14, CAR-16) can start without waiting on all externals; CAR-17/18 need must-have freeze.

---

## Track — Forge recovery + auth scaffold (∥ F2)

[Project](https://linear.app/career-forge-v2/project/forge-recovery-auth-scaffold-fab4691ea85e) · epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) · [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md)

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| CAR-23 | AuthProvider + anon JWT Bearer middleware | [P] | Done — `career_forge/auth/` + Bearer wire; forge SSE public until CAR-26 |
| CAR-24 | `forge_artifacts` + persist on forge complete | [S] | Done — BIGSERIAL + `public_id` UUID; snapshot on `graph_ready` |
| CAR-25 | List / open + freeze-before-promote | [S] | Backlog (blocked by CAR-24 ✅) |
| CAR-27 | Share + resume tokens + landing Continue | [S] | Backlog (blocked by CAR-25) |
| CAR-26 | Forge SSE stream ticket | [S] | Backlog (blocked by CAR-23 ✅; Labs ↔ CAR-21) |

---

## Parity matrix (v2-relevant)

| Area | Status | Notes |
|------|--------|-------|
| LangGraph motor (diagnosis → forge → validation) | ✅ Keep | Untouched by design (V2-PLAN) |
| AI execution (GraphExecutor / Factory) | ✅ Keep | See engineering/AI-EXECUTION.md |
| Diagnosis CTRR (ADR-001) | ✅ Keep | Recalibrate prompts in F2; soft gate |
| Labs deploy path | ⚠️ Partial | Auto-deploy on `main` (CAR-13); same-origin rewrite (CAR-19/20); path OK via reverse proxy (CAR-9); forge SSE broken (CAR-21) |
| 4 LLM goals + catalog seeds | ✅ Done | CAR-5 — `data/catalog/` ×4 tracks |
| Cost pool + per-user cap | ✅ Done | CAR-6 — CostGuard + usage_monthly + 429 kill-switch |
| F1 synthetic cost gate report | ✅ Done | CAR-7 — 24 forges + samples · GO vs R$500/R$700 |
| English-first | ⬜ F2 | CAR-16 hard cutover |
| Must-have node drafts (4 goals) | ✅ Drafted | CAR-8 — `docs/product/must-haves/`; freeze on Yuri sign-off or silence |
| Soft gate + lean forge | ⬜ F2 | CAR-15 — mean CTRR bar; must-haves + foundation |
| F2 golden cases | ⬜ F2 | CAR-18 — 16 fixtures + Yuri spot-check 4 |
| Auth scaffold (anon JWT Bearer) | ✅ Done | CAR-23 — `AuthProvider` + middleware; F3-ready Borderless swap |
| Forge artifacts (historical snapshots) | ✅ Done | CAR-24 — `forge_artifacts` on `graph_ready`; list/open = CAR-25 |
| Platform auth (`borderless-api`) | ⬜ F3 | CAR-28 — Borderless issuer on same Bearer wire |
| Rebrand + landing `/career-forge` | ⬜ F3 | |
| BASE/PSP pilots | ⬜ F3 | After gate + F2 + auth |

---

## Blockers / externals

| Item | Owner | Status |
|------|-------|--------|
| Labs forge SSE through reverse proxy | Pedro | Open (CAR-21) — path fixed in CAR-9 |
| Org `borderlesscodinghub` access | Pedro / Yuri | Partial OK |

---

## After each CAR merge

1. Update **Last merge** line above
2. Flip the matching ROADMAP checkbox / STATUS row
3. Linear issue → Done (manual — no GitHub↔Linear automation)
