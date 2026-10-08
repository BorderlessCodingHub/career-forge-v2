# ADR-005: Identity gate at product entry · paywall before diagnosis

The product loop requires **Email identity** before any step. Unpaid `external` learners also hit **Paywall** before starting diagnosis or a forge. Welcome, share, and resume stay public. This kills anonymous LLM spend, post-forge OTP as the identity gate, and the one free forge.

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-08-22 (Founder Engineer) · **Amend 2026-09-12:** password entry = Borderless credential check, CF still IdP ([ADR-008](./ADR-008-borderless-password-credential-check.md)) · **Amend 2026-10-07:** public price USD $7/mo ([price lock](https://linear.app/one-percent-better/issue/CAR-120/dollar15-stripe-price-vs-welcome-copy-lock)) · **Amend 2026-10-08:** one lifetime forge for `external`, then the subscription; BASE/PSP stay at 2 completed forges per UTC month ([V3-PLAN](../V3-PLAN.md) § Freemium) |
| **Date** | 2026-08-22 |
| **Deciders** | Pedro Alano |
| **Linear (v2)** | [CAR-57](https://linear.app/career-forge-v2/issue/CAR-57) · project F3b — Email OTP auth + membership |
| **Supersedes (partial)** | [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) identity-gate **timing** (anon until 1st forge → OTP on `/forge/complete`) and CAR-46 **free forge**. Does **not** supersede artifacts, share/resume tokens, Bearer + stream ticket, or Career Forge email OTP as IdP. |
| **Glossary** | [CONTEXT.md](../../CONTEXT.md) — Email identity, Identity gate, Anonymous session, Membership, Entitlement, Paywall, Product loop |

---

## Context

ADR-003 / F3b (CAR-44…46) shipped **Anonymous session** through diagnosis + first forge, then mandatory OTP on `/forge/complete`, then one free forge for `external` before Stripe. That was deliberate PLG: wow, then capture.

It also meant we paid for nameless diagnosis and forge, the OTP wall was **UI-only** (roadmap APIs still accepted anon JWT), and Membership could not be labeled until after the expensive work.

---

## Decision

### 1. Identity gate = Email identity at product entry

| Concern | Decision |
|---------|----------|
| Event | **Email identity** (Career Forge 6-digit OTP). Not Borderless SSO. |
| When | Before the **product loop** (goal → diagnosis → forge → roadmap → validate → report). |
| Where not | **Welcome**, share, resume stay public. No login on marketing. |
| Enforcement | **Server:** product-loop APIs require `provider=email`. Delete the `/forge/complete` OTP wall — one gate, not two. |
| Deep links | Identity gate, then **return to the URL** if client state still belongs to them. **No** server-side mid-flight diagnosis resume (ADR-003 out of scope stands). |
| Migration | Existing Anonymous sessions with artifacts: **promote / chooser** (CAR-44 semantics). **No new anon mints** on the happy path. |

### 2. Paywall = billing before diagnosis for `external`

| Concern | Decision |
|---------|----------|
| Entitled BASE/PSP | Diagnosis + forge without Stripe. |
| Unpaid `external` | **402** on **start diagnosis** and **start forge**. No free forge. No unpaid diagnosis. |
| Goal picker | Allowed without billing (no LLM). |
| Existing Roadmap | **Not ransomed** — Continue / validate / report stay usable. Paywall does not lock `/` for someone who already has an artifact. |
| Welcome | Pricing chrome is honest copy (CAR-92): BASE/PSP included · External **$7/mo** billed in-loop. Runtime checkout is **not** on Welcome. Checkout may present that USD price in BRL. Amended 2026-10-07; was $15/mo. |
| Pilot grant | **Amended by CAR-87:** `billing_pilot_emails` is the runtime source. Migration 018 imports `ENTITLEMENT_BILLING_ALLOWLIST` once; runtime then ignores the env. |

Identity and Paywall remain **two gates**. Early identity does not mean BASE/PSP pay. It does mean `external` pays before we run diagnosis.

### 3. Pilots

CAR-36 / V2-PLAN F3.7 (E2E on anon scaffold) is **dead**. Pilots use Email identity + the database pilot billing list (and real membership when the API exists). No secret anon bypass.

### 4. Temporary freeze — skip OTP (CAR-100, 2026-09-01)

While Resend cannot deliver to arbitrary inboxes (`onboarding@resend.dev`), Labs may set `IDENTITY_EMAIL_OTP=false`:

| Concern | Freeze behavior |
|---------|-----------------|
| Learner entry | Email + Continue. `POST /auth/pilot/enter` mints `provider=email` if the address is on `billing_pilot_emails`. No 6-digit code. |
| Exclusive door | Product-loop APIs require the session user's email on that list. BASE/PSP, Stripe, and prior OTP JWTs are blocked unless listed. |
| Operator | Unchanged (still OTP). |
| Restore | `IDENTITY_EMAIL_OTP=true` (code default) restores this ADR's OTP + billing split. OTP implementation is not deleted. |

Impersonation (typing a listed email) is accepted for the closed cohort.

### 5. Learner entry method (CAR-102 / ADR-008)

`IDENTITY_METHOD` (`email_otp` \| `pilot_enter` \| `borderless_password`) is the explicit switch. Empty → derive from `IDENTITY_EMAIL_OTP` (`true` → OTP, `false` → pilot enter). **`IDENTITY_EMAIL_OTP=false` is never password mode.** Borderless password does not replace Career Forge as JWT issuer — see [ADR-008](./ADR-008-borderless-password-credential-check.md).

### 6. Freemium and Career Forge password (2026-10-08)

This amends §2. The title’s “paywall before diagnosis” is the 2026-08-22 rule. From this amend, the paywall sits after the lifetime forge.

| Concern | Decision |
|---------|----------|
| Included programs | BASE and PSP only, from `GET /api/users/profile` field `membership`. FREE, any other value, and a missing field are `external`. |
| BASE / PSP | No Stripe. Up to 2 completed forges in a UTC month. The third waits until the next month. No Stripe offer on that path. |
| External | One forge in the life of the account, and only when no forge on that account has been completed. Starting it spends the allowance, including failure or leaving. Diagnosis may be repeated until that start. A completed forge, including one completed as BASE or PSP, spends it too. |
| After the allowance | 402 on start diagnosis and start forge until a Career Forge subscription (USD $7/mo). Cancel does not restore another free forge. |
| Subscribed external | Outside the 2/month ceiling. The global monthly API budget still applies. |
| Failed profile read | Last successful label stands. The next entitlement check retries in silence once five minutes have passed. No poll while the learner is away. |
| Password mode | `borderless_user_id` alone does not include the learner. |
| Career Forge password | First access proves the email with OTP and sets a password Career Forge stores. Later access uses that password. The same email on Borderless sign-in is the same account. |
| Existing Roadmap | Still not withheld. Welcome still does not host checkout. |

---

## Considered options (rejected)

- **Post-forge OTP** — capture after wow. Rejected: nameless LLM spend; people bounce without Email identity.
- **UI-only gate** — cheap, does not stop `POST /diagnosis/interview/start` with an anon JWT.
- **Paywall on Welcome** — reopens the public landpage. Rejected.
- **Keep one free forge** after early identity — stops *anonymous* spend only; unpaid diagnosis still burns the pool.
- **Ransom existing artifacts** until Stripe — hostage past work.
- **Delete anon tokens this release** — strands resume links and in-browser forges we promised to promote.

---

## Consequences

- Happy path from 2026-10-08: Welcome → identity → goal → one forge for `external` (diagnosis included) → Paywall → subscription. BASE/PSP skip the Paywall and stop at 2 completed forges in the UTC month.
- `FREE_FORGE_LIMIT` for `external` goes away as an unbounded counter. The allowance is one start in the life of the account. Entitlement still runs on diagnosis start and on forge start.
- F3a “login not required” is historical for landing work already shipped; **humans in the loop** now require CAR-57.
- Cost caps (`FORGE_CAP_PER_USER_MONTH`, pool) still apply to entitled learners.

---

## Related

- [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) — recovery + IdP wire (still binding except timing / free forge)
- [ENTITLEMENT.md](../engineering/ENTITLEMENT.md)
- [V2-PLAN.md](../V2-PLAN.md) — Decision #1 amend 2026-08-22; F3.6 / F3.7
- Grill session 2026-08-22
- Grill session 2026-09-01 (CAR-100 freeze)
