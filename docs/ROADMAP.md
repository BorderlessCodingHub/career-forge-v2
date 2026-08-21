# ROADMAP — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Status:** [STATUS.md](./STATUS.md) · **Linear:** [Career Forge V2](https://linear.app/career-forge-v2) (`CAR`)

Branch format: `CAR-XX-title-slug` (no username prefix).

Classify work as **[P]** parallel · **[S]** sequential · **[B]** blocker. Parallel-safe issues with deps satisfied → launch Task subagents in one message.

---

## Current focus — Phase 3a (Rebrand + landing + pilots)

**Prerequisite:** F2 golden cases + Yuri GO (#1/#2/#3) — **met 2026-08-08**.  
**F3a humans after:** hard caps (P95 bump) + rebrand + marketing `/welcome` — **not** platform login (grill F3.7/F3.8).  
**F3b:** [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) epic — email OTP IdP + Borderless membership (grill 2026-08-20; **not** issuer JWT).

Grill decisions: [V2-PLAN.md](./V2-PLAN.md) § Fase 3 (F3.1–F3.13). Amend 2026-08-13: `/welcome` EN · pt-BR → CAR-37 · motion → CAR-38. Amend 2026-08-14: `/welcome` copy → CAR-39. Amend 2026-08-20: F3b OTP pivot.

**Project:** [Phase 3a — Rebrand + landing + pilots](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12)

### F3a — parallel **[P]**

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-33](https://linear.app/career-forge-v2/issue/CAR-33) | Kill-switch P95 → 1.3639 (env + Labs) | [P] | **Done** — Labs live; repo default synced |
| [CAR-34](https://linear.app/career-forge-v2/issue/CAR-34) | Rebrand tokens + logo SVG + favicon | [P] | **Done** — PR #28 |

### F3a — sequential

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-35](https://linear.app/career-forge-v2/issue/CAR-35) | Marketing `/welcome` (EN) | [S] | **Done** — PR #31 |
| [CAR-37](https://linear.app/career-forge-v2/issue/CAR-37) | pt-BR marketing + chrome | [S] | CAR-35 Done |
| [CAR-38](https://linear.app/career-forge-v2/issue/CAR-38) | `/welcome` motion polish | [S] | **Done** — PR #32 |
| [CAR-39](https://linear.app/career-forge-v2/issue/CAR-39) | `/welcome` marketing copy (outcome hero) | [P] | **Done** — PR #34 |
| [CAR-40](https://linear.app/career-forge-v2/issue/CAR-40) | Marketing `/welcome/plg` (product-led) | [P] | **Done** — PR #35 |
| [CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) | Preview premium landings A/B (static HTML, unlinked) | [P] | **Done** — PR #36 |
| [CAR-36](https://linear.app/career-forge-v2/issue/CAR-36) | 2 BASE/PSP pilots + F3a closeout note | [S] | CAR-35 Done |

**Start order:** CAR-37 → CAR-36. **CAR-33–35 Done** · **CAR-38 Done** · **CAR-39 Done** · **CAR-40 Done** · **CAR-41 Done** · **CAR-34 Done**.

### F3b — email OTP auth + membership **[S]**

**Project:** [F3b — Email OTP auth + membership](https://linear.app/career-forge-v2/project/f3b-email-otp-auth-membership-53040eae6cbf) · ADR-003 amend 2026-08-20 · does **not** block F3a pilots

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic: Email OTP auth + Borderless membership | — | — |
| [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) | Email OTP + post-forge upgrade (promote / chooser) | [S] | **Done** |
| [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) | Membership soft label (stub + Borderless members client) | [S] | CAR-44 Done — **start here** |
| [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) | Send resume link by email | [S] | CAR-44 Done |
| [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) | Entitlement paywall (1 free forge → Stripe for external) | [S] | CAR-44 + CAR-45 · later |

**Ask Yuri:** `GET …/members?email=` → `{ active, program }` + staging token — **not** issuer JWT/JWKS.

---

## Observability — LangSmith cost (cross-cutting)

Grill 2026-08-19 — hybrid Postgres gate + LangSmith analytics. CAR-7 `cost_gate.py` stays synthetic; production rollup → CAR-43.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-42](https://linear.app/career-forge-v2/issue/CAR-42) | LangSmith metadata on StructuredToolClient (PR1) | [P] | **Done** — PR #37 · `ai/tracing.py` · 5 callers tagged |
| [CAR-43](https://linear.app/career-forge-v2/issue/CAR-43) | GraphRun ↔ LangSmith link + cost-report (PR2) | [S] | **Done** — PR #38 · migration `010` · GraphExecutor capture · `./scripts/cost-report` |

**Observability track complete** (CAR-42 + CAR-43). CAR-7 `cost_gate.py` remains the synthetic gate.

---

## Phase 1 (Infra + cost gate) — ✅ Completed

**Gate:** cost report + budget (hard R$500 / approval ≤ R$700) — **Yuri GO 2026-08-08**.

### Track A — unblocked now **[P]**

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-5](https://linear.app/career-forge-v2/issue/CAR-5) | Swap goals + minimal catalog seeds (LLM tracks) | [P] ✅ Done |
| [CAR-6](https://linear.app/career-forge-v2/issue/CAR-6) | Cost instrumentation (global pool + per-user cap) | [P] ✅ Done |
| [CAR-8](https://linear.app/career-forge-v2/issue/CAR-8) | Draft must-have nodes (4 LLM goals) | [P] ✅ Done |

### Track A — sequential

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-7](https://linear.app/career-forge-v2/issue/CAR-7) | Synthetic cost gate run + Yuri report | [S] ✅ Done | Report delivered — **Yuri GO 2026-08-08** |
| [CAR-13](https://linear.app/career-forge-v2/issue/CAR-13) | Re-enable auto-deploy on push to `main` | [S] ✅ Done | Paused in CAR-7; restored `push: branches: [main]` |

### Track B — Labs path / streaming **[B]**

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-9](https://linear.app/career-forge-v2/issue/CAR-9) | Labs path `/career-forge` via reverse proxy | [B] ✅ Done (not host nginx) |
| [CAR-21](https://linear.app/career-forge-v2/issue/CAR-21) | Labs forge SSE stream broken (reverse proxy) | [B] ✅ Done |
| [CAR-30](https://linear.app/career-forge-v2/issue/CAR-30) | Labs roadmap GET HTML (page vs API collision) | [B] ✅ Done |

---

## Track — Forge recovery + auth scaffold (∥ F2) — ✅ epic closed

**Project:** [Forge recovery + auth scaffold](https://linear.app/career-forge-v2/project/forge-recovery-auth-scaffold-fab4691ea85e)  
**ADR:** [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md) · grill 2026-07-30 · close-out grill 2026-08-01  
**Epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) Done** (MVP + Slice 2). Slice 3 deferred. **Next:** F2.

### MVP

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) | Epic: Forge recovery + auth scaffold | — | ✅ Done |
| [CAR-23](https://linear.app/career-forge-v2/issue/CAR-23) | AuthProvider + anon JWT Bearer middleware | [P] ✅ Done | — |
| [CAR-24](https://linear.app/career-forge-v2/issue/CAR-24) | `forge_artifacts` + persist on forge complete | [S] ✅ Done | CAR-23 |
| [CAR-25](https://linear.app/career-forge-v2/issue/CAR-25) | List / open + freeze-before-promote | [S] ✅ Done | CAR-24 |
| [CAR-27](https://linear.app/career-forge-v2/issue/CAR-27) | Share + resume tokens + landing Continue | [S] ✅ Done | CAR-25 |
| [CAR-26](https://linear.app/career-forge-v2/issue/CAR-26) | Forge SSE stream ticket | [S] ✅ Done | CAR-23; Labs SSE CAR-21 Done |

**Start order:** CAR-23 first → CAR-24 → CAR-25 → CAR-27; CAR-26 ∥ after CAR-23.

### Slice 2 / 3

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-29](https://linear.app/career-forge-v2/issue/CAR-29) | Slice 2: `/forges` UI + optional email + diagnosis profile | [S] ✅ Done |
| [CAR-31](https://linear.app/career-forge-v2/issue/CAR-31) | Polish `/forges` list UX — scan & open hierarchy | [P] ✅ Done |
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic F3b: Email OTP + membership (was issuer Slice 3) | [S] → **F3b** — CAR-44 Done; next CAR-45…47 |

---

## Phase 2 — Goals LLM + prompts + english-first — ✅ Completed

**Project:** [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3) **Completed**  
**Prerequisite:** F1 cost GO (Yuri); must-haves frozen for harness/golden acceptance (CAR-8 sign-off or silence baseline).  
**No real students.** Mentor out of scope. Acceptance: golden cases + ≥70% **post-forge** must-have coverage — **met 2026-08-08**.

Grill decisions locked in [V2-PLAN.md](./V2-PLAN.md) § Fase 2 (2026-07-25).

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14) | CTRR prompt/rubric recalibration + light validation align | [S] ✅ Done | — |
| [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15) | Soft gate: global CTRR bar + lean forge prune + warnings | [S] ✅ Done | CAR-14 ✅ |
| [CAR-16](https://linear.app/career-forge-v2/issue/CAR-16) | English-first hard cutover (UI + prompts + reports) | [P] ✅ Done | — (∥ CAR-32) |
| [CAR-32](https://linear.app/career-forge-v2/issue/CAR-32) | Docs: reconcile ADR-001 / V2-PLAN to 5 live profile dims | [P] ✅ Done | — |
| [CAR-17](https://linear.app/career-forge-v2/issue/CAR-17) | Must-have enforcement in forge + ≥70% coverage harness | [S] ✅ Done | CAR-8 silence baseline ✅, CAR-15 ✅ |
| [CAR-18](https://linear.app/career-forge-v2/issue/CAR-18) | 16 golden cases + rubric + Yuri spot-check (F2 QA) | [S] ✅ Done | CAR-14…17 ✅ · Yuri #1+#2+#3 GO 2026-08-08 |

**Start order:** CAR-14 ✅ → CAR-15 ✅; CAR-16 ✅ ∥ CAR-32 ✅ → CAR-17 ✅ → CAR-18 ✅.

---

## Phase 3 — see Current focus (F3a / F3b)

Placeholders replaced 2026-08-08 (grill freeze). Linear: [Phase 3a](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) · CAR-33…36 · F3b CAR-28.

---

## Out of scope (v3+)

SSO beyond platform · NocoDB/Discord · OPS dashboard · Gate-as-a-Service · Stripe · job-RAG in forge · diagnosis hard block · Frame landing · global standalone domain

Hackathon sprint history: [archive/SPRINT-BOARD.md](./archive/SPRINT-BOARD.md)
