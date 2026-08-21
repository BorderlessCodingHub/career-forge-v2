# Entitlement paywall (CAR-46)

Identity (email OTP) and membership label (`base|psp|external`) are separate from **billing**. After the free forge, `external` learners need a Career Forge subscription (or a pilot allowlist). Active BASE/PSP never hit the Stripe gate.

Cost caps still apply to everyone (`FORGE_CAP_PER_USER_MONTH`).

---

## Rules

| Caller | After 1 enqueued `roadmap_forge` run |
|--------|--------------------------------|
| `membership_entitled` BASE/PSP | Allowed (no Stripe) |
| `external` + `billing_entitled` (Stripe or allowlist) | Allowed |
| `external` otherwise | HTTP **402** `paywall` |
| `demo-ana` / synthetic gate | Excluded (same as CostGuard) |

The gate runs on `POST /forge` and `POST /forge/runs` **before** CostGuard.

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
