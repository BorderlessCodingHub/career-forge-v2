# Learner mail — absolute links

> **Status:** Implemented · Grill lock 2026-10-18
> **Observed:** Confirmation letter received 2026-10-18 14:01 from `careerforgelabs@gmail.com`. Body was the English confirm template. The link line was `/account/confirm?token=…` with no scheme and no host.

## Problem

`_link_url` joins `FRONTEND_URL` to the path. Production compose sets `FRONTEND_URL: ${FRONTEND_URL:-}`. An empty base yields a path. SMTP, Resend, and SES send that path as `text/plain`. A mail client linkifies a line that starts with `http://` or `https://`. A path stays text.

The same join builds every learner letter that carries a URL.

## Lock

A learner letter carries one absolute URL on its own line, in the text body that already exists. The copy catalogs stay as they are. English and pt-BR receive the same URL.

The public base is `FRONTEND_URL` with one trailing slash removed. A legal base has:

- scheme `http` or `https`
- a host, and an optional port
- path exactly `/career-forge`
- no userinfo, query, or fragment

`/career-forge` is the Next `basePath` on every deploy. The assembler preserves that path and appends the letter path (`/account/confirm`, `/account/reset`, `/resume/…`, `/roadmap?…`, `/billing/card`).

| Mailer | Legal base |
|---|---|
| `smtp`, `resend`, `ses` | Legal base whose scheme is `https` |
| any other value, including `log` | Legal base with `http` or `https` |

`http://localhost:3300/career-forge` stays legal for the log mailer. Labs mail uses `https://labs.borderlesscoding.com/career-forge`.

One assembler performs the join and the check. Confirm, reset, resume, continuity, and billing call it before a letter is rendered. An illegal base raises before any network send, so the path never becomes a body.

## When the base is illegal

Each caller keeps the reaction it has today. The letter is not sent.

| Caller | Reaction that stays |
|---|---|
| Signup, resend confirmation | HTTP 503 `Could not send the email`. The pending account remains. The screen already offers resend. |
| Password reset | Generic success. The response does not reveal whether the account exists. A warning is logged. |
| Resume link | The new token is not committed. |
| Continuity | That stretch stays unspent. The sweep continues. |
| Billing failed-charge | That spell stays unspent. |

OTP and the Operator console code have no URL. They stay as they are.

Checkout success and cancel use `FRONTEND_URL` plus `/billing/return`. They are not letters, and that page does not start a forge. The Stripe portal return URL also uses `FRONTEND_URL` and is not a letter.

Production compose keeps an empty default. The process does not invent a Labs origin.

## People who already received the path

They use the confirmation resend control that already exists. There is no mass resend. After Labs `FRONTEND_URL` is the https base above, resend retires the open confirmation token and sends a new absolute URL.

## Acceptance

1. With `MAILER_BACKEND=smtp` and `FRONTEND_URL=https://labs.borderlesscoding.com/career-forge`, the confirm body contains `https://labs.borderlesscoding.com/career-forge/account/confirm?token=` on its own line. Reset, resume, continuity, and billing bodies use that same origin.
2. With an empty `FRONTEND_URL`, signup returns 503 and no mailer sends.
3. With `MAILER_BACKEND=smtp` and `FRONTEND_URL=http://localhost:3300/career-forge`, no mailer sends.
4. With `MAILER_BACKEND=log` and `FRONTEND_URL=http://localhost:3300/career-forge`, the log line contains that absolute confirm URL.
5. A base of `https://labs.borderlesscoding.com` (no `/career-forge`) does not send.
6. Reset with an illegal base still returns generic success and does not send.
7. Resume with an illegal base leaves no new token committed.
8. Continuity and billing with an illegal base leave the stretch and the spell unspent.
9. On Labs, `FRONTEND_URL=https://labs.borderlesscoding.com/career-forge` is set on the host before the next confirmation letter goes out.

## Done when

An implementer can point at one assembler, the five callers, and tests for rows 1–8. Row 9 is a host setting, checked on the running Labs backend, not a code default.
