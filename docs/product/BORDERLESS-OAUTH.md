# Borderless OAuth — implementation spec

> **Status:** Spec, grill 2026-11-06. Amends [ADR-008](../decisions/ADR-008-borderless-password-credential-check.md) when the code lands.
> **Gate:** `IDENTITY_METHOD=borderless_password` keeps its name. In that mode the gate is Career Forge password plus Borderless OAuth.

Career Forge stays the session issuer. The browser stores the Career Forge JWT. The Borderless `sub` is stored on `users.borderless_user_id` and is never the JWT subject.

## Provider contract

Confidential client. Token endpoint auth is `client_secret_basic`. PKCE is `S256`.

| Item | Value |
|---|---|
| Issuer | `https://api.borderlesscoding.com/api/auth` |
| Discovery | `https://api.borderlesscoding.com/api/auth/.well-known/openid-configuration` |
| Authorize | `https://api.borderlesscoding.com/api/auth/oauth2/authorize` |
| Token | `https://api.borderlesscoding.com/api/auth/oauth2/token` |
| Scopes | `openid profile email offline_access` |
| Redirect URI | `https://labs.borderlesscoding.com/career-forge/auth/borderless/callback` |
| Consent | Already skipped for this app |

Resolve authorize, token, and JWKS from discovery. The rows above are the expected document.

`client_id` and `client_secret` come from the environment. The registration note that says `id_token` and `secret` is a placeholder, not a credential. With either value empty, or with `BORDERLESS_TOKEN_ENCRYPTION_KEY` empty, the OAuth control is absent and `GET /auth/borderless/start` does not redirect.

The token response carries `access_token` (1 hour), `id_token` (10 hours), and `refresh_token` (30 days, rotating). User data is the verified `id_token` claims. Membership refresh uses `grant_type=refresh_token` and the new `id_token`. Store the new refresh token on every successful refresh.

| Claim | Use |
|---|---|
| `sub` | Borderless user id. Stable account key. |
| `email`, `email_verified` | Link and contact email. |
| `name` | Display name for a new account, or a placeholder name. |
| `borderless_membership` | `FREE`, `STARTER`, `BASE`, or `PSP`. |
| `picture`, `preferred_username` | Ignore. |

Verify the `id_token` with the issuer JWKS: signature, `iss`, `aud` equal to the client id, `exp`, and `nonce`.

## Sign-in flow

1. The learner chooses Borderless on the password gate. The browser navigates to `GET /auth/borderless/start`.
2. The backend creates `state`, `nonce`, and a PKCE verifier, stores them in `HttpOnly`, `Secure`, `SameSite=Lax` cookies with a short lifetime, and redirects to the authorize URL with `response_type=code`, the scopes, `state`, `nonce`, and the S256 `code_challenge`.
3. Borderless sends the browser to `/career-forge/auth/borderless/callback` with `code` and `state`, or with an error.
4. The page posts `code` and `state` to `POST /auth/borderless/callback`.
5. The backend checks `state`, exchanges the code with the verifier and HTTP Basic auth, verifies the `id_token`, binds the account, seals the refresh token, applies the membership claim, and returns the Career Forge JWT.
6. The page stores that JWT the same way `POST /auth/account/signin` does, and the gate closes.

The redirect URI is the Labs URL above. It is a constant, not a request parameter. Tests mock discovery and the token endpoint. They do not call Borderless.

## Account binding

Search in this order:

1. `users.borderless_user_id == sub`.
2. A verified email matching `users.email` whose `borderless_user_id` is empty. Set `borderless_user_id` to `sub`.
3. No row. Create `external_id = user-{uuid}`, store the email and `sub`.

A row whose `borderless_user_id` is a different `sub` raises `BorderlessIdentityMismatchError` (409). `email_verified` false raises `BorderlessEmailUnverifiedError` (403). A later verified email from Borderless replaces the stored email only when no other row has it. A pending Career Forge signup is claimed, as the password sign-in already does. The Career Forge password hash stays as it is.

The JWT subject remains `external_id`.

## Membership

| Claim | Stored label | Included |
|---|---|---|
| `BASE` | `base` | yes |
| `PSP` | `psp` | yes |
| `FREE`, `STARTER`, anything else, missing | `external` | no |

`users.operator_membership_label` of `base` or `psp` still wins.

Later reads use the sealed refresh token. A successful refresh replaces the refresh token and the label from the new `id_token`. `invalid_grant` latches the row: keep the last label, stop refreshing, and wait for the next OAuth sign-in. The Career Forge session stays valid until it expires.

The learner path does not call `GET /api/users/profile` and does not call `/oauth2/userinfo`. The OAuth access token is not stored.

## What leaves the gate

On `IDENTITY_METHOD=borderless_password` the gate shows the Career Forge password (sign-in, sign-up, forgot, resend) and the OAuth control.

Remove the Borderless email and password form, its forgot-password link, and the modal that opens `platform.borderlesscoding.com/sign-up`. `POST /auth/signin`, the route that forwards that password, returns 410. `POST /auth/account/signin` stays.

OTP and `pilot_enter` do not show the OAuth control.

## Persistence

Add a sealed `users.borderless_refresh_token`, encrypted with `BORDERLESS_TOKEN_ENCRYPTION_KEY`, same scheme as the existing access-token column. OAuth sign-in writes that column and clears the stored Borderless access token so a later entitlement read cannot take the profile path. An old access token left from before this change is not read.

## Failures

Cancellation, `error` on the callback, a `state` mismatch, or a token endpoint failure opens no session. The learner returns to the gate with one generic message.

403 and 409 keep the specific errors above.

## Done when

- The OAuth control is absent unless client id, client secret, and the encryption key are set.
- A mocked code exchange returns a Career Forge JWT and stores `sub` plus a sealed refresh token.
- `BASE` and `PSP` include. `FREE` and `STARTER` are `external`.
- A second refresh stores the rotated refresh token and updates the label.
- `invalid_grant` leaves the last label and the Career Forge session in place.
- Mismatched `sub` is 409. Unverified email is 403.
- `POST /auth/signin` is 410. Career Forge password sign-in still opens a session.
- The password gate in `borderless_password` mode has no Borderless password field and no Borderless sign-up modal.
