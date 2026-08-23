"""FastAPI dependencies for authenticated identity (ADR-003 / CAR-57)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
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


def require_email_provider(
    principal: Annotated[AuthPrincipal, Depends(get_principal)],
) -> AuthPrincipal:
    """Product-loop routes require Career Forge email OTP identity (ADR-005)."""
    if principal.provider != EMAIL_PROVIDER:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "email_identity_required",
                "message": "Email identity required for this action",
            },
        )
    return principal


def get_email_external_id(
    principal: Annotated[AuthPrincipal, Depends(require_email_provider)],
) -> str:
    return principal.external_id


ExternalId = Annotated[str, Depends(get_external_id)]
EmailExternalId = Annotated[str, Depends(get_email_external_id)]
