# Entitlement paywall (CAR-46 · **CAR-57 / ADR-005**)

Identity (email OTP) and membership label (`base|psp|external`) are separate from **billing**. Unpaid `external` learners cannot **start diagnosis** or **start a forge** until they have a Career Forge subscription (or a pilot allowlist). There is **no free forge**. Active BASE/PSP never hit the Stripe gate. An existing Roadmap is not withheld.

Cost caps still apply to everyone (`FORGE_CAP_PER_USER_MONTH`).

Canonical product rule: [ADR-005](../decisions/ADR-005-identity-gate-product-entry.md).

---

## Rules

| Caller | Start diagnosis / start forge |
|--------|-------------------------------|
| `membership_entitled` BASE/PSP | Allowed (no Stripe) |
| `external` + `billing_entitled` (Stripe or allowlist) | Allowed |
| `external` otherwise | HTTP **402** `paywall` |
| `demo-ana` / synthetic gate | Excluded (same as CostGuard) |

Also allowed **without** billing: choosing a goal; Continue / validate / report on a Roadmap they already have.

The gate runs on diagnosis **start** and on `POST /forge` / `POST /forge/runs` **before** CostGuard. Product-loop APIs also require Email identity (`provider=email`) — see ADR-005.

---

## Env

| Variable | Purpose |
|----------|---------|
| `ENTITLEMENT_BILLING_ALLOWLIST` | Comma emails treated as billed (pilots until Stripe) |
| `STRIPE_SECRET_KEY` | Checkout + retrieve session |
| `STRIPE_WEBHOOK_SECRET` | `Stripe-Signature` HMAC |
| `STRIPE_PRICE_ID` | Subscription price for Checkout |
| `FRONTEND_URL` | Success/cancel URLs (`/forge?billing=success&session_id={CHECKOUT_SESSION_ID}`) |

Stripe is **off** until all three `STRIPE_*` values are set. Allowlist still works.

---

## HTTP

| Method | Path | Auth |
|--------|------|------|
| `POST` | `/billing/checkout` | Bearer |
| `POST` | `/billing/sync` | Bearer — polling after success_url |
| `POST` | `/billing/stripe/webhook` | Public + `Stripe-Signature` |

Webhook events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`.

`GET /me/profile` includes `billing_entitled` and `checkout_available`.
