# CAR-113 — Customer Portal + past_due / payment-failed on the current Stripe adapter

**Question:** Given the existing thin Stripe HTTP adapter (`apps/backend/src/career_forge/services/stripe_billing.py`: Checkout subscription + three webhook events, no Customer Portal), what does **Customer Portal + past_due / payment-failed** require?

**Snapshot (origin/main):** Thin urllib adapter (no Stripe SDK). `HttpStripeBillingClient` = `POST /v1/checkout/sessions` + `GET /v1/checkout/sessions/{id}` only. App HTTP: `POST /billing/checkout`, `POST /billing/sync`, `POST /billing/stripe/webhook`. Webhook handlers: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`. Entitlement grace set: `ACTIVE_STRIPE_SUBSCRIPTION_STATUSES = {active, trialing, past_due}` in `entitlement.py`. Mailer (`ResendMailer`) has OTP / operator OTP / resume only — **no billing templates**. No `billing_portal` call, no `invoice.*` handling, no portal route.

---

## Answer

**Portal needs one new Stripe API call + one authenticated app endpoint + Dashboard portal config. Dunning needs `invoice.payment_failed` (and/or `past_due` on `customer.subscription.updated`) as a learner-email trigger — not a new entitlement status.**

This repo already treats `past_due` as entitled (grace). Stripe’s lifecycle says: on failure → notify + let the customer update payment details; revoke on `canceled` / `unpaid`, not on the first failed attempt. The adapter already maps `customer.subscription.updated|deleted` through `stripe_subscription_is_active`, so Portal-driven cancel/reactivate and status flips to `past_due` / `unpaid` / `canceled` are **already in the entitlement path**. What is missing is (1) a way for the learner to open Customer Portal, (2) listening for payment-failed as an **email** signal, and (3) a billing-email channel (Stripe Dashboard emails and/or Career Forge Resend) separate from Continuity.

**Contract to implement (when a build ticket lands — not done here):**

1. Dashboard: Customer Portal configuration (at least payment-method update + cancel; invoice history optional). Branding optional.
2. Adapter: `POST /v1/billing_portal/sessions` with `customer` = `users.stripe_customer_id` + `return_url` (and optionally `flow_data[type]=payment_method_update` for dunning deep links).
3. App: `POST /billing/portal` (Bearer) → `{ portal_url }` — refuse if no `stripe_customer_id`.
4. Webhook destination: keep the three existing events; **add** `invoice.payment_failed` as a notify trigger (do not revoke solely from this event). Optionally listen for `invoice.paid` / `invoice.payment_action_required` as polish.
5. Learner email: either Stripe “failed payment” emails linked to Portal, or Resend templates fired from `invoice.payment_failed` / first transition to `past_due`, with CTA → Portal URL (or deep-link session). Not Continuity mail.

**No entitlement rule change is required for `past_due` grace** — it already matches Stripe’s “notify while past_due; revoke on unpaid/canceled” guidance. Confirm Dashboard failed-payment settings so the terminal state is `canceled` or `unpaid` (both already non-entitled here).

---

## 1. What the current adapter already does

### 1.1 HTTP surface ([ENTITLEMENT.md](../engineering/ENTITLEMENT.md))

| Method | Path | Role |
|---|---|---|
| `POST` | `/billing/checkout` | Create Checkout Session (`mode=subscription`) |
| `POST` | `/billing/sync` | Poll `retrieve_checkout_session` after `success_url` |
| `POST` | `/billing/stripe/webhook` | HMAC verify + `apply_stripe_event` |

Env gate: all three of `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_ID`. `FRONTEND_URL` builds Checkout success/cancel URLs only (`/forge?billing=…`).

### 1.2 Stripe calls in `stripe_billing.py`

- `POST /v1/checkout/sessions` — `client_reference_id` + `metadata[external_id]`, optional `customer_email`, single `line_items[0][price]`.
- `GET /v1/checkout/sessions/{id}` — sync path.

No `billing_portal/sessions`, no Customer retrieve/create, no Invoice APIs.

### 1.3 Webhook → entitlement

| Event handled | Effect |
|---|---|
| `checkout.session.completed` | If paid/complete: set `billing_entitled=True`, store `stripe_customer_id` / `stripe_subscription_id`, status `"active"` |
| `customer.subscription.updated` | Lookup by `customer`; `entitled = stripe_subscription_is_active(status)`; persist status |
| `customer.subscription.deleted` | Revoke; status `"canceled"` |

Lookup: `client_reference_id` / metadata on checkout; `stripe_customer_id` on subscription events. Portal sessions require that customer id — Checkout already writes it when payment succeeds.

### 1.4 Entitlement map (`ACTIVE_STRIPE_SUBSCRIPTION_STATUSES`)

| Stripe `subscription.status` | This repo | Product meaning |
|---|---|---|
| `active` | Entitled | Good standing |
| `trialing` | Entitled | Safe to provision (Stripe) |
| `past_due` | Entitled | Grace — dunning / update PM; **do not** 402 yet |
| `incomplete` / `incomplete_expired` | Not entitled | First invoice never activated |
| `unpaid` | Not entitled | Stripe: revoke after retries exhausted |
| `canceled` | Not entitled | Terminal; revoke |
| `paused` | Not entitled | Trial ended without PM |

OTP / `pilot_enter` path: BASE/PSP skip Stripe; `external` needs active Stripe status **or** `billing_entitled` flag **or** `billing_pilot_emails`. Password mode (`borderless_password`) ignores Stripe for entitlement (CAR-108) — Portal/dunning still matter for any future paid `external` under OTP restore, and for operators reading Stripe status.

Sources in-repo: `entitlement.py`, `ENTITLEMENT.md`, ADR-005.

---

## 2. Customer Portal — Stripe contract vs this adapter

### 2.1 Official integrate path

Stripe’s Customer Portal integration is:

1. **Configure** portal features in the Dashboard (or `POST /v1/billing_portal/configurations`).
2. **Create a portal session** and redirect the customer to `session.url`.
3. **Listen to webhooks** for subscription / payment-method changes.
4. Launch in live mode (separate sandbox vs live configs).

Sources:

- [Integrate the customer portal with the API](https://docs.stripe.com/customer-management/integrate-customer-portal)
- [Create a portal session](https://docs.stripe.com/api/customer_portal/sessions/create) — `POST /v1/billing_portal/sessions`

Minimal Customers v1 create:

```bash
curl https://api.stripe.com/v1/billing_portal/sessions \
  -u "$STRIPE_SECRET_KEY:" \
  -d "customer=cus_…" \
  --data-urlencode "return_url=https://example.com/forge"
