# Borderless issuer swap (F3 / CAR-28)

Bearer wire stays: `Authorization: Bearer <token>`.

1. Implement `BorderlessTokenProvider.verify` against `borderless-api`.
2. Keep `AuthPrincipal(external_id, provider)` shape.
3. `CompositeAuthProvider` already falls through from anonymous JWT to Borderless.

Code: `career_forge/auth/providers.py`, `api/deps.py`, `auth/middleware.py`.

See [ADR-003](../../../../../docs/decisions/ADR-003-forge-recovery-auth-scaffold.md).
