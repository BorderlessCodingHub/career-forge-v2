"""AuthProvider protocol + anonymous issuer + Borderless stub (F3).

Swap path for CAR-28: implement :meth:`BorderlessTokenProvider.verify` against
``borderless-api``, keep the same Bearer wire and :class:`AuthPrincipal` shape.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import jwt

from career_forge.auth.jwt_tokens import ANON_PROVIDER, decode_token, mint_anonymous_token
from career_forge.auth.principal import AuthPrincipal

_auth_provider: AuthProvider | None = None


@runtime_checkable
class AuthProvider(Protocol):
    """F3-ready identity contract — mint/verify without knowing the HTTP layer."""

    def mint_anonymous(self, external_id: str) -> str:
        """Return a Bearer access token for an anonymous external_id."""
        ...

    def verify(self, token: str) -> AuthPrincipal:
        """Validate token and return principal. Raise ``ValueError`` if invalid."""
        ...


class AnonymousLocalProvider:
    """App-signed JWT issuer (CAR-23). Claim ``provider=anonymous``."""

    def mint_anonymous(self, external_id: str) -> str:
        return mint_anonymous_token(external_id)

    def verify(self, token: str) -> AuthPrincipal:
        try:
            payload = decode_token(token)
        except jwt.PyJWTError as exc:
            raise ValueError("invalid or expired token") from exc
        sub = payload.get("sub")
        provider = payload.get("provider")
        if not isinstance(sub, str) or not sub.strip():
            raise ValueError("token missing sub")
        if provider != ANON_PROVIDER:
            raise ValueError(f"unsupported provider: {provider!r}")
        return AuthPrincipal(external_id=sub.strip(), provider=ANON_PROVIDER)


class BorderlessTokenProvider:
    """Stub for F3 / CAR-28 — same protocol, platform issuer not wired yet."""

    def mint_anonymous(self, external_id: str) -> str:
        raise NotImplementedError(
            "BorderlessTokenProvider does not mint anonymous tokens; use AnonymousLocalProvider"
        )

    def verify(self, token: str) -> AuthPrincipal:
        raise NotImplementedError(
            "Borderless issuer lands in F3 (CAR-28); token not verified here"
        )


class CompositeAuthProvider:
    """Try anonymous JWT first; later add Borderless without changing callers."""

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

    def verify(self, token: str) -> AuthPrincipal:
        try:
            return self._anonymous.verify(token)
        except ValueError:
            pass
        # F3: decode unverified provider claim and route to borderless.verify
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
