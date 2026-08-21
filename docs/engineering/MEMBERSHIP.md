# Membership soft label (CAR-45)

Career Forge **identity** is email OTP (CAR-44). Borderless is **membership only** — not an IdP. After a successful OTP verify, Career Forge looks up the email and persists a soft label on `users`:

| Label | When | `membership_entitled` |
|-------|------|------------------------|
| `base` | active BASE member | `true` |
| `psp` | active PSP member | `true` |
| `external` | unknown, inactive, or non BASE/PSP | `false` |

No paywall in the membership slice itself. **CAR-46** enforces 1 free forge then a Stripe (or allowlist) gate for `external`. BASE/PSP stay entitled. See [ENTITLEMENT.md](./ENTITLEMENT.md).

The label is **re-resolved on every successful OTP login** (promote or owned-email chooser).

---

## Env

| Variable | Default | Purpose |
|----------|---------|---------|
| `MEMBERSHIP_BACKEND` | `stub` | `stub` (allowlist) or `http` (Borderless) |
| `MEMBERSHIP_STUB_ALLOWLIST` | empty | `email:program` comma pairs, e.g. `ana@borderless.com:base,psp@x.com:psp` |
| `BORDERLESS_MEMBERS_URL` | empty | Members resource URL (no query string) |
| `BORDERLESS_MEMBERS_TOKEN` | empty | Staging/prod service token (`Authorization: Bearer`) |

Unknown emails and HTTP failures **fail-open** to `external` / not entitled so OTP login is never blocked by membership.

Swap stub → HTTP when staging URL + token exist:

```
MEMBERSHIP_BACKEND=http
BORDERLESS_MEMBERS_URL=https://<host>/…/members
BORDERLESS_MEMBERS_TOKEN=<service-token>
```

---

## Contract note for Yuri / platform

We do **not** need issuer JWT, JWKS, or audience. Ask only:

```
GET {BORDERLESS_MEMBERS_URL}?email=<addr>
Authorization: Bearer <service-token>
→ { "active": true|false, "program": "base"|"psp"|null }
```

| Field | Meaning |
|-------|---------|
| `active` | Current membership |
| `program` | `"base"` or `"psp"` when the person is in a program; `null` otherwise |

Career Forge mapping:

- `active=true` and `program` in `{base, psp}` → that label + entitled
- anything else (including 4xx/5xx/timeout) → `external`, not entitled

Staging URL + service token unblocks `MEMBERSHIP_BACKEND=http`. Until then, eng uses the stub allowlist.

See [ADR-003](../decisions/ADR-003-forge-recovery-auth-scaffold.md) amend 2026-08-20 · [auth OTP pivot](../reports/2026-08-20-auth-otp-pivot.md).
