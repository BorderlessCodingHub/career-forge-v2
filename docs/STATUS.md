# STATUS — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Roadmap:** [ROADMAP.md](./ROADMAP.md) · **Checkpoint:** [CHECKPOINT.md](./CHECKPOINT.md)

Last updated: **2026-08-01** · Last merge: **CAR-30** · prior **CAR-29** · **CAR-27** · Epic **CAR-22** closed (Slice 3 deferred)  
Linear: [Career Forge V2](https://linear.app/career-forge-v2) · F1: [Phase 1 — Infra + cost gate](https://linear.app/career-forge-v2/project/phase-1-infra-cost-gate-7ea0a33e6ef7) · F2: [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3)  
**Next eng:** F2 (CAR-14 ∥ CAR-16). **CAR-28** blocked on `borderless-api` — zero prep.

**Deploy:** Auto-deploy on `main` (CAR-13). Bake `API_INTERNAL_URL` at frontend build (CAR-19). Forge enqueue via `POST /forge/runs` (CAR-20). Trail fetch via `GET /roadmap/current` to avoid App Router page HTML (CAR-30).

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
| B | CAR-21 Labs forge SSE stream | Done — Labs live timeline stream verified |
| — | CAR-13 Re-enable auto-deploy on push to `main` | Done — `push: branches: [main]` restored in deploy.yml |
| — | CAR-19 Bake `API_INTERNAL_URL` into frontend image | Done — Labs `/career-forge/health` rewrite fixed |
| — | CAR-20 `POST /forge/runs` (avoid `/forge` page 405) | Done — Labs verified (API JSON, not Next 405) |
| — | CAR-30 `GET /roadmap/current` (avoid `/roadmap` page HTML) | Done — same-origin trail JSON, not Next DOCTYPE |

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

## Track — Forge recovery + auth scaffold (∥ F2) — epic Done

[Project](https://linear.app/career-forge-v2/project/forge-recovery-auth-scaffold-fab4691ea85e) · epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) **Done** (grill 2026-08-01) · [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md)

MVP + Slice 2 shipped. **Slice 3 ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)) deferred to F3** — no `borderless-api` access; zero implementation until issuer contract exists.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| CAR-22 | Epic: Forge recovery + auth scaffold | — | Done — MVP + Slice 2; Slice 3 → F3 |
| CAR-23 | AuthProvider + anon JWT Bearer middleware | [P] | Done — `career_forge/auth/` + Bearer wire |
| CAR-24 | `forge_artifacts` + persist on forge complete | [S] | Done — BIGSERIAL + `public_id` UUID; snapshot on `graph_ready` |
| CAR-25 | List / open + freeze-before-promote | [S] | Done — `GET /me/forges` + `POST …/open` freeze-before-promote |
| CAR-27 | Share + resume tokens + landing Continue | [S] | Done — share/resume tokens + landing Continue + `/forges` MVP |
| CAR-29 | Slice 2: rich `/forges` + email store + diagnosis re-forge | [S] | Done — rename/revoke, resume conflict chooser, `PATCH /me/email`, `GET /me/profile` re-forge |
| CAR-26 | Forge SSE stream ticket | [S] | Done — `POST …/stream-ticket` + `GET …/stream?ticket=` |
| CAR-28 | Slice 3: Borderless issuer + send resume + merge | [S] | Backlog / F3 — blocked on `borderless-api` |

---

## Parity matrix (v2-relevant)

| Area | Status | Notes |
|------|--------|-------|
| LangGraph motor (diagnosis → forge → validation) | ✅ Keep | Untouched by design (V2-PLAN) |
| AI execution (GraphExecutor / Factory) | ✅ Keep | See engineering/AI-EXECUTION.md |
| Diagnosis CTRR (ADR-001) | ✅ Keep | Recalibrate prompts in F2; soft gate |
| Labs deploy path | ✅ Path + trail + SSE | Auto-deploy on `main` (CAR-13); same-origin rewrite (CAR-19/20/30); path OK (CAR-9); forge SSE OK (CAR-21) |
| 4 LLM goals + catalog seeds | ✅ Done | CAR-5 — `data/catalog/` ×4 tracks |
| Cost pool + per-user cap | ✅ Done | CAR-6 — CostGuard + usage_monthly + 429 kill-switch |
| F1 synthetic cost gate report | ✅ Done | CAR-7 — 24 forges + samples · GO vs R$500/R$700 |
| English-first | ⬜ F2 | CAR-16 hard cutover |
| Must-have node drafts (4 goals) | ✅ Drafted | CAR-8 — `docs/product/must-haves/`; freeze on Yuri sign-off or silence |
| Soft gate + lean forge | ⬜ F2 | CAR-15 — mean CTRR bar; must-haves + foundation |
| F2 golden cases | ⬜ F2 | CAR-18 — 16 fixtures + Yuri spot-check 4 |
| Auth scaffold (anon JWT Bearer) | ✅ Done | CAR-23 — `AuthProvider` + middleware; F3-ready Borderless swap |
| Forge SSE stream ticket | ✅ Done | CAR-26 — Bearer mint → `?ticket=` on stream; Labs path CAR-21 Done |
| Forge artifacts (historical snapshots) | ✅ Done | CAR-24 persist + CAR-25 list/open freeze-before-promote |
| Forge recovery (share / resume / Continue) | ✅ Done | CAR-27 — `forge_access_tokens`; landing gate; `/share` + `/resume` deep-links |
| Forge recovery Slice 2 | ✅ Done | CAR-29 — rich `/forges`, conflict chooser, email store, diagnosis re-forge |
| Platform auth (`borderless-api`) | ⬜ F3 | CAR-28 deferred — blocked on issuer access; zero prep (grill 2026-08-01) |
| Rebrand + landing `/career-forge` | ⬜ F3 | |
| BASE/PSP pilots | ⬜ F3 | After gate + F2 + auth |

---

## Blockers / externals

| Item | Owner | Status |
|------|-------|--------|
| Labs forge SSE through reverse proxy | Pedro | Done (CAR-21) |
| `borderless-api` issuer access (CAR-28) | Pedro / platform | Blocked — no access yet; Slice 3 deferred to F3 |
| Org `borderlesscodinghub` access | Pedro / Yuri | Partial OK |

---

## After each CAR merge

1. Update **Last merge** line above
2. Flip the matching ROADMAP checkbox / STATUS row
3. Linear issue → Done (manual — no GitHub↔Linear automation)
