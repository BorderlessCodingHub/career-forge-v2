# Entitlement paywall (CAR-46 · **CAR-57 / CAR-87 / ADR-005** · **CAR-108**)

Identity (email OTP or Borderless password) and membership label (`base|psp|external`) are separate from **billing** in OTP / `pilot_enter` modes. Unpaid `external` learners cannot **start diagnosis** or **start a forge** until they have a Career Forge subscription (or a pilot allowlist). There is **no free forge**. Active BASE/PSP never hit the Stripe gate. An existing Roadmap is not withheld.

When `IDENTITY_METHOD=borderless_password`, a Borderless platform account **is** Career Forge included: entitled **only** if `users.borderless_user_id` is set (plus existing demo / cost-guard exclude). Pilot list, Stripe, `billing_entitled`, and BASE/PSP label do **not** bypass that gate.

Cost caps still apply to everyone (`FORGE_CAP_PER_USER_MONTH`).

Canonical product rule: [ADR-005](../decisions/ADR-005-identity-gate-product-entry.md).

---

## Rules

| Caller | Start diagnosis / start forge |
|--------|-------------------------------|
| **Password mode** (`IDENTITY_METHOD=borderless_password`) + `users.borderless_user_id` set | Allowed |
| **Password mode** without `borderless_user_id` (stale OTP/pilot JWT) | HTTP **402** `paywall` — until `POST /auth/signin` |
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

`IDENTITY_METHOD=borderless_password` (CAR-107 Labs cutover, CAR-108 entitlement): set the method explicitly. Sign-in **must not** call membership HTTP. `MEMBERSHIP_BACKEND=stub`. `BORDERLESS_MEMBERS_*` is **not** a cutover requirement. Access desk membership may stay stale (`Not entitled`) this slice.

---

## HTTP

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/billing/checkout` | Bearer |
| `POST` | `/billing/sync` | Bearer — polling after success_url |
| `POST` | `/billing/stripe/webhook` | Public + `Stripe-Signature` |
| `GET` | `/operator/access/pilot-emails` | Operator `access` / `both` |
| `POST` | `/operator/access/pilot-emails` | Operator `access` / `both` |
| `DELETE` | `/operator/access/pilot-emails/{email}` | Operator `access` / `both` |

Webhook events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`.

`GET /me/profile` includes `billing_entitled` and `checkout_available`.
`GET /operator/access/learners/{email}` also includes `pilot_email_listed`.
