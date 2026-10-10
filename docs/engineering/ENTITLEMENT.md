# Entitlement paywall (CAR-46 · **CAR-57 / CAR-87 / ADR-005** · **CAR-108**)

> **Spec ahead of the code for the lifetime forge (2026-10-08).** [V3-PLAN](../V3-PLAN.md) § Freemium gives `external` one forge, then the subscription. That allowance is [CAR-130](https://linear.app/career-forge-v2/issue/CAR-130) and is not in this table. Password-mode inclusion below is CAR-128.

Identity (email OTP or Borderless password) and membership label (`base|psp|external`) are separate from **billing** in OTP / `pilot_enter` modes. Unpaid `external` learners cannot **start diagnosis** or **start a forge** until they have a Career Forge subscription (or a pilot allowlist). There is **no free forge** until CAR-130. Active BASE/PSP never hit the Stripe gate. An existing Roadmap is not withheld.

A Career Forge password (CAR-129) opens the same email account and does not include the learner. Signup stores the password before a session exists. The session opens when the confirmation link is consumed, and that confirmation does not change the allowance. Inclusion still waits for a Borderless sign-in that reads the profile. When `IDENTITY_METHOD=borderless_password`, a linked learner is included only when the stored profile label is BASE or PSP, or the Operator desk overrides it. `users.borderless_user_id` alone does not include. Each entitlement check reads `GET /api/users/profile` with the encrypted Borderless access token when that token can still be used. A failed read keeps the last successful label and retries on the next check after five minutes. 401/403 keeps that label until the next Borderless password sign-in. Unpaid `external` is paywalled. Active Stripe, `billing_entitled`, and `billing_pilot_emails` still allow.

Cost caps still apply to everyone (`FORGE_CAP_PER_USER_MONTH`).

Canonical product rule: [ADR-005](../decisions/ADR-005-identity-gate-product-entry.md).

---

## Rules

| Caller | Start diagnosis / start forge |
|--------|-------------------------------|
| **Password mode** + profile BASE/PSP, or Operator override `base`/`psp` | Allowed |
| **Password mode** + active Stripe, `billing_entitled`, or pilot email | Allowed |
| **Password mode** otherwise (`borderless_user_id` alone, FREE, missing profile, Career Forge-only) | HTTP **402** `paywall` |
| OTP / `pilot_enter`: `membership_entitled` BASE/PSP | Allowed (no Stripe) |
| OTP / `pilot_enter`: `external` + active Stripe subscription | Allowed |
| OTP / `pilot_enter`: `external` + `users.billing_entitled` operator flag | Allowed |
| OTP / `pilot_enter`: `external` + email in `billing_pilot_emails` | Allowed |
| OTP / `pilot_enter`: `external` otherwise | HTTP **402** `paywall` |
| `demo-ana` / synthetic gate | Excluded (same as CostGuard) |

Also allowed **without** billing: choosing a goal; Continue / validate / report on a Roadmap they already have.

The gate runs on diagnosis **start** and on `POST /forge` / `POST /forge/runs` **before** CostGuard. Product-loop APIs also require Email identity (`provider=email`) — see ADR-005.

---

## Pilot billing emails

`billing_pilot_emails` is the canonical pilot grant list. It can grant access before
the learner completes OTP and gets a `users` row. Adding/removing a pilot email
never writes `users.billing_entitled` and never changes Stripe state.

Every effective list mutation writes `billing_pilot_email_audit`; database triggers
reject audit updates/deletes. API add/delete operations are idempotent.

Migration `018_billing_pilot_emails` performs the one-shot import from the legacy
`ENTITLEMENT_BILLING_ALLOWLIST` and records migration audit rows with no operator.
Runtime entitlement ignores that environment variable after migration. Clear it
after the migration has run; emergency revoke is through the Operator API or direct
SQL.

## Env

| Variable | Purpose |
|----------|---------|
| `STRIPE_SECRET_KEY` | Checkout + retrieve session |
| `STRIPE_WEBHOOK_SECRET` | `Stripe-Signature` HMAC |
| `STRIPE_PRICE_ID` | Subscription price for Checkout |
| `FRONTEND_URL` | Success/cancel URLs (`/forge?billing=success&session_id={CHECKOUT_SESSION_ID}`) |

Stripe is **off** until all three `STRIPE_*` values are set. Database pilot grants
still work.

When `IDENTITY_EMAIL_OTP=false` (CAR-100 freeze) **and** `IDENTITY_METHOD` is empty (ADR-008), the same table is also the
**only product-loop door**: `require_email_provider` rejects sessions whose
`users.email` is not listed. Restore `true` to return to OTP + billing-as-grant.

`IDENTITY_METHOD=borderless_password` (CAR-107 Labs cutover, CAR-128 profile membership): set the method explicitly. Sign-in stores the Borderless access token encrypted and reads the profile. `BORDERLESS_TOKEN_ENCRYPTION_KEY` is required or the process does not start. `MEMBERSHIP_BACKEND=stub`. `BORDERLESS_MEMBERS_*` is **not** a cutover requirement.

---

## HTTP

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/billing/checkout` | Bearer |
| `POST` | `/billing/sync` | Bearer — polling after success_url |
| `POST` | `/billing/portal` | Bearer — fresh Customer Portal session (`payment_method_update`). Not Roadmap presence. No Stripe action in the Operator console. |
| `POST` | `/billing/stripe/webhook` | Public + `Stripe-Signature` |
| `GET` | `/operator/access/pilot-emails` | Operator `access` / `both` |
| `POST` | `/operator/access/pilot-emails` | Operator `access` / `both` |
| `DELETE` | `/operator/access/pilot-emails/{email}` | Operator `access` / `both` |

Webhook events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`, `invoice.paid`.

`past_due` stays entitled. Entering `past_due` sends one Billing email for that failed-charge spell. The link is `{FRONTEND_URL}/billing/card` (Identity gate, then `POST /billing/portal`). A later `invoice.paid`, or a status that leaves `past_due`, closes the spell. Stripe Dashboard failed-payment emails stay off — Career Forge sends this letter. `invoice.payment_failed` does not send mail.

`GET /me/profile` includes `billing_entitled` and `checkout_available`.
`GET /operator/access/learners/{email}` also includes `pilot_email_listed`.
