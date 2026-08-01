# ROADMAP — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Status:** [STATUS.md](./STATUS.md) · **Linear:** [Career Forge V2](https://linear.app/career-forge-v2) (`CAR`)

Branch format: `CAR-XX-title-slug` (no username prefix).

Classify work as **[P]** parallel · **[S]** sequential · **[B]** blocker. Parallel-safe issues with deps satisfied → launch Task subagents in one message.

---

## Current focus — Phase 1 (Infra + cost gate)

**Gate:** cost report + budget (hard R$500 / approval ≤ R$700) approved by Yuri → **no students before that**.

### Track A — unblocked now **[P]**

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-5](https://linear.app/career-forge-v2/issue/CAR-5) | Swap goals + minimal catalog seeds (LLM tracks) | [P] ✅ Done |
| [CAR-6](https://linear.app/career-forge-v2/issue/CAR-6) | Cost instrumentation (global pool + per-user cap) | [P] ✅ Done |
| [CAR-8](https://linear.app/career-forge-v2/issue/CAR-8) | Draft must-have nodes (4 LLM goals) | [P] ✅ Done |

### Track A — sequential

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-7](https://linear.app/career-forge-v2/issue/CAR-7) | Synthetic cost gate run + Yuri report | [S] ✅ Done | Report delivered — Yuri go/no-go pending |
| [CAR-13](https://linear.app/career-forge-v2/issue/CAR-13) | Re-enable auto-deploy on push to `main` | [S] ✅ Done | Paused in CAR-7; restored `push: branches: [main]` |

### Track B — Labs path / streaming **[B]**

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-9](https://linear.app/career-forge-v2/issue/CAR-9) | Labs path `/career-forge` via reverse proxy | [B] ✅ Done (not host nginx) |
| [CAR-21](https://linear.app/career-forge-v2/issue/CAR-21) | Labs forge SSE stream broken (reverse proxy) | [B] |

---

## Track — Forge recovery + auth scaffold (∥ F2)

**Project:** [Forge recovery + auth scaffold](https://linear.app/career-forge-v2/project/forge-recovery-auth-scaffold-fab4691ea85e)  
**ADR:** [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md) · grill 2026-07-30  
**Parallel to F2.** CAR-21 blocks Labs stream-ticket only.

### MVP

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) | Epic: Forge recovery + auth scaffold | — | — |
| [CAR-23](https://linear.app/career-forge-v2/issue/CAR-23) | AuthProvider + anon JWT Bearer middleware | [P] ✅ Done | — |
| [CAR-24](https://linear.app/career-forge-v2/issue/CAR-24) | `forge_artifacts` + persist on forge complete | [S] ✅ Done | CAR-23 |
| [CAR-25](https://linear.app/career-forge-v2/issue/CAR-25) | List / open + freeze-before-promote | [S] ✅ Done | CAR-24 |
| [CAR-27](https://linear.app/career-forge-v2/issue/CAR-27) | Share + resume tokens + landing Continue | [S] | CAR-25 |
| [CAR-26](https://linear.app/career-forge-v2/issue/CAR-26) | Forge SSE stream ticket | [S] In Progress | CAR-23; Labs ↔ CAR-21 |

**Start order:** CAR-23 first → CAR-24 → CAR-25 → CAR-27; CAR-26 ∥ after CAR-23 (Labs ticket after CAR-21).

### Slice 2 / 3

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-29](https://linear.app/career-forge-v2/issue/CAR-29) | Slice 2: `/forges` UI + optional email + diagnosis profile | [S] |
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Slice 3: Borderless issuer + send resume + merge | [S] |

---

## Phase 2 — Goals LLM + prompts + english-first

**Project:** [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3)  
**Prerequisite:** F1 cost GO (Yuri); must-haves frozen for harness/golden acceptance (CAR-8 sign-off or silence baseline).  
**No real students.** Mentor out of scope. Acceptance: golden cases + ≥70% **post-forge** must-have coverage.

Grill decisions locked in [V2-PLAN.md](./V2-PLAN.md) § Fase 2 (2026-07-25).

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-14](https://linear.app/career-forge-v2/issue/CAR-14) | CTRR prompt/rubric recalibration + light validation align | [S] | — |
| [CAR-15](https://linear.app/career-forge-v2/issue/CAR-15) | Soft gate: global CTRR bar + lean forge prune + warnings | [S] | CAR-14 |
| [CAR-16](https://linear.app/career-forge-v2/issue/CAR-16) | English-first hard cutover (UI + prompts + reports) | [P] | — (∥ CAR-14) |
| [CAR-17](https://linear.app/career-forge-v2/issue/CAR-17) | Must-have enforcement in forge + ≥70% coverage harness | [S] | CAR-8 freeze, CAR-15 |
| [CAR-18](https://linear.app/career-forge-v2/issue/CAR-18) | 16 golden cases + rubric + Yuri spot-check (F2 QA) | [S] | CAR-14…17 |

**Start order:** CAR-14 + CAR-16 in parallel when ready → CAR-15 → CAR-17 (after must-have freeze) → CAR-18 last.

---

## Phase 3 — Rebrand + auth platform + landing + pilots (placeholders)

**Prerequisite:** F2 golden cases OK.  
**First humans BASE/PSP only after:** platform auth + hard caps + rebrand/landing.

- [ ] Auth via `borderless-api` (platform)
- [ ] Hard caps (pool R$500 + per-user)
- [ ] Rebrand Borderless + i18n pt-BR
- [ ] Landing Next.js at `/career-forge`
- [ ] 2 BASE/PSP pilots end-to-end

---

## Out of scope (v3+)

SSO beyond platform · NocoDB/Discord · OPS dashboard · Gate-as-a-Service · Stripe · job-RAG in forge · diagnosis hard block · Frame landing · global standalone domain

Hackathon sprint history: [archive/SPRINT-BOARD.md](./archive/SPRINT-BOARD.md)
