# ROADMAP — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Status:** [STATUS.md](./STATUS.md) · **Linear:** [Career Forge V2](https://linear.app/career-forge-v2) (`CAR`)

Branch format: `CAR-XX-title-slug` (no username prefix).

Classify work as **[P]** parallel · **[S]** sequential · **[B]** blocker. Parallel-safe issues with deps satisfied → launch Task subagents in one message.

---

## Current focus — Phase 3a (Rebrand + landing + pilots)

**Prerequisite:** F2 golden cases + Yuri GO (#1/#2/#3) — **met 2026-08-08**.  
**F3a humans after:** hard caps (P95 bump) + rebrand + marketing `/welcome`. **Product loop** requires Email identity ([ADR-005](./decisions/ADR-005-identity-gate-product-entry.md) / [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57)) — not anon scaffold.  
**F3b:** [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) epic — email OTP IdP + Borderless membership (grill 2026-08-20; **not** issuer JWT). Gate **timing** + no free forge = [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57).

Grill decisions: [V2-PLAN.md](./V2-PLAN.md) § Fase 3 (F3.1–F3.13). Amend 2026-08-13: `/welcome` EN · pt-BR → CAR-37 · motion → CAR-38. Amend 2026-08-14: `/welcome` copy → CAR-39. Amend 2026-08-20: F3b OTP pivot.

**Project:** [Phase 3a — Rebrand + landing + pilots](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12)

### F3a — parallel **[P]**

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-33](https://linear.app/career-forge-v2/issue/CAR-33) | Kill-switch P95 → 1.3639 (env + Labs) | [P] | **Done** — Labs live; repo default synced |
| [CAR-34](https://linear.app/career-forge-v2/issue/CAR-34) | Rebrand tokens + logo SVG + favicon | [P] | **Done** — PR #28 |
| [CAR-70](https://linear.app/career-forge-v2/issue/CAR-70) | Product chrome brand lockup (Career Forge + Borderless Labs) | [P] | **Done** — PR #51 |

### F3a — sequential

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-35](https://linear.app/career-forge-v2/issue/CAR-35) | Marketing `/welcome` (EN) | [S] | **Done** — PR #31 |
| [CAR-37](https://linear.app/career-forge-v2/issue/CAR-37) | pt-BR marketing + chrome | [S] | CAR-35 Done |
| [CAR-38](https://linear.app/career-forge-v2/issue/CAR-38) | `/welcome` motion polish | [S] | **Done** — PR #32 |
| [CAR-39](https://linear.app/career-forge-v2/issue/CAR-39) | `/welcome` marketing copy (outcome hero) | [P] | **Done** — PR #34 |
| [CAR-40](https://linear.app/career-forge-v2/issue/CAR-40) | Marketing `/welcome/plg` (product-led) | [P] | **Done** — PR #35 |
| [CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) | Preview premium landings A/B (static HTML, unlinked) | [P] | **Done** — PR #36 |
| [CAR-36](https://linear.app/career-forge-v2/issue/CAR-36) | 2 BASE/PSP pilots + F3a closeout note | [S] | **Next** — CAR-57 Done |

**Start order:** CAR-37 → CAR-36. **CAR-57 Done** · **CAR-33–35 Done** · **CAR-38 Done** · **CAR-39 Done** · **CAR-40 Done** · **CAR-41 Done** · **CAR-34 Done**.

### F3a — Welcome is Premium B ([CAR-48](https://linear.app/career-forge-v2/issue/CAR-48) map)

Spec locked 2026-08-22 ([CAR-54](https://linear.app/career-forge-v2/issue/CAR-54)). Honesty grill [CAR-53](https://linear.app/career-forge-v2/issue/CAR-53) **Done**; implementation [CAR-92](https://linear.app/career-forge-v2/issue/CAR-92) PR #70.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-49](https://linear.app/career-forge-v2/issue/CAR-49) | Tailwind 4 upgrade path on Next 14 | [P] | **Done** — research |
| [CAR-50](https://linear.app/career-forge-v2/issue/CAR-50) | Tailwind 4 upgrade contract | — | **Done** |
| [CAR-51](https://linear.app/career-forge-v2/issue/CAR-51) | Welcome port architecture | — | **Done** |
| [CAR-52](https://linear.app/career-forge-v2/issue/CAR-52) | Vite Premium B source after the port | — | **Done** |
| [CAR-54](https://linear.app/career-forge-v2/issue/CAR-54) | Welcome cutover spec lock | — | **Done** |
| [CAR-55](https://linear.app/career-forge-v2/issue/CAR-55) | Upgrade `apps/frontend` Tailwind 3 → 4 | [S] | **Done** — PR #45 |
| [CAR-56](https://linear.app/career-forge-v2/issue/CAR-56) | Welcome cutover: Premium B as `/welcome` | [S] | **Done** — PR #46 |
| [CAR-53](https://linear.app/career-forge-v2/issue/CAR-53) | Real Welcome proof | — | **Done** — grill 2026-08-25 |
| [CAR-91](https://linear.app/career-forge-v2/issue/CAR-91) | Welcome top bar: BASE/PSP included | [P] | **Done** — PR #70 |
| [CAR-92](https://linear.app/career-forge-v2/issue/CAR-92) | Welcome honesty pass | [S] | **Done** — PR #70 |

**Start order:** CAR-36 pilots · CAR-37 pt-BR · CAR-93 quotes. CAR-53/91/92 **Done**.

### F3b — email OTP auth + membership **[S]**

**Project:** [F3b — Email OTP auth + membership](https://linear.app/career-forge-v2/project/f3b-email-otp-auth-membership-53040eae6cbf) · ADR-003 + [ADR-005](./decisions/ADR-005-identity-gate-product-entry.md) · **F3b complete**

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic: Email OTP auth + Borderless membership | — | **Done** |
| [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) | Email OTP + post-forge upgrade (promote / chooser) | [S] | **Done** (gate **location** superseded by CAR-57) |
| [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) | Membership soft label (stub + Borderless members client) | [S] | **Done** — PR #41 |
| [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) | Send resume link by email | [S] | **Done** — PR #43 |
| [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) | Entitlement paywall (Stripe for external) | [S] | **Done** — PR #42 · **free forge superseded** by CAR-57 |
| [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57) | Identity gate at product entry + paywall before diagnosis | [S] | **Done** — PR #49 |
| [CAR-69](https://linear.app/career-forge-v2/issue/CAR-69) | Sign out + JWT jti revocation | [S] | **Done** — PR #50 · [ADR-006](./decisions/ADR-006-sign-out-jti-revocation.md) |

**Ask Yuri:** `GET …/members?email=` → `{ active, program }` + staging token — **not** issuer JWT/JWKS.

### F3c — Operator console — ✅ Completed

Spec [CAR-58](https://linear.app/career-forge-v2/issue/CAR-58) **Done**. Identity is a second Career Forge OTP (`provider=operator`), not learner OTP + allowlist. Six Feature CARs delivered the sequence identity → shell → (Access writes ∥ Content) → Access UI → docs.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-75](https://linear.app/career-forge-v2/issue/CAR-75) | Operator identity — OTP, operators table, session cookie | [S] | **Done** — PR #52 |
| [CAR-76](https://linear.app/career-forge-v2/issue/CAR-76) | Operator console shell — path, desk tabs, roles | [S] | **Done** — PR #53 |
| [CAR-77](https://linear.app/career-forge-v2/issue/CAR-77) | Access desk writes + audit | [S] | **Done** — PR #59 |
| [CAR-79](https://linear.app/career-forge-v2/issue/CAR-79) | Content sidecar + desk | [P] | **Done** — PR #61 |
| [CAR-78](https://linear.app/career-forge-v2/issue/CAR-78) | Access card UI | [S] | **Done** — PR #60 |
| [CAR-80](https://linear.app/career-forge-v2/issue/CAR-80) | F3c docs amend | [S] | **Done** — PR #63 |
| [CAR-87](https://linear.app/career-forge-v2/issue/CAR-87) | Pilot billing emails — table, gate, API | [S] | **Done** — PR #65 |
| [CAR-88](https://linear.app/career-forge-v2/issue/CAR-88) | Access desk UI — pilot billing email list CRUD | [S] | **Done** — PR #66 |

#### Supporting fixes delivered during F3c

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-81](https://linear.app/career-forge-v2/issue/CAR-81) | Mailer env in compose + deploy git-sync | [P] | **Done** — PR #54 |
| [CAR-82](https://linear.app/career-forge-v2/issue/CAR-82) | OTP verify 401 with stale access token | [P] | **Done** — PR #56 |
| [CAR-83](https://linear.app/career-forge-v2/issue/CAR-83) | Inject JWT_SECRET into compose | [P] | **Done** — PR #57 |
| [CAR-84](https://linear.app/career-forge-v2/issue/CAR-84) | Resend User-Agent (Cloudflare 1010) | [P] | **Done** — PR #58 |

**F3c complete:** CAR-75 → CAR-76 → (CAR-77 ∥ CAR-79) → CAR-78 → CAR-80.

### Product loop — Canonical skill content + Node References

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-94](https://linear.app/career-forge-v2/issue/CAR-94) | Canonical skill content (`/learn/{skill_id}`) | [P] | **This branch** — ADR-004 inventory lookup + deterministic attach |
| [CAR-85](https://linear.app/career-forge-v2/issue/CAR-85) | In-product Reference viewer (`/reference`) | [P] | **Done** — PR #62 · [ADR-007](./decisions/ADR-007-reference-viewer.md) |
| [CAR-86](https://linear.app/career-forge-v2/issue/CAR-86) | Reference source card (blocked iframe fallback) | [P] | **Done** — PR #64 · ADR-007 amend |
| [CAR-89](https://linear.app/career-forge-v2/issue/CAR-89) | Embed allowlist: persist proven hosts (API + learner GET) | [P] | **Done** — PR #67 · ADR-007 amend |
| [CAR-90](https://linear.app/career-forge-v2/issue/CAR-90) | Operator embed queue + `/reference` reads live allowlist | [S] | **Done** — PR #68 · ADR-007 amend |

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
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic F3b: Email OTP + membership (was issuer Slice 3) | [S] → **F3b** — CAR-44 + CAR-45 + CAR-46 + CAR-47 **Done** |

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

## Phase 3 — see Current focus (F3a / F3b / F3c)

Placeholders replaced 2026-08-08 (grill freeze). Linear: [Phase 3a](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) · CAR-33…36 · F3b CAR-28.

---

## Out of scope (v3+)

SSO beyond platform · NocoDB/Discord · generic OPS dashboard beyond the scoped F3c Operator console · Gate-as-a-Service · Stripe actions in the console · job-RAG in forge · diagnosis hard block · Frame landing · global standalone domain

Hackathon sprint history: [archive/SPRINT-BOARD.md](./archive/SPRINT-BOARD.md)
