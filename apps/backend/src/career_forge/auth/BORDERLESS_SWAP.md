# Auth evolution notes (F3b)

> **Amend 2026-08-20:** Borderless JWT **issuer** swap is abandoned. Career Forge owns passwordless **email OTP**; Borderless is membership-only.

Bearer wire stays: `Authorization: Bearer <token>` · `AuthPrincipal(external_id, provider)`.

## Current (shipped)

- `AnonymousLocalProvider` — app-signed JWT `provider=anonymous` **or** `provider=email` (CAR-44)
- `CompositeAuthProvider` — app-signed first; stub `BorderlessTokenProvider` unused for IdP
- `POST /auth/otp/request` · `POST /auth/otp/verify` — promote new email / 409 chooser when owned
- Soft membership label on `users` after OTP verify (CAR-45) — stub allowlist until `MEMBERSHIP_BACKEND=http`

## F3b target (CAR-28 epic)

| Slice | Issue | Change |
|-------|-------|--------|
| OTP IdP | [CAR-44](https://linear.app/career-forge-v2/issue/CAR-44) | Mint/verify email OTP → JWT `provider=email`; promote/chooser after 1st forge |
| Membership | [CAR-45](https://linear.app/career-forge-v2/issue/CAR-45) | Soft label `base\|psp\|external` via stub → `GET members?email=` — **see [MEMBERSHIP.md](../../../../../docs/engineering/MEMBERSHIP.md)** |
| Send resume | [CAR-47](https://linear.app/career-forge-v2/issue/CAR-47) | Email resume link (prod mailer) |
| Paywall | [CAR-46](https://linear.app/career-forge-v2/issue/CAR-46) | Later — 1 free forge → Stripe for `external` |

Do **not** implement `BorderlessTokenProvider.verify` as the product IdP.

Code: `career_forge/auth/providers.py`, `api/auth.py`, `services/otp.py`, `services/mailer.py`, `services/membership.py`.

See [ADR-003](../../../../../docs/decisions/ADR-003-forge-recovery-auth-scaffold.md) · [pivot report](../../../../../docs/reports/2026-08-20-auth-otp-pivot.md).
