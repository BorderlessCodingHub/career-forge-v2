"""Auth scaffold (ADR-003 / CAR-23 / CAR-44).

Wire: ``Authorization: Bearer <JWT>``.
App-signed issuer for ``provider=anonymous`` and ``provider=email`` (OTP).
Borderless is membership-only (CAR-45) — not an IdP.
"""

from career_forge.auth.principal import AuthPrincipal
from career_forge.auth.providers import (
    AnonymousLocalProvider,
    AuthProvider,
    BorderlessTokenProvider,
    CompositeAuthProvider,
    get_auth_provider,
    set_auth_provider,
)

__all__ = [
    "AnonymousLocalProvider",
    "AuthPrincipal",
    "AuthProvider",
    "BorderlessTokenProvider",
    "CompositeAuthProvider",
    "get_auth_provider",
    "set_auth_provider",
]
