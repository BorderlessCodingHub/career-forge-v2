# ADR-003: Forge recovery + auth scaffold (pre-Borderless)

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-07-30 (Founder Engineer) · **Amend 2026-08-20** (email OTP IdP) · **Partial supersede 2026-08-22:** identity-gate **timing** and free forge → [ADR-005](./ADR-005-identity-gate-product-entry.md) |
| **Date** | 2026-07-30 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | Epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) · project Forge recovery + auth scaffold · parallel to F2 · F3b epic [CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) |
| **Supersedes (partial)** | V2-PLAN Decision #1 timing — auth *scaffold* ships before F3. **Amend 2026-08-20:** Borderless JWT **issuer** abandoned; Career Forge owns passwordless email OTP; Borderless = membership check only |

---

## Context

Forge run id + graph lived in **sessionStorage**. Closing the tab lost access even though Postgres already holds `graph_runs` and user roadmap state. `user_id` anon survives in localStorage, but there is no product surface to list or reopen past forges, and no F3-ready identity contract.

Waiting for `borderless-api` blocks internal/real use recovery. We need a **minimal architecture** that recovers forges now and plugs Borderless later.

---

## Decision

### 1. Product: historical forges + dual deep-links

| Concern | Decision |
|---------|----------|
| Recovery target | **List of forge artifacts** + open roadmap for a chosen forge |
| Deep-link unit | **Per forge run / artifact** → opens **roadmap artifact** (not timeline replay, not full workspace) |
| Token roles | **`share`** (read-only) and **`resume`** (reattach local session to owner `user_id`) |
| Session conflict | **Chooser UI** — no silent merge; auto-assume resume only if local session has no persisted forge |
| Token TTL | `share` until revoke; `resume` **single-use + ~7d TTL** |
| Active roadmap | One active graph per user (`user_skill_nodes`); **open = promote snapshot** |
| Switch safety | **Freeze-before-promote** — snapshot current active into its artifact, then promote chosen snapshot |
| UI | Landing inteligente (**Continue / View all / New forge**) **+** route `/forges` |
| Diagnosis | MVP = forge only; Slice 2 = reusable diagnosis **result** (not mid-flight interview) |

### 2. Auth scaffold (F3-ready wire)

| Concern | Decision |
|---------|----------|
| Provider | `AuthProvider`: `AnonymousLocal` now → **email OTP** in F3b (`provider=email`); Borderless JWT issuer **out** (amend 2026-08-20) |
| HTTP | `Authorization: Bearer <JWT>` for all authenticated REST |
| Anon JWT | App-signed; `sub` = `users.external_id`; claim `provider=anonymous` |
| Email JWT | App-signed after OTP verify; same `sub` contract; claim `provider=email` |
| SSE | Browser `EventSource` cannot set Bearer → **stream ticket**: `POST …/stream-ticket` (Bearer) → `GET …/stream?ticket=` (short TTL) |
| Spoofing | Stop trusting raw `user_id` body/query as sole identity once middleware ships |

### 3. Data model

- New thin table **`forge_artifacts`** (not “list from `graph_runs`”): links `graph_run_id`, goal, title/created_at, **roadmap snapshot**, active pointer, token metadata as needed.
- `graph_runs` remains audit trail.

### 4. Email (Slice 2, designed now)

- Post-forge: always show **resume link (copy)**.
- **Optional email** stored for future delivery; **no SMTP/magic-link now** (Slice 2).
- **Amend 2026-08-20:** F3b verifies email via **OTP** (Career Forge IdP). Send resume = later child issue. Optional CAR-29 store is not proof of ownership.

### 5. Delivery slices

| Slice | Scope |
|-------|--------|
| **MVP** | AuthProvider + JWT · `forge_artifacts` + create on forge complete · `GET /me/forges` · open/promote + freeze · landing Continue · stream ticket · share/resume tokens |
| **Slice 2** | Rich `/forges` UI · email capture · conflict chooser polish · reusable diagnosis profile |
| **Slice 3 / F3b** | **Amend 2026-08-20:** Email OTP IdP + membership soft label + (later) send resume + paywall — **not** Borderless issuer |

**Amend 2026-08-01 (grill):** Epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) closed after MVP + Slice 2. Slice 3 ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)) stays F3.

**Amend 2026-08-08 (F3 grill):** Slice 3 = **F3b** only. [F3a](https://linear.app/career-forge-v2/project/phase-3a-rebrand-landing-pilots-ebc398e30d12) closeable **without** login — pilots E2E on anon scaffold are valid (V2-PLAN F3.7/F3.8).

**Amend 2026-08-20 (auth pivot grill):** F3b abandons Borderless JWT issuer. Career Forge owns passwordless **email OTP** (6-digit). After OTP, call Borderless **membership** API (stub/allowlist until ready) → soft label `base|psp|external`. Anon until 1st forge → mandatory OTP upgrade (promote new email / chooser if exists). No paywall in first slices; target = 1 free forge then Stripe for `external`; BASE/PSP active = entitled. Project: [F3b — Email OTP auth + membership](https://linear.app/career-forge-v2/project/f3b-email-otp-auth-membership-53040eae6cbf). Children: [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) OTP · [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) membership · [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) send resume · [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) paywall.

**Amend 2026-08-22 (identity-gate grill):** Timing + free forge **superseded** by [ADR-005](./ADR-005-identity-gate-product-entry.md) / [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57). Product loop requires Email identity at entry (server-side). Unpaid `external` Paywall before diagnosis (no free forge). Artifacts, share/resume, OTP-as-IdP, Bearer + stream ticket **unchanged**.

### 6. Priority vs F2

- Track runs **in parallel** with F2 (CAR-14…18).
- [CAR-21](https://linear.app/career-forge-v2/issue/CAR-21) blocks **Labs SSE/ticket path only**, not JWT/artifacts/list/promote.

---

## Consequences

### Positive

- Internal users can recover forges without waiting for Borderless.
- Single Bearer contract for F3 swap.
- Share vs resume separates mentor demo from account recovery threat model.

### Negative / risks

- Anon JWT + resume links are **not** strong auth — acceptable pre-pilot, not for public BASE/PSP.
- Clearing browser without saved resume still loses access until email/Borderless (Slice 2/3).
- Freeze/promote adds write path complexity on every switch.

### Out of scope (this ADR)

- Mid-flight diagnosis interview resume
- Timeline SSE replay as product feature
- Magic-link (click) IdP — **OTP codes are in scope for F3b** (amend 2026-08-20); magic **links** remain out
- Borderless JWT issuer / SSO as Career Forge IdP (superseded 2026-08-20)
- Multi-active roadmaps
- Stripe checkout mechanics (CAR-46 shipped; **when** it fires → [ADR-005](./ADR-005-identity-gate-product-entry.md) / CAR-57 — before diagnosis, no free forge)

---

## Related

- [V2-PLAN.md](../V2-PLAN.md) — decision log #1 amended; #13+
- [CHECKPOINT.md](../CHECKPOINT.md)
- [EXECUTION-FLOW.md](../engineering/EXECUTION-FLOW.md)
- Grill session 2026-07-30 · auth pivot grill 2026-08-20 · identity-gate grill 2026-08-22
- [ADR-005](./ADR-005-identity-gate-product-entry.md) — supersedes identity-gate timing + free forge
- [2026-08-20-auth-otp-pivot.md](../reports/2026-08-20-auth-otp-pivot.md)