```

Required input we already persist: `users.stripe_customer_id`. Required product URL: a `return_url` (Dashboard default or per-session). This repo has no portal return URL helper today (only Checkout `checkout_urls()`).

### 2.2 Missing app / adapter pieces

| Gap | Detail |
|---|---|
| Stripe API method | `create_billing_portal_session(customer_id, return_url, flow_data?)` on the thin client |
| App endpoint | e.g. `POST /billing/portal` → `{ portal_url }` (Bearer; 503 if Stripe off; 400/404 if no customer id) |
| Frontend CTA | “Manage billing” for entitled externals (not on Welcome — CAR-109 / waitlist intent) |
| Env / docs | Document portal return path; no new secret beyond existing `STRIPE_*` (portal uses the same secret key) |
| Dashboard | Enable payment method update (+ cancel if product allows self-serve cancel). Optional invoice history |

Optional but useful for dunning CTAs: [portal deep links](https://docs.stripe.com/customer-management/portal-deep-links) with `flow_data[type]=payment_method_update` so the email lands on “update card” only.

### 2.3 Webhooks Portal already expects — vs what we handle

From Stripe’s portal guide:

| Event | Portal relevance | This adapter |
|---|---|---|
| `customer.subscription.updated` | Upgrade/downgrade, cancel-at-period-end, reactivation, **status → past_due** | **Handled** (entitlement flip) |
| `customer.subscription.deleted` | Immediate cancel → revoke | **Handled** |
| `customer.updated` | Default PM / billing email changes | Not handled — OK if we do not mirror Customer fields locally |
| `payment_method.attached` / `detached` | PM inventory | Not handled — not required for entitlement |
| `billing_portal.session.created` | Audit only | Not needed for product access |
| `invoice.paid` | Confirm recovery after past_due | Not handled — status update via subscription.updated is enough for access |

**Verdict:** Portal does **not** force new entitlement webhooks if cancel/update already flow through `customer.subscription.*`. It **does** force the session-create API + app route + Dashboard config.

---

## 3. `past_due` / `invoice.payment_failed` — lifecycle mapped to entitlement

### 3.1 Stripe status semantics (primary)

From [How subscriptions work](https://docs.stripe.com/billing/subscriptions/overview) and [Using webhooks with subscriptions](https://docs.stripe.com/billing/subscriptions/webhooks):

- **`past_due`:** latest finalized invoice payment failed or was not attempted; invoices keep generating; Smart Retries may run; **notify the customer** to update payment details; Dashboard settings choose next status (`canceled`, `unpaid`, or stay `past_due`).
- **`unpaid` / `canceled`:** Stripe says **revoke** product access after retries (especially `unpaid`).
- **`invoice.payment_failed`:** payment attempt failed; **notify the customer**; collect new PM / update default PM; enable Smart Retries. Subscription may be `incomplete` on **first** invoice, or move toward `past_due` on renewals. This event is the reliable **failure signal**; access decisions should still follow **subscription.status**.

### 3.2 Map to this repo

| Stripe signal | Entitlement today | Gap |
|---|---|---|
| `status=past_due` via `customer.subscription.updated` | Still entitled (`ACTIVE_…`) | Persist status yes; **no learner email** |
| `invoice.payment_failed` | Ignored | **Missing webhook branch** for notify (and optional analytics) |
| `status=unpaid` / `canceled` / deleted | Not entitled | Already correct revoke path |
| Recovery → `active` via update / `invoice.paid` | Entitled again when status hits active set | Works if `subscription.updated` fires (it does on recovery) |

**Do not** set `billing_entitled=False` on `invoice.payment_failed` alone — that would fight the intentional `past_due` grace and Stripe’s own guidance.

### 3.3 Dashboard coupling (ops, not code)

Failed-payment settings decide whether grace ends in `canceled` vs `unpaid` vs lingering `past_due`. Both terminal-ish revoke statuses are already non-entitled here. Smart Retries + Stripe customer emails are Dashboard toggles under [Revenue recovery](https://docs.stripe.com/billing/revenue-recovery) — no adapter code required to enable them.

---

## 4. Learner email trigger points

Continuity email (CAR-109 / CONTEXT.md) is explicitly **not** billing dunning. Billing mail is a separate track.

### 4.1 Options Stripe documents

| Mechanism | Trigger | CTA |
|---|---|---|
| Dashboard “Send emails when card payments fail” | Each failed card payment | Hosted page or **Customer Portal** link |
| Dashboard renewal / trial / expiring-card emails | Schedule-based | Same link destination setting |
| App-owned email (Resend here) | Webhook-driven | App builds Portal session URL (or deep link) in the body |

Source: [Automate customer emails](https://docs.stripe.com/billing/revenue-recovery/customer-emails)

### 4.2 Recommended trigger matrix for Career Forge

| Trigger point | Who sends | When | Entitlement side effect |
|---|---|---|---|
| **A.** `invoice.payment_failed` | CF Resend **or** Stripe Dashboard | Every failed attempt (dedupe/policy TBD) | None — keep grace if status `past_due` |
| **B.** `customer.subscription.updated` where `status` becomes `past_due` (edge from non-past_due) | CF Resend (once per spell) | First entry into grace | None |
| **C.** Stripe Dashboard failed-payment email | Stripe | Same as A | None |
| **D.** Portal deep link in email | Session created at send time | CTA click | Later `subscription.updated` may restore `active` |
| **E.** Transition to `unpaid` / `canceled` | Optional “access ended” mail | After revoke | Access already revoked by webhook |

**Minimum for V3 “past_due / payment-failed learner email”:** A **or** C, plus a Portal (or hosted update) link. B is a good once-per-dunning-spell complement if Stripe Dashboard mail is off.

### 4.3 What the mailer lacks today

`career_forge/services/mailer.py`: `send_otp`, `send_operator_otp`, `send_resume_link` only. No `send_payment_failed` / `send_billing_portal_link`. Continuity will add its own templates later — keep billing templates namespaced separately so payment copy does not ride Continuity (CAR-109 standing preference).

---

## 5. Gap checklist (research only)

### Missing endpoints / adapter methods

1. `POST /v1/billing_portal/sessions` on `HttpStripeBillingClient`
2. `POST /billing/portal` (or equivalent) returning short-lived `url`
3. `return_url` helper (e.g. `FRONTEND_URL` + `/forge` or profile) — parallel to `checkout_urls()`
4. Optional: portal `flow_data` for `payment_method_update` when creating sessions from dunning email

### Missing / optional webhook events

| Event | Priority | Why |
|---|---|---|
| `invoice.payment_failed` | **Required for app-owned dunning email** | Official failure notify hook; does not replace status sync |
| `invoice.paid` | Optional | Confirm recovery; entitlement already follows subscription status |
| `invoice.payment_action_required` | Optional | 3DS / confirm; Stripe can email hosted confirm links |
| `customer.updated` / `payment_method.*` | Optional | Only if we store PM metadata locally |

Existing three events stay necessary. Portal cancel/update relies on `customer.subscription.updated|deleted` — **already present**.

### Learner email trigger points (summary)

1. `invoice.payment_failed` → “Payment failed — update card” + Portal URL  
2. First `past_due` on `customer.subscription.updated` → same (if not duplicating Stripe Dashboard mail)  
3. Optional: access-ended on `unpaid` / `canceled`  
4. **Not** Continuity inactivity / next-Node templates  

### Explicitly out of this gap (parent map)

- Welcome Checkout / waitlist Stripe on `/welcome`
- Stripe actions in Operator console
- Changing `past_due` out of the entitled set (would break the documented grace)
- Continuity email track carrying payment copy

---

## 6. Decisions this unlocks for the V3 map

When a later plan ticket slices build work, prefer:

1. **Portal session endpoint** as the smallest self-serve payment-update surface (thin adapter stays urllib; no SDK required).
2. **Keep `past_due` entitled**; use email + Portal to recover; revoke only when status leaves the active set (`unpaid` / `canceled` / deleted / incomplete*).
3. **Dunning email** either Dashboard-native (fastest ops) or Resend-on-`invoice.payment_failed` (product-owned copy); both need Portal (or Stripe hosted update) as CTA.
4. **Webhook destination** in Stripe Dashboard must include `invoice.payment_failed` if CF sends mail; Portal alone does not require it for access correctness.

---

## Implementation notes (not done here)

1. No code, migrations, or Linear Done in this ticket.
2. Provision live keys / Price / Portal config remains HITL ([CAR-121](https://linear.app/one-percent-better/issue/CAR-121) style ops).
3. `$15` Price vs Welcome copy is a separate lock ([CAR-120](https://linear.app/one-percent-better/issue/CAR-120)).
4. When implementing: extend `scripts/agent-verify.sh` / webhook tests for portal create + `invoice.payment_failed` notify seam; do not teach entitlement to revoke on payment_failed.

---

## Sources (primary only)

| Doc | URL |
|---|---|
| Integrate Customer Portal (API) | https://docs.stripe.com/customer-management/integrate-customer-portal |
| Create portal session API | https://docs.stripe.com/api/customer_portal/sessions/create |
| Customer Portal Sessions | https://docs.stripe.com/api/customer_portal/sessions |
| Portal deep links / flows | https://docs.stripe.com/customer-management/portal-deep-links |
| Subscriptions overview + statuses | https://docs.stripe.com/billing/subscriptions/overview |
| Webhooks with subscriptions (`invoice.payment_failed`, status table) | https://docs.stripe.com/billing/subscriptions/webhooks |
| Revenue recovery | https://docs.stripe.com/billing/revenue-recovery |
| Automate customer emails (failed payment → Portal) | https://docs.stripe.com/billing/revenue-recovery/customer-emails |
| In-repo entitlement | `apps/backend/src/career_forge/services/entitlement.py`, [ENTITLEMENT.md](../engineering/ENTITLEMENT.md) |
| In-repo adapter | `apps/backend/src/career_forge/services/stripe_billing.py`, `apps/backend/src/career_forge/api/billing.py` |
