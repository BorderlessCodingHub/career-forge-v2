# ADR-003: Forge recovery + auth scaffold (pre-Borderless)

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-07-30 (Founder Engineer) |
| **Date** | 2026-07-30 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | Epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) · project Forge recovery + auth scaffold · parallel to F2 |
| **Supersedes (partial)** | V2-PLAN Decision #1 timing — auth *scaffold* ships before F3; Borderless issuer still F3 |

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
| Provider | `AuthProvider`: `AnonymousLocal` now → `BorderlessToken` in F3 |
| HTTP | `Authorization: Bearer <JWT>` for all authenticated REST |
| Anon JWT | App-signed; `sub` = `users.external_id`; claim `provider=anonymous` |
| SSE | Browser `EventSource` cannot set Bearer → **stream ticket**: `POST …/stream-ticket` (Bearer) → `GET …/stream?ticket=` (short TTL) |
| Spoofing | Stop trusting raw `user_id` body/query as sole identity once middleware ships |

### 3. Data model

- New thin table **`forge_artifacts`** (not “list from `graph_runs`”): links `graph_run_id`, goal, title/created_at, **roadmap snapshot**, active pointer, token metadata as needed.
- `graph_runs` remains audit trail.

### 4. Email (Slice 2, designed now)

- Post-forge: always show **resume link (copy)**.
- **Optional email** stored for future delivery; **no SMTP/magic-link now**.
- F3: Borderless verified email + “send resume”.

### 5. Delivery slices

| Slice | Scope |
|-------|--------|
| **MVP** | AuthProvider + JWT · `forge_artifacts` + create on forge complete · `GET /me/forges` · open/promote + freeze · landing Continue · stream ticket · share/resume tokens |
| **Slice 2** | Rich `/forges` UI · email capture · conflict chooser polish · reusable diagnosis profile |
| **Slice 3** | Borderless issuer · email send · account merge |

**Amend 2026-08-01 (grill):** Epic [CAR-22](https://linear.app/career-forge-v2/issue/CAR-22) closed after MVP + Slice 2. Slice 3 ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28)) stays F3 — blocked on `borderless-api` access; **zero implementation** until issuer contract is usable. Next eng: CAR-21 → F2.

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
- Magic-link / local IdP
- Multi-active roadmaps

---

## Related

- [V2-PLAN.md](../V2-PLAN.md) — decision log #1 amended; #13+
- [CHECKPOINT.md](../CHECKPOINT.md)
- [EXECUTION-FLOW.md](../engineering/EXECUTION-FLOW.md)
- Grill session 2026-07-30
