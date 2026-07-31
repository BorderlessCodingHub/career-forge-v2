"""FastAPI dependencies for authenticated identity (ADR-003)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from career_forge.auth.principal import AuthPrincipal


def get_principal(request: Request) -> AuthPrincipal:
    """Return principal set by :class:`BearerAuthMiddleware`."""
    principal = getattr(request.state, "principal", None)
    if principal is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return principal


def get_external_id(principal: Annotated[AuthPrincipal, Depends(get_principal)]) -> str:
    """Stable external user id from Bearer ``sub`` — prefer over body/query ``user_id``."""
    return principal.external_id


ExternalId = Annotated[str, Depends(get_external_id)]
