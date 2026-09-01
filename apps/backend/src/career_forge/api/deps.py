"""FastAPI dependencies for authenticated identity (ADR-003 / CAR-57)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.auth.principal import AuthPrincipal
from career_forge.config import settings
from career_forge.db.repositories.user import get_by_external_id
from career_forge.db.session import get_db
from career_forge.errors import NOT_ALLOWED_CODE, NOT_ALLOWED_MESSAGE, ForbiddenError
from career_forge.services.billing_pilot_emails import pilot_email_is_listed


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
    db: Session = Depends(get_db),
) -> AuthPrincipal:
    """Product-loop routes require Career Forge email identity (ADR-005 / CAR-100)."""
    if principal.provider != EMAIL_PROVIDER:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "email_identity_required",
                "message": "Email identity required for this action",
            },
        )
    if settings.identity_email_otp:
        return principal
    user = get_by_external_id(db, principal.external_id)
    if user is None or not pilot_email_is_listed(db, user.email):
        raise ForbiddenError(NOT_ALLOWED_MESSAGE, code=NOT_ALLOWED_CODE)
    return principal


def get_email_external_id(
    principal: Annotated[AuthPrincipal, Depends(require_email_provider)],
) -> str:
    return principal.external_id


ExternalId = Annotated[str, Depends(get_external_id)]
EmailExternalId = Annotated[str, Depends(get_email_external_id)]
