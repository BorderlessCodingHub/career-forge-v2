"""AuthProvider protocol + app-signed JWT issuer + Borderless stub (unused IdP).

Career Forge owns email OTP (CAR-44). Do not implement Borderless as IdP —
membership soft label is CAR-45.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import jwt

from career_forge.auth.jwt_tokens import (
    ANON_PROVIDER,
    APP_PROVIDERS,
    EMAIL_PROVIDER,
    decode_token,
    mint_anonymous_token,
    mint_email_token,
)
from career_forge.auth.principal import AuthPrincipal

_auth_provider: AuthProvider | None = None


@runtime_checkable
class AuthProvider(Protocol):
    """Identity contract — mint/verify without knowing the HTTP layer."""

    def mint_anonymous(self, external_id: str) -> str:
        """Return a Bearer access token for an anonymous external_id."""
        ...

    def mint_email(self, external_id: str) -> str:
        """Return a Bearer access token after email OTP verify (CAR-44)."""
        ...

    def verify(self, token: str) -> AuthPrincipal:
        """Validate token and return principal. Raise ``ValueError`` if invalid."""
        ...


class AnonymousLocalProvider:
    """App-signed JWT issuer (CAR-23/44). Claims ``provider=anonymous|email``."""

    def mint_anonymous(self, external_id: str) -> str:
        return mint_anonymous_token(external_id)

    def mint_email(self, external_id: str) -> str:
        return mint_email_token(external_id)

    def verify(self, token: str) -> AuthPrincipal:
        try:
            payload = decode_token(token)
        except jwt.PyJWTError as exc:
            raise ValueError("invalid or expired token") from exc
        sub = payload.get("sub")
        provider = payload.get("provider")
        if not isinstance(sub, str) or not sub.strip():
            raise ValueError("token missing sub")
        if provider not in APP_PROVIDERS:
            raise ValueError(f"unsupported provider: {provider!r}")
        assert provider in (ANON_PROVIDER, EMAIL_PROVIDER)
        return AuthPrincipal(external_id=sub.strip(), provider=provider)


class BorderlessTokenProvider:
    """Legacy stub — Borderless is membership-only (CAR-45), not IdP."""

    def mint_anonymous(self, external_id: str) -> str:
        raise NotImplementedError(
            "BorderlessTokenProvider does not mint anonymous tokens; use AnonymousLocalProvider"
        )

    def mint_email(self, external_id: str) -> str:
        raise NotImplementedError(
            "BorderlessTokenProvider does not mint email tokens; use AnonymousLocalProvider"
        )

    def verify(self, token: str) -> AuthPrincipal:
        raise NotImplementedError(
            "Borderless issuer abandoned 2026-08-20; email OTP is Career Forge IdP"
        )


class CompositeAuthProvider:
    """App-signed JWT first; Borderless stub kept only for protocol completeness."""

    def __init__(
        self,
        *,
        anonymous: AnonymousLocalProvider | None = None,
        borderless: BorderlessTokenProvider | None = None,
    ) -> None:
        self._anonymous = anonymous or AnonymousLocalProvider()
        self._borderless = borderless or BorderlessTokenProvider()

    def mint_anonymous(self, external_id: str) -> str:
        return self._anonymous.mint_anonymous(external_id)

    def mint_email(self, external_id: str) -> str:
        return self._anonymous.mint_email(external_id)

    def verify(self, token: str) -> AuthPrincipal:
        try:
            return self._anonymous.verify(token)
        except ValueError:
            pass
        try:
            return self._borderless.verify(token)
        except NotImplementedError as exc:
            raise ValueError("invalid or expired token") from exc


def get_auth_provider() -> AuthProvider:
    global _auth_provider
    if _auth_provider is None:
        _auth_provider = CompositeAuthProvider()
    return _auth_provider


def set_auth_provider(provider: AuthProvider | None) -> None:
    """Override for tests; pass ``None`` to reset to default composite."""
    global _auth_provider
    _auth_provider = provider
