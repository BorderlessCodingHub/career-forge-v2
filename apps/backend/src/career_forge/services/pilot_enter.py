"""Pilot-list enter without OTP (CAR-100 freeze)."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user, get_by_external_id
from career_forge.errors import (
    NOT_ALLOWED_CODE,
    NOT_ALLOWED_MESSAGE,
    ForbiddenError,
    NotFoundError,
)
from career_forge.schemas.otp import _DEMO_EMAIL_SUFFIX, _normalize_otp_email
from career_forge.services.billing_pilot_emails import pilot_email_is_listed
from career_forge.services.membership import MembershipClient, apply_membership_label
from career_forge.services.otp import OtpPromoteResult, _check_rate_limit, _token_payload


def _fresh_external_id() -> str:
    return f"user-{uuid.uuid4().hex[:8]}"


def _is_placeholder_email(email: str | None) -> bool:
    return email is None or email.endswith(_DEMO_EMAIL_SUFFIX)


def _token_for(user: User) -> OtpPromoteResult:
    if not user.external_id:
        raise ForbiddenError(NOT_ALLOWED_MESSAGE, code=NOT_ALLOWED_CODE)
    payload = _token_payload(user.external_id)
    return {
        "status": "promoted",
        "access_token": payload["access_token"],
        "token_type": payload["token_type"],
        "external_id": payload["external_id"],
        "provider": payload["provider"],
        "expires_in": payload["expires_in"],
    }


def _bindable_session_user(session: Session, external_id: str) -> User:
    existing = get_by_external_id(session, external_id)
    if existing is None:
        return ensure_user(session, external_id)
    if _is_placeholder_email(existing.email):
        return existing
    return ensure_user(session, _fresh_external_id())


def enter_pilot(
    session: Session,
    *,
    email: str,
    client_ip: str,
    external_id: str,
    membership: MembershipClient | None = None,
) -> OtpPromoteResult:
    """Mint ``provider=email`` when the address is on ``billing_pilot_emails``."""
    if settings.identity_email_otp:
        raise NotFoundError("not found")

    rate_key = email.strip().lower()[:255]
    _check_rate_limit(email=rate_key, client_ip=client_ip, key_prefix="pilot:")

    try:
        normalized = _normalize_otp_email(email)
    except ValueError as exc:
        raise ForbiddenError(NOT_ALLOWED_MESSAGE, code=NOT_ALLOWED_CODE) from exc
    if not pilot_email_is_listed(session, normalized):
        raise ForbiddenError(NOT_ALLOWED_MESSAGE, code=NOT_ALLOWED_CODE)

    owner = session.scalar(select(User).where(User.email == normalized))
    if owner is not None:
        apply_membership_label(owner, normalized, membership)
        session.commit()
        return _token_for(owner)

    current = _bindable_session_user(session, external_id)
    current.email = normalized
    apply_membership_label(current, normalized, membership)
    session.commit()
    return _token_for(current)
