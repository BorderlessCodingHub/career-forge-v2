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
| [CAR-5](https://linear.app/career-forge-v2/issue/CAR-5) | Swap goals + minimal catalog seeds (LLM tracks) | [P] |
| [CAR-6](https://linear.app/career-forge-v2/issue/CAR-6) | Cost instrumentation (global pool + per-user cap) | [P] |
| [CAR-8](https://linear.app/career-forge-v2/issue/CAR-8) | Draft must-have nodes (4 LLM goals) | [P] |

### Track A — sequential

| Issue | Title | Class | Blocked by |
|-------|-------|-------|------------|
| [CAR-7](https://linear.app/career-forge-v2/issue/CAR-7) | Synthetic cost gate run + Yuri report | [S] | CAR-5, CAR-6 |

### Track B — external **[B]**

| Issue | Title | Class |
|-------|-------|-------|
| [CAR-9](https://linear.app/career-forge-v2/issue/CAR-9) | Labs nginx path `/career-forge` (Brunno / domain) | [B] |

---

## Phase 2 — Goals LLM + prompts + english-first (placeholders)

**Prerequisite:** F1 cost gate approved; must-haves sign-off (or silence baseline).  
**No real students.** Acceptance: golden cases + ≥70% must-have coverage; soft gate on diagnosis.

- [ ] CTRR prompts/rubrics for BASE/PSP spectrum (4 goals)
- [ ] Soft gate (lean forge + warning below bar)
- [ ] Catalog + prompts enforce must-have nodes
- [ ] English-first UI / prompts / reports
- [ ] 16 golden cases (4 goals × 4 CTRR dims)

Create Linear issues when F1 gate closes.

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
