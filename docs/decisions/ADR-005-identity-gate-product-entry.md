# ADR-005: Identity gate at product entry · paywall before diagnosis

The product loop requires **Email identity** before any step. Unpaid `external` learners also hit **Paywall** before starting diagnosis or a forge. Welcome, share, and resume stay public. This kills anonymous LLM spend, post-forge OTP as the identity gate, and the one free forge.

| Field | Value |
|-------|-------|
| **Status** | **Accepted** — grill 2026-08-22 (Founder Engineer) |
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
| Welcome | Pricing remains **scenery** until a later honesty pass (CAR-53). Runtime checkout is **not** on Welcome. Dissonance accepted. |
| Stub | `ENTITLEMENT_BILLING_ALLOWLIST` still stands in for Stripe keys. The 402 just fires earlier. |

Identity and Paywall remain **two gates**. Early identity does not mean BASE/PSP pay. It does mean `external` pays before we run diagnosis.

### 3. Pilots

CAR-36 / V2-PLAN F3.7 (E2E on anon scaffold) is **dead**. Pilots use Email identity + billing allowlist (and real membership when the API exists). No secret anon bypass.

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

- Happy path: Welcome → `/` → OTP → membership → goal (even if unpaid `external`) → Paywall if unpaid `external` → diagnosis → forge.
- `FREE_FORGE_LIMIT` for `external` goes away. Entitlement must run on diagnosis start, not only `POST /forge`.
- F3a “login not required” is historical for landing work already shipped; **humans in the loop** now require CAR-57.
- Cost caps (`FORGE_CAP_PER_USER_MONTH`, pool) still apply to entitled learners.

---

## Related

- [ADR-003](./ADR-003-forge-recovery-auth-scaffold.md) — recovery + IdP wire (still binding except timing / free forge)
- [ENTITLEMENT.md](../engineering/ENTITLEMENT.md)
- [V2-PLAN.md](../V2-PLAN.md) — Decision #1 amend 2026-08-22; F3.6 / F3.7
- Grill session 2026-08-22
