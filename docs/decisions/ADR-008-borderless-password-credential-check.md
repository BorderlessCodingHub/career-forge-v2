# ADR-008: Borderless password is credential check only (Career Forge stays IdP)

Linear [CAR-102](https://linear.app/career-forge-v2/issue/CAR-102) asked for “ADR-007”; that number is already [ADR-007](./ADR-007-reference-viewer.md) (Reference viewer). This document is **ADR-008**.

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-09-11 (Founder Engineer) |
| **Date** | 2026-09-12 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | Epic [CAR-101](https://linear.app/career-forge-v2/issue/CAR-101) · first slice [CAR-102](https://linear.app/career-forge-v2/issue/CAR-102) |
| **Amends** | [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) · [ADR-005](./ADR-005-identity-gate-product-entry.md) — issuer remains Career Forge; learner *entry method* may be Borderless email+password when flagged |
| **Does not supersede** | Bearer JWT, `jti` / sign-out (ADR-006), membership `GET members?email=`, paywall 402, Operator OTP |

---

## Context

Career Forge is the JWT issuer (passwordless email OTP, 2026-08-20). Borderless is membership-only. The platform now exposes `POST https://api.borderlesscoding.com/api/auth/signin` (`email` + `password`). Using that token as the product session would reverse the IdP lock (`BorderlessTokenProvider` stays a stub).

---

## Decision

Career Forge **remains the IdP**. Borderless signin is a **server-side credential check**. The backend calls Borderless, **discards** `accessToken`, and mints the existing CF email JWT (`provider=email`, `jti`). The browser never talks to `api.borderlesscoding.com`.

### Locked table (grill 2026-09-11)

| Topic | Decision |
|-------|----------|
| IdP | Career Forge. Do **not** implement `BorderlessTokenProvider.verify` |
| Audience now | Only people with a Borderless platform account |
| OTP / pilot | Learner IdentityGate = password only when `IDENTITY_METHOD=borderless_password`. Learner `/auth/otp/*` + `/auth/pilot/enter` → **410** in that mode (**CAR-105**, not this ADR’s code). Operator OTP unchanged |
| Existing JWTs | OTP/pilot tokens remain valid until exp/sign-out |
| Identity | Lookup `users.email`. Reuse `external_id`. New users: CF `user-{uuid}`, never Borderless `user.id` as `sub` (**CAR-103/104**) |
| `borderless_user_id` | Persist if NULL; mismatch → refuse |
| `emailVerified: false` | Refuse |
| Membership | Still `GET members?email=` after login. `external` still 402 |
| Profile | Copy `name` → placeholder `display_name` only. Ignore `username` / `careerStage` |
| Borderless down | Timeout 2–3s, 1 retry, then 503. No OTP fallback |
| 401 | Generic “Invalid email or password” |
| Rate limit | CF per email + IP **before** proxy |
| Flag | `IDENTITY_METHOD=borderless_password \| email_otp \| pilot_enter` |
| Legacy | Unset `IDENTITY_METHOD` → `IDENTITY_EMAIL_OTP=true` maps `email_otp`, `false` maps `pilot_enter`. **Never** treat `IDENTITY_EMAIL_OTP=false` as password |
| CF route | `POST /auth/signin` — CF session JSON (**CAR-104**) |
| UI | IdentityGate overlay; Platform-like card; signup modal (**CAR-106**) |

### `GET /auth/identity-mode` (this slice)

| Field | Meaning |
|-------|---------|
| `method` | `email_otp` \| `pilot_enter` \| `borderless_password` |
| `email_otp_required` | **Legacy.** `true` unless `method=pilot_enter`. Password mode stays `true` so old IdentityGate does not fall through to pilot enter before CAR-105/106 |

Do not set `IDENTITY_METHOD=borderless_password` in Labs until CAR-105 + CAR-106 are on `main`. Cutover is ops-only: [DEPLOY-LABS-MANUAL §2.5](../DEPLOY-LABS-MANUAL.md) (CAR-107). Repo examples keep `IDENTITY_METHOD` empty.

---

## Consequences

- Proxy + password UI + 410 OTP ship in later CAR-101 children.
- Labs freeze (`IDENTITY_EMAIL_OTP=false`, empty `IDENTITY_METHOD`) is unchanged: `pilot_enter`.

## Related

- [V2-PLAN.md](../V2-PLAN.md) decision #1
- Grill 2026-09-11 · UI grill (IdentityGate / signup modal)
