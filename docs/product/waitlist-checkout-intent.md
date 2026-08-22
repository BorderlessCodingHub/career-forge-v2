# Waitlist + checkout — intent (v3+)

> **Status:** Intent only · **Not** in F3a runtime · Grill lock 2026-08-13 (CAR-35) · Amended CAR-56  
> **Related:** [V2-PLAN.md](../V2-PLAN.md) · [CAR-56](https://linear.app/career-forge-v2/issue/CAR-56)

## Current funnel (F3a)

Marketing CTA on `/welcome` → product `/`. `/welcome` does **not** require Email identity. The product loop does ([ADR-005](../decisions/ADR-005-identity-gate-product-entry.md) / [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57)): OTP at product entry, then Paywall before diagnosis for unpaid `external`.

`/welcome` is commercial Premium B (CAR-56): pricing / apply / syllabus / strategy UI is **scenery** (client modals only). Fake proof until [CAR-53](https://linear.app/career-forge-v2/issue/CAR-53). Waitlist and Stripe checkout are **not** runtime on Welcome (dissonance with in-loop Paywall is accepted).

[CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) `/welcome/premium-a` remains an **unlinked** HTML bake-off clone. `/welcome/premium-b` redirects to `/welcome` (CAR-52). Neither is waitlist/checkout runtime.

## Future intent (document only)

When growth / commercialisation is in scope (after Frame / platform auth as needed):

| Capability | Intent |
|------------|--------|
| **Email / waitlist** | Optional capture for non-pilot audiences; must not block BASE/PSP pilot paths |
| **Checkout** | Paid access or seat billing (e.g. Stripe-class) — **explicitly out of v2** (V2-PLAN fora) |

[CAR-57](https://linear.app/career-forge-v2/issue/CAR-57) / [ADR-005](../decisions/ADR-005-identity-gate-product-entry.md) is **in-loop Paywall** (unpaid `external` before diagnosis), not a marketing `/welcome` checkout. This intent doc still applies to waitlist + landing pricing theater.

## Non-goals for now

- No real waitlist / Stripe / email from Welcome scenery modals
- No promoting pricing theater as live checkout
- Entry-gate login is F3b OTP at product entry ([ADR-005](../decisions/ADR-005-identity-gate-product-entry.md) / [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57)) — not Welcome conversion

## When to promote this doc

Create an ADR + Linear issue only when issuer + payment provider contracts exist and Yuri scopes commercialisation.
