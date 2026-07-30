"""Auth scaffold (ADR-003 / CAR-23).

Wire: ``Authorization: Bearer <JWT>``.
Anon issuer now; Borderless issuer swaps in via :class:`BorderlessTokenProvider` (F3 / CAR-28).
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
