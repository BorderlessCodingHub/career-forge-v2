# ADR-006: Sign out + JWT jti revocation

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-08-23 |
| **Date** | 2026-08-23 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | [CAR-69](https://linear.app/career-forge-v2/issue/CAR-69) · extends [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) / [ADR-005](./ADR-005-identity-gate-product-entry.md) |
| **Glossary** | [CONTEXT.md](../../CONTEXT.md) — **Sign out** |

---

## Context

Access JWTs are stateless with **90-day TTL** and no server-side escape hatch. Learners on shared browsers, switching accounts, or with a stolen token need **Sign out on this device** without waiting for natural expiry.

Share/resume links and forge stream tickets remain short-lived opaque tokens — out of scope for jti revocation.

---

## Decision

### 1. Product — Sign out ends Email identity on this browser

| Concern | Decision |
|---------|----------|
| Scope | **This device / this browser** — not “logged out of Borderless” |
| UI copy (EN v1) | Button: **Sign out** · confirm: *You will lose in-progress work on this device. Continue?* |
| Flow | optional confirm → `POST /auth/sign-out` → **always** wipe client → redirect `/` → Identity gate |
| Confirm when | `career-forge.diagnosis-session-id` **or** `career-forge.forge-run-id` in sessionStorage |
| Client wipe | Prefix scan `career-forge.` and `career-forge:` in **localStorage + sessionStorage** |
| Button visibility | Email identity active **and** past Identity gate (hidden on OTP screen) |
| Not revoked | Share links, resume links, forge stream tickets |

### 2. Server — jti denylist

| Concern | Decision |
|---------|----------|
| Mint | Add **`jti`** (UUID) to all new anon + email JWTs |
| Cutover | Middleware rejects tokens **without** `jti` → one forced re-OTP on deploy |
| Storage | Postgres `revoked_token_jtis` (`jti` PK, `exp`, `revoked_at`) |
| Verify | decode → require `jti` → denylist check → lazy `DELETE WHERE exp < now()` |
| Sign out | `POST /auth/sign-out` — Bearer required → insert `jti` → **204**; reuse → **401** |
| Scope | **This token only** — no sign-out-everywhere in v1 |
| TTL | Keep `jwt_anon_ttl_days = 90` |

### 3. Client

| Concern | Decision |
|---------|----------|
| API | `signOut()` in `user-session.ts` — API first; wipe regardless of API result |
| Chrome | Shared `SignOutButton` in **ArtifactShell** top bar + `(setup)/layout.tsx` header |

---

## Out of scope (v1)

- Sign out everywhere (`auth_epoch` / nuclear revoke all devices)
- Shorter email JWT TTL
- PT-BR copy (confirm + button)
- Revoking share/resume/stream tickets
- Server-side mid-flight diagnosis resume

---

## Consequences

- Deploy forces one re-OTP for sessions holding pre-jti tokens (acceptable hard cutover).
- Denylist rows expire with JWT `exp` — lazy cleanup keeps table bounded.
- Client wipe is prefix-based; new keys must stay under `career-forge.` or `career-forge:`.

---

## Related

- [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) — Bearer scaffold
- [ADR-005](./ADR-005-identity-gate-product-entry.md) — Identity gate timing
- [CAR-69](https://linear.app/career-forge-v2/issue/CAR-69)
