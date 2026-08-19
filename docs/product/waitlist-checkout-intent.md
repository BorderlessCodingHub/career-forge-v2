# Waitlist + checkout — intent (v3+)

> **Status:** Intent only · **Not** in F3a runtime · Grill lock 2026-08-13 (CAR-35)  
> **Related:** [V2-PLAN.md](../V2-PLAN.md) · [CAR-35](https://linear.app/career-forge-v2/issue/CAR-35)

## Current funnel (F3a)

Marketing CTA on `/welcome` → product `/` as **anon** (no signup, no email capture, no checkout).

[CAR-41](https://linear.app/career-forge-v2/issue/CAR-41) `/welcome/premium-a` and `/welcome/premium-b` are **unlinked visual clones** with fake pricing/apply theater. They are **not** waitlist or checkout runtime and must not replace `/welcome`.

## Future intent (document only)

When growth / commercialisation is in scope (after Frame / platform auth as needed):

| Capability | Intent |
|------------|--------|
| **Email / waitlist** | Optional capture for non-pilot audiences; must not block BASE/PSP pilot paths |
| **Checkout** | Paid access or seat billing (e.g. Stripe-class) — **explicitly out of v2** (V2-PLAN fora) |

## Non-goals for now

- No waitlist UI on `/welcome` in CAR-35
- No pricing table (even “coming soon”) in F3a
- No entry-gate login until F3b issuer ([CAR-28](https://linear.app/career-forge-v2/issue/CAR-28))

## When to promote this doc

Create an ADR + Linear issue only when issuer + payment provider contracts exist and Yuri scopes commercialisation.
