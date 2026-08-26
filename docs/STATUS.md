# STATUS — Career Forge v2

> **Plan:** [V2-PLAN.md](./V2-PLAN.md) · **Roadmap:** [ROADMAP.md](./ROADMAP.md) · **Checkpoint:** [CHECKPOINT.md](./CHECKPOINT.md)

Last updated: **2026-08-25** · Last merge: **PR #70** CAR-92 Welcome honesty (`3194a61`) · prior **PR #68** CAR-90 · **PR #67** CAR-89 · **PR #66** CAR-88 · **PR #65** CAR-87 · **PR #64** CAR-86 · Epic **CAR-28** F3b **complete** · Epic **CAR-22** closed  
Linear: [Career Forge V2](https://linear.app/career-forge-v2) · F1: [Phase 1 — Infra + cost gate](https://linear.app/career-forge-v2/project/phase-1-infra-cost-gate-7ea0a33e6ef7) · F2: [Phase 2 — Goals LLM + prompts + english-first](https://linear.app/career-forge-v2/project/phase-2-goals-llm-prompts-english-first-40c6a783a3b3) **Completed** · **F3a:** [Phase 3a — Rebrand + landing + pilots](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) · **F3b:** [Email OTP auth + membership](https://linear.app/career-forge-v2/project/f3b-email-otp-auth-membership-53040eae6cbf) **Completed** · **F3c:** [Operator console spec](https://linear.app/career-forge-v2/issue/CAR-58) **Completed** (CAR-75…80)

**Next eng:** **F3a** — [CAR-36](https://linear.app/career-forge-v2/issue/CAR-36) pilots · [CAR-37](https://linear.app/career-forge-v2/issue/CAR-37) pt-BR · [CAR-93](https://linear.app/career-forge-v2/issue/CAR-93) Welcome pilot quotes.

**Deploy:** Auto-deploy on `main` (CAR-13). **CAR-92 Done** — PR #70 Welcome honesty pass (CAR-91 bar included): BASE·PSP included + External $10–15/mo copy; no scenery modals; Yuri + Pedro mentors; Unsplash testimonials until CAR-93. **CAR-90 Done** — PR #68 Operator pending/liberated embed queue from live evidence + `/reference` live allowlist; sandbox `allow-same-origin` + self-origin guard. **CAR-89 Done** — PR #67 `embed_hosts` + Content desk CRUD + learner `GET /reference/embed-hosts`; run Alembic 019. **CAR-88 Done** — PR #66 Access desk list/add/remove for `billing_pilot_emails` + `pilot list` badges. **CAR-87 Done** — PR #65 `billing_pilot_emails` + operator APIs; run Alembic 018 with legacy env populated, then clear `ENTITLEMENT_BILLING_ALLOWLIST`. **CAR-86 Done** — PR #64 Reference source card (allowlist-only iframe). **CAR-80 Done** — PR #63 F3c docs amend. **CAR-85 Done** — PR #62 in-product Reference viewer (`/reference`). **CAR-79 Done** — PR #61 Content sidecar + desk. **CAR-78 Done** — PR #60 Access card UI. **CAR-77 Done** — PR #59 Access desk writes + audit. **CAR-84 Done** — PR #58 Resend `User-Agent` (Cloudflare 1010). **CAR-83 Done** — PR #57 injects `JWT_SECRET`. **CAR-81 Done** — PR #54 injects mailer env; deploy `git pull --ff-only origin main` before `compose up`. VPS `APP_DIR` must be owned by `VPS_USER` (no `sudo git`). Bake `API_INTERNAL_URL` at frontend build (CAR-19). Forge enqueue via `POST /forge/runs` (CAR-20). Trail fetch via `GET /roadmap/current` to avoid App Router page HTML (CAR-30).

---

## v1 (hackathon) — complete

Borderless BASE hackathon motor shipped (diagnosis CTRR → forge SSE → validation → adaptive loop). Historical parity matrix and sprint board live under [archive/](./archive/).

---

## Phase 1 — Infra + cost gate — ✅ Completed

| Track | Item | Status |
|-------|------|--------|
| A | CAR-5 Goals + seeds (LLM tracks) | Done |
| A | CAR-6 Cost instrumentation | Done |
| A | CAR-7 Synthetic cost gate + Yuri report | Done — F1 Notion **GO** (R$72.53) · F2 re-cost [2026-08-06](./reports/2026-08-06-cost-gate.md) **GO** (R$90.15) · **Yuri ack 2026-08-08** |
| A | CAR-8 Must-have node drafts | Done — `docs/product/must-haves/` ×4 · silence baseline 2026-08-04 · **Yuri OK 2026-08-08** |
| B | CAR-9 Labs path `/career-forge` | Done — reverse proxy (not host nginx) |
| B | CAR-21 Labs forge SSE stream | Done — Labs live timeline stream verified |
| — | CAR-13 Re-enable auto-deploy on push to `main` | Done — `push: branches: [main]` restored in deploy.yml |
| — | CAR-19 Bake `API_INTERNAL_URL` into frontend image | Done — Labs `/career-forge/health` rewrite fixed |
| — | CAR-20 `POST /forge/runs` (avoid `/forge` page 405) | Done — Labs verified (API JSON, not Next 405) |
| — | CAR-30 `GET /roadmap/current` (avoid `/roadmap` page HTML) | Done — same-origin trail JSON, not Next DOCTYPE |

**Cost gate:** F1 2026-07-24 · Forge P95 **R$1.10** · F2 re-cost 2026-08-06 · Forge P95 **R$1.36** · proj. **R$90.15** · Hard stop R$500/mo · Approval ceiling R$700 · **Yuri GO on #1+#2+#3 (2026-08-08)** · F3a: bump kill-switch to **1.3639** + cap/user **2**; humans after caps + rebrand/landing (login = F3b)

---

## Phase 2 backlog (created 2026-07-25)

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| CAR-14 | CTRR prompts + light validation align | [S] | Done — EN prompts + per-goal briefs + `profile_score` + LLM validation keywords |
| CAR-15 | Soft gate + lean prune + warnings | [S] | Done — `SOFT_GATE_CUTOFF=0.50` (CAR-18 retune); was 0.55 provisional |
| CAR-32 | Docs: reconcile ADR-001 / V2-PLAN to 5 live dims | [P] | Done — ADR banners + V2-PLAN F2.8 match 5-dim + `profile_score` |
| CAR-16 | English-first hard cutover | [P] | Done — UI/prompts/catalog/reports EN; PR #18 → `main` |
| CAR-17 | Must-have forge + ≥70% harness | [S] | Done — silence baseline; bias+inject; `make must-have-coverage`; PR #21 → `main` |
| CAR-18 | 16 golden cases + Yuri spot-check | [S] | **Done** — harness PR #22; Pedro 16/16 PASS; Yuri approvals 2026-08-08 (#1 cost F1 · #2 must-haves · #3 re-cost F2) |

Grill decisions: [V2-PLAN.md](./V2-PLAN.md) § Fase 2. Golden docs: [PEDRO-RUNBOOK](./product/golden-cases/PEDRO-RUNBOOK.md) · [RUBRIC](./product/golden-cases/RUBRIC.md).

---

## Track — Forge recovery + auth scaffold (∥ F2) — epic Done

[Project](https://linear.app/career-forge-v2/project/forge-recovery-auth-scaffold-fab4691ea85e) · epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) **Done** (grill 2026-08-01) · [ADR-003](./decisions/ADR-003-forge-recovery-auth-scaffold.md)

MVP + Slice 2 shipped. **F3b auth pivot (grill 2026-08-20):** epic [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) = email OTP IdP + membership soft label — **not** Borderless issuer. **CAR-57 Done** — Email identity at product entry; paywall before diagnosis.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| CAR-22 | Epic: Forge recovery + auth scaffold | — | Done — MVP + Slice 2; F3b → CAR-28 epic |
| CAR-23 | AuthProvider + anon JWT Bearer middleware | [P] | Done — `career_forge/auth/` + Bearer wire |
| CAR-24 | `forge_artifacts` + persist on forge complete | [S] | Done — BIGSERIAL + `public_id` UUID; snapshot on `graph_ready` |
| CAR-25 | List / open + freeze-before-promote | [S] | Done — `GET /me/forges` + `POST …/open` freeze-before-promote |
| CAR-27 | Share + resume tokens + landing Continue | [S] | Done — share/resume tokens + landing Continue + `/forges` MVP |
| CAR-29 | Slice 2: rich `/forges` + email store + diagnosis re-forge | [S] | Done — rename/revoke, resume conflict chooser, `PATCH /me/email`, `GET /me/profile` re-forge |
| CAR-31 | Polish `/forges` list UX — scan & open hierarchy | [P] | Done — Open+Rename visible; share/resume/revoke in ⋯; untitled shows goal_id |
| CAR-26 | Forge SSE stream ticket | [S] | Done — `POST …/stream-ticket` + `GET …/stream?ticket=` |
| CAR-28 | Epic F3b: Email OTP + membership | — | **Done** — CAR-44 + CAR-45 + CAR-46 + CAR-47 + **CAR-57** |

---

## Phase 3a backlog (grill freeze 2026-08-08)

**Project:** [Phase 3a — Rebrand + landing + pilots](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) · Decisions: [V2-PLAN](./V2-PLAN.md) § Fase 3 (F3.1–F3.12)

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-33](https://linear.app/career-forge-v2/issue/CAR-33) | Kill-switch P95 → 1.3639 | [P] | **Done** — Labs `1.3639`; repo `.env.example` + `config.py` default synced |
| [CAR-34](https://linear.app/career-forge-v2/issue/CAR-34) | Rebrand tokens + logo + favicon | [P] | **Done** — PR #28 · `#121212` / `#5316CC` / `#2DEBB1` + BrandMark |
| [CAR-35](https://linear.app/career-forge-v2/issue/CAR-35) | Marketing `/welcome` (EN) | [S] | **Done** — PR #31 · CTA → `/`; pt-BR → CAR-37; motion → CAR-38 |
| [CAR-37](https://linear.app/career-forge-v2/issue/CAR-37) | pt-BR marketing + chrome | [S] | Backlog — after CAR-35 |
| [CAR-38](https://linear.app/career-forge-v2/issue/CAR-38) | `/welcome` motion polish | [S] | **Done** — PR #32 · lean CSS + reduced-motion; does not gate CAR-36 |
| [CAR-39](https://linear.app/career-forge-v2/issue/CAR-39) | `/welcome` marketing copy (outcome hero) | [P] | **Done** — PR #34 · outcome H1 + `Start diagnosis` + `CONTEXT.md`; does not gate CAR-36 |
| [CAR-40](https://linear.app/career-forge-v2/issue/CAR-40) | Marketing `/welcome/plg` (product-led) | [P] | **Done** — PR #35 · first fold pinned; trail/phases/features slide in; not linked from `/welcome`; does not gate CAR-36 |
| [CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) | Preview premium landings A/B | [P] | **Done** — PR #36 · `/welcome/premium-a` + `/welcome/premium-b`; static HTML rewrite; not linked; does not gate CAR-37/36 |
| [CAR-48](https://linear.app/career-forge-v2/issue/CAR-48) | Welcome is Premium B (map) | — | Spec locked via CAR-54 |
| [CAR-54](https://linear.app/career-forge-v2/issue/CAR-54) | Welcome cutover spec lock | — | **Done** — grill 2026-08-22; Linear-only |
| [CAR-55](https://linear.app/career-forge-v2/issue/CAR-55) | Upgrade `apps/frontend` Tailwind 3 → 4 | [S] | **Done** — PR #45 · hand `@theme` path; `@tailwindcss/postcss` |
| [CAR-56](https://linear.app/career-forge-v2/issue/CAR-56) | Welcome cutover: Premium B as `/welcome` | [S] | **Done** — PR #46 · `marketing/welcome/`; premium-b → `/welcome`; A-only bake-off |
| [CAR-53](https://linear.app/career-forge-v2/issue/CAR-53) | Real Welcome proof | — | **Done** — grill 2026-08-25; implementation [CAR-92](https://linear.app/career-forge-v2/issue/CAR-92) PR #70 |
| [CAR-91](https://linear.app/career-forge-v2/issue/CAR-91) | Welcome top bar BASE/PSP included | [P] | **Done** — PR #70 (same as CAR-92) |
| [CAR-92](https://linear.app/career-forge-v2/issue/CAR-92) | Welcome honesty pass | [S] | **Done** — PR #70 · Next `marketing/welcome/` only |
| [CAR-36](https://linear.app/career-forge-v2/issue/CAR-36) | 2 BASE/PSP pilots + F3a closeout note | [S] | **Next** — CAR-57 Done |
| [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) | Epic: Email OTP + membership (F3b) | — | **Done** — CAR-44…47 + **CAR-57** |
| [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) | Email OTP + post-forge upgrade | [S] | **Done** — promote/chooser · gate **location → CAR-57 Done** |
| [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) | Membership soft label + Borderless client | [S] | **Done** — PR #41 · stub allowlist + `BorderlessMembershipClient` · `GET /me/profile` |
| [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) | Send resume by email | [S] | **Done** — PR #43 · `POST …/resume/email` + CTAs |
| [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) | Paywall (Stripe external) | [S] | **Done** — PR #42 · **free forge → CAR-57** |
| [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57) | Identity gate at product entry + paywall before diagnosis | [S] | **Done** — PR #49 · [ADR-005](./decisions/ADR-005-identity-gate-product-entry.md) |
| [CAR-69](https://linear.app/career-forge-v2/issue/CAR-69) | Sign out + JWT jti revocation | [S] | **Done** — PR #50 · [ADR-006](./decisions/ADR-006-sign-out-jti-revocation.md) |
| [CAR-70](https://linear.app/career-forge-v2/issue/CAR-70) | Product chrome brand lockup | [P] | **Done** — PR #51 · `BrandLockup` on setup/artifact/IdentityGate/resume |

**Start order:** CAR-36 pilots · CAR-37 pt-BR · CAR-93 pilot quotes. **CAR-33–35 Done** · **CAR-38 Done** · **CAR-39 Done** · **CAR-40 Done** · **CAR-41 Done** · **CAR-34 Done** · **CAR-54 Done** · **CAR-55 Done** · **CAR-56 Done** · **CAR-57 Done** · **CAR-70 Done** · **CAR-53 Done** · **CAR-91 Done** · **CAR-92 Done.**

---

## F3c — Operator console — ✅ Completed

Spec map [CAR-58](https://linear.app/career-forge-v2/issue/CAR-58) **Done**. Six Feature CARs shipped: identity → shell → (Access writes ∥ Content) → Access UI → docs.

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-75](https://linear.app/career-forge-v2/issue/CAR-75) | Operator identity — OTP, operators table, session cookie | [S] | **Done** — PR #52 · `operators` + `provider=operator` OTP + `cf_operator_session`; learner JWT → 403 on `/operator/*` |
| [CAR-76](https://linear.app/career-forge-v2/issue/CAR-76) | Operator console shell — path, desk tabs, roles | [S] | **Done** — PR #53 · `/operator` shell, desk tabs by grant, role-agnostic seats |
| [CAR-77](https://linear.app/career-forge-v2/issue/CAR-77) | Access desk writes + audit | [S] | **Done** — PR #59 · override + billing writes; Stripe lock; append-only audit |
| [CAR-79](https://linear.app/career-forge-v2/issue/CAR-79) | Content sidecar + desk | [P] | **Done** — PR #61 · annotate 40 catalog ids; `skill_content` sidecar; git body gate |
| [CAR-78](https://linear.app/career-forge-v2/issue/CAR-78) | Access card UI | [S] | **Done** — PR #60 · lookup + Access card + read-only cost strip |
| [CAR-80](https://linear.app/career-forge-v2/issue/CAR-80) | F3c docs — V2-PLAN / ROADMAP / STATUS amend | [S] | **Done** — PR #63 · F3c handoff |
| [CAR-87](https://linear.app/career-forge-v2/issue/CAR-87) | Pilot billing emails — table, gate, API | [S] | **Done** — PR #65 · `billing_pilot_emails`; runtime ignores env |
| [CAR-88](https://linear.app/career-forge-v2/issue/CAR-88) | Access desk UI — pilot email list CRUD | [S] | **Done** — PR #66 · list/add/remove + `pilot list` badge |

### Supporting fixes delivered during F3c

| Issue | Title | Class | Status |
|-------|-------|-------|--------|
| [CAR-81](https://linear.app/career-forge-v2/issue/CAR-81) | Mailer env in compose + git-sync prod compose on deploy | [P] | **Done** — PR #54 · `MAILER_*`/`RESEND_*` injected; VPS `chown` (PR #55 not merged) |
| [CAR-82](https://linear.app/career-forge-v2/issue/CAR-82) | OTP verify 401 with stale access token | [P] | **Done** — PR #56 · always send `external_id`; clear token on 401 |
| [CAR-83](https://linear.app/career-forge-v2/issue/CAR-83) | Inject JWT_SECRET into compose + reject prod default | [P] | **Done** — PR #57 · fail-fast when ENV=production uses the public default |
| [CAR-84](https://linear.app/career-forge-v2/issue/CAR-84) | Resend OTP 500 — Cloudflare 1010 / urllib User-Agent | [P] | **Done** — PR #58 · `User-Agent` + error body on Resend HTTP |

---

## Parity matrix (v2-relevant)

| Area | Status | Notes |
|------|--------|-------|
| LangGraph motor (diagnosis → forge → validation) | ✅ Keep | Untouched by design (V2-PLAN) |
| AI execution (GraphExecutor / Factory) | ✅ Keep | See engineering/AI-EXECUTION.md |
| Diagnosis CTRR (ADR-001) | ✅ Recalibrated | CAR-14 — EN prompts + 5 live dims + per-goal briefs; soft gate next |
| Labs deploy path | ✅ Path + trail + SSE | Auto-deploy on `main` (CAR-13); same-origin rewrite (CAR-19/20/30); path OK (CAR-9); forge SSE OK (CAR-21) |
| 4 LLM goals + catalog seeds | ✅ Done | CAR-5 — `data/catalog/` ×4 tracks |
| Cost pool + per-user cap | ✅ Done | CAR-6 — CostGuard + usage_monthly + 429 kill-switch; F3a bump P95 → 1.3639 |
| LangSmith trace metadata (StructuredToolClient) | ✅ Done | CAR-42 — `ai/tracing.py`; filter by `user_id` / `graph:*` tags; PR #37 |
| LangSmith ↔ GraphRun link + cost-report | ✅ Done | CAR-43 — `langsmith_trace_id` + `actual_cost_usd` + `./scripts/cost-report`; PR #38 |
| Kill-switch P95 = F2 re-cost | ✅ Done | CAR-33 — Labs + `.env.example` + config default **1.3639**; pool R$500; forge cap/user **2** |
| F1 synthetic cost gate report | ✅ Done | CAR-7 — 24 forges + samples · GO vs R$500/R$700 |
| English-first | ✅ Done | CAR-16 — UI + remaining prompts/catalog/reports EN (CAR-14 diagnosis/validation prompts) |
| Must-have node drafts (4 goals) | ✅ Done | CAR-8 + Yuri OK 2026-08-08 |
| Soft gate + lean forge | ✅ Done | CAR-15 + CAR-18 — `SOFT_GATE_CUTOFF=0.50` (midpoint retune) |
| Must-have forge + ≥70% harness | ✅ Done | CAR-17 — bias+inject; `make must-have-coverage` |
| F2 golden cases | ✅ Done | CAR-18 — 16/16 PASS + Yuri approvals 2026-08-08 · Phase 2 closed |
| Auth scaffold (anon JWT Bearer) | ✅ Done | CAR-23 — `AuthProvider` + middleware; F3b = email OTP (not Borderless issuer) |
| Forge SSE stream ticket | ✅ Done | CAR-26 — Bearer mint → `?ticket=` on stream; Labs path CAR-21 Done |
| Forge artifacts (historical snapshots) | ✅ Done | CAR-24 persist + CAR-25 list/open freeze-before-promote |
| Forge recovery (share / resume / Continue) | ✅ Done | CAR-27 — `forge_access_tokens`; landing gate; `/share` + `/resume` deep-links |
| Forge recovery Slice 2 | ✅ Done | CAR-29 — rich `/forges`, conflict chooser, email store, diagnosis re-forge |
| `/forges` list UX polish | ✅ Done | CAR-31 — scan & open hierarchy (Open+Rename; ⋯ overflow) |
| Email OTP IdP + membership (F3b) | ✅ Done | CAR-44…47 + **CAR-57** — OTP; membership; paywall at diagnosis start; resume email |
| Send resume by email | ✅ Done | CAR-47 — PR #43 · OTP-verified `POST /me/forges/{id}/resume/email` · forge/complete + `/forges` CTAs |
| Entitlement paywall (external) | ✅ Done | CAR-57 — 402 on diagnosis start + forge; no free forge ([ADR-005](./decisions/ADR-005-identity-gate-product-entry.md)) |
| Pilot billing emails (DB) | ✅ Done | CAR-87 — PR #65 · `billing_pilot_emails` + append-only audit; gate = Stripe OR `billing_entitled` OR table; env unused at runtime |
| Identity gate at product entry | ✅ Done | CAR-57 — Email identity before product loop; server-side `provider=email` |
| OTP verify with stale Bearer | ✅ Done | CAR-82 — PR #56 · `external_id` always in verify payload; clear token on 401 |
| JWT_SECRET injected in compose | ✅ Done | CAR-83 — PR #57 · both compose files; prod boot rejects the public default |
| Resend OTP through Cloudflare | ✅ Done | CAR-84 — PR #58 · `User-Agent` on Resend HTTP; error body in RuntimeError |
| Sign out (this device) | ✅ Done | CAR-69 — PR #50 · `POST /auth/sign-out` + jti denylist; client wipe + confirm ([ADR-006](./decisions/ADR-006-sign-out-jti-revocation.md)) |
| Operator identity (F3c) | ✅ Done | CAR-75 — PR #52 · `operators` + Operator OTP + `cf_operator_session`; learner JWT 403 on `/operator/*` |
| Operator console shell (F3c) | ✅ Done | CAR-76 — PR #53 · `/operator`; Access/Content tabs by grant; role-agnostic seats |
| Access desk writes + audit (F3c) | ✅ Done | CAR-77 — PR #59 · `operator_membership_label` + `billing_entitled`; Stripe-active lock; `operator_access_audit` |
| Access card UI (F3c) | ✅ Done | CAR-78 — PR #60 · email lookup; membership override; billing; Stripe lock; audit; `GET /operator/access/cost-pool` |
| Pilot billing email list UI | ✅ Done | CAR-88 — PR #66 · Access desk CRUD; `pilot list` badge; delete does not toggle `billing_entitled` |
| Content sidecar + desk (F3c) | ✅ Done | CAR-79 — PR #61 · annotate 40 catalog `skill_id`s; title/URL/`published`; git owns body (ADR-004) |
| F3c docs amend | ✅ Done | CAR-80 — PR #63 · V2-PLAN F3c after identity/paywall; kitchen-sink OPS stays out |
| In-product Reference viewer | ✅ Done | CAR-85 — PR #62 · `/reference?node=&item=`; CAR-86 — PR #64 source card default; CAR-89 — PR #67 operational embed allowlist (`embed_hosts`); CAR-90 — PR #68 desk queue + live learner allowlist + `allow-same-origin` ([ADR-007](./decisions/ADR-007-reference-viewer.md)) |
| Rebrand tokens + logo/favicon | ✅ Done | CAR-34 — `#121212` / `#5316CC` / `#2DEBB1`; `BrandMark` + favicon; PR #29 copies `public/` into standalone (Labs `/brand/*`) |
| Product chrome brand lockup | ✅ Done | CAR-70 — PR #51 · `BrandLockup` on `SetupHeader` + `ArtifactShell`; in-card on IdentityGate/resume; route rules hide duplicate topbar |
| Marketing landing `/welcome` | ✅ Done | CAR-35 — EN `/welcome`; CTA → `/`; no pricing/email; pt-BR → CAR-37 |
| `/welcome` motion polish | ✅ Done | CAR-38 — lean CSS hero stagger + scroll reveal; reduced-motion still; PR #32 |
| `/welcome` marketing copy | ✅ Done | CAR-39 — outcome hero + `Start diagnosis` + roadmap glossary (`CONTEXT.md`); PR #34 |
| Marketing `/welcome/plg` | ✅ Done | CAR-40 — EN product-led exploration; first fold pinned; CTA → `/`; not linked from `/welcome`; PR #35 |
| Preview premium A/B | ✅ Done | CAR-41 — PR #36 · `/welcome/premium-a` + `/welcome/premium-b`; Vite clones, rewrite to static HTML, `noindex`; not the funnel; not linked from `/welcome` |
| Welcome-as-B cutover | ✅ Done | CAR-56 — PR #46 · `/welcome` is Premium B (`marketing/welcome/`); `/welcome/premium-b` → `/welcome`; Vite `b/` frozen |
| Welcome honesty pass | ✅ Done | CAR-92 — PR #70 · CAR-91 bar included; BASE·PSP included + External $10–15/mo; no scenery modals; Yuri + Pedro; Unsplash until CAR-93 |
| BASE/PSP pilots (×2 E2E) | ⬜ F3a | **Next** — CAR-57 Done; Email identity + DB list (CAR-87) + Access UI (CAR-88) |

---

## Blockers / externals

| Item | Owner | Status |
|------|-------|--------|
| Labs forge SSE through reverse proxy | Pedro | Done (CAR-21) |
| Borderless membership API (`GET members?email=`) | Yuri / platform | Stub/allowlist live (CAR-45); HTTP path waits on staging URL + token |
| Stripe live keys (`STRIPE_SECRET_KEY` / webhook / price) | Pedro / product | Optional — paywall ships with `billing_pilot_emails` until keys exist |
| Org `borderlesscodinghub` access | Pedro / Yuri | Partial OK |

---

## After each CAR merge

1. Update **Last merge** line above
2. Flip the matching ROADMAP checkbox / STATUS row
3. Linear issue → Done (manual — no GitHub↔Linear automation)
