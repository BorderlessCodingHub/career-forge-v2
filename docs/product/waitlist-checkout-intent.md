# Waitlist + checkout — intent (v3+)

> **Status:** Intent only · **Not** in F3a runtime · Grill lock 2026-08-13 (CAR-35) · Amended CAR-56  
> **Related:** [V2-PLAN.md](../V2-PLAN.md) · [CAR-56](https://linear.app/career-forge-v2/issue/CAR-56)

## Current funnel (F3a)

Marketing CTA on `/welcome` → product `/` as **anon** via **Start diagnosis** (no signup, no email capture, no checkout).

`/welcome` is commercial Premium B (CAR-56): pricing / apply / syllabus / strategy UI is **scenery** (client modals only). Fake proof until [CAR-53](https://linear.app/career-forge-v2/issue/CAR-53). Waitlist and Stripe checkout are **not** runtime on Welcome.

[CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) `/welcome/premium-a` remains an **unlinked** HTML bake-off clone. `/welcome/premium-b` redirects to `/welcome` (CAR-52). Neither is waitlist/checkout runtime.

## Future intent (document only)

When growth / commercialisation is in scope (after Frame / platform auth as needed):

| Capability | Intent |
|------------|--------|
| **Email / waitlist** | Optional capture for non-pilot audiences; must not block BASE/PSP pilot paths |
| **Checkout** | Paid access or seat billing (e.g. Stripe-class) — **explicitly out of v2** (V2-PLAN fora) |

[CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) is **post-forge entitlement** (1 free forge → Stripe/allowlist for `external`), not a marketing `/welcome` checkout. This intent doc still applies to waitlist + landing pricing theater.

## Non-goals for now

- No real waitlist / Stripe / email from Welcome scenery modals
- No promoting pricing theater as live checkout
- Entry-gate login remains F3b OTP ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28) children Done) — not Welcome conversion

## When to promote this doc

Create an ADR + Linear issue only when issuer + payment provider contracts exist and Yuri scopes commercialisation.
