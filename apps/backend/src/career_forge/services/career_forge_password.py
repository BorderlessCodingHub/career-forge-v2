"""Career Forge password (CAR-129).

Signup stores the password and sends a confirmation link. The session opens
when that link is consumed. A later visit uses the stored password. A forgotten
password is replaced through a different link. Learner OTP verify stays closed
in password mode. The Borderless password is unchanged.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from urllib.parse import quote

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.email_otp import EmailOtp
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import (
    BadRequestError,
    ConflictError,
    EmailUnconfirmedError,
    GoneError,
    InvalidCredentialsError,
    MailDeliveryError,
)
from career_forge.identity_method import BORDERLESS_PASSWORD
from career_forge.services import otp as otp_service
from career_forge.services.mailer import get_mailer

logger = logging.getLogger(__name__)

CF_CONFIRM = "cf_confirm"
CF_RESET = "cf_reset"
PASSWORD_MIN_LENGTH = 8
LINK_TTL = timedelta(hours=24)
_EXPIRED = "This link has expired"
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def _require_password_mode() -> None:
    if settings.resolved_identity_method() != BORDERLESS_PASSWORD:
        raise GoneError("Career Forge password is only available in password mode")


def _token_payload(external_id: str) -> dict[str, str | int]:
    return {
        "access_token": get_auth_provider().mint_email(external_id),
        "token_type": "bearer",
        "external_id": external_id,
        "provider": EMAIL_PROVIDER,
        "expires_in": settings.jwt_anon_ttl_days * 24 * 3600,
    }


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=32,
    )
    salt_b64 = base64.urlsafe_b64encode(salt).decode("ascii")
    digest_b64 = base64.urlsafe_b64encode(digest).decode("ascii")
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt_b64}${digest_b64}"


def verify_password(password: str, stored: str) -> bool:
    try:
        scheme, n_raw, r_raw, p_raw, salt_b64, digest_b64 = stored.split("$")
        if scheme != "scrypt":
            return False
        expected = base64.urlsafe_b64decode(digest_b64.encode("ascii"))
        digest = hashlib.scrypt(
            password.encode("utf-8"),
            salt=base64.urlsafe_b64decode(salt_b64.encode("ascii")),
            n=int(n_raw),
            r=int(r_raw),
            p=int(p_raw),
            dklen=len(expected),
        )
    except (ValueError, TypeError):
        return False
    return secrets.compare_digest(digest, expected)


def _require_password_length(password: str) -> None:
    if len(password) < PASSWORD_MIN_LENGTH:
        raise BadRequestError("password must be at least 8 characters")


def _is_pending(user: User) -> bool:
    return (
        user.email_confirmed_at is None
        and user.borderless_user_id is None
        and bool(user.password_hash)
    )


def _retire_open_links(
    session: Session, *, email: str, provider: str, now: datetime
) -> None:
    session.execute(
        update(EmailOtp)
        .where(
            EmailOtp.email == email,
            EmailOtp.provider == provider,
            EmailOtp.consumed_at.is_(None),
        )
        .values(consumed_at=now),
    )


def _store_link(session: Session, *, email: str, provider: str) -> str:
    raw = secrets.token_urlsafe(32)
    now = datetime.now(UTC)
    _retire_open_links(session, email=email, provider=provider, now=now)
    session.add(
        EmailOtp(
            email=email,
            provider=provider,
            code_hash=otp_service._hash_code(raw),
            expires_at=now + LINK_TTL,
        ),
    )
    return raw


def _link_url(path: str, raw: str) -> str:
    base = settings.frontend_url.rstrip("/")
    return f"{base}{path}?token={quote(raw, safe='')}"


def _deliver(
    *,
    to_email: str,
    url: str,
    kind: str,
    locale: str | None,
) -> None:
    hours = int(LINK_TTL.total_seconds() // 3600)
    try:
        get_mailer().send_account_link(
            to_email=to_email,
            url=url,
            kind=kind,
            hours=hours,
            locale=locale,
        )
    except MailDeliveryError:
        raise
    except Exception as exc:
        raise MailDeliveryError() from exc


def _consume_token(session: Session, *, token: str, provider: str) -> str:
    now = datetime.now(UTC)
    row = session.scalar(
        select(EmailOtp).where(
            EmailOtp.provider == provider,
            EmailOtp.code_hash == otp_service._hash_code(token),
            EmailOtp.consumed_at.is_(None),
        ),
    )
    if row is None or row.expires_at <= now:
        if row is not None and row.expires_at <= now:
            row.consumed_at = now
            session.commit()
        raise BadRequestError(_EXPIRED)
    row.consumed_at = now
    session.flush()
    return row.email


def register_account(
    session: Session,
    *,
    name: str,
    email: str,
    password: str,
    client_ip: str,
) -> None:
    """Store a pending account and email a confirmation link. No session."""
    _require_password_mode()
    otp_service._check_rate_limit(email=email, client_ip=client_ip, key_prefix="cf-signup:")
    _require_password_length(password)
    user = session.scalar(select(User).where(User.email == email))
    if user is not None and not _is_pending(user):
        raise ConflictError("This email already has an account")
    if user is None:
        external_id = f"user-{uuid.uuid4()}"
        user = ensure_user(session, external_id, display_name=name)
        user.email = email
    else:
        user.display_name = name
    user.password_hash = hash_password(password)
    user.email_confirmed_at = None
    raw = _store_link(session, email=email, provider=CF_CONFIRM)
    locale = user.ui_locale
    session.commit()
    _deliver(
        to_email=email,
        url=_link_url("/account/confirm", raw),
        kind="confirm",
        locale=locale,
    )


def resend_confirmation(
    session: Session,
    *,
    email: str,
    client_ip: str,
) -> None:
    """Send a fresh confirmation link for a pending account. Password stays."""
    _require_password_mode()
    otp_service._check_rate_limit(email=email, client_ip=client_ip, key_prefix="cf-resend:")
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not _is_pending(user):
        return
    raw = _store_link(session, email=email, provider=CF_CONFIRM)
    locale = user.ui_locale
    session.commit()
    _deliver(
        to_email=email,
        url=_link_url("/account/confirm", raw),
        kind="confirm",
        locale=locale,
    )


def confirm_account(session: Session, *, token: str) -> dict[str, str | int]:
    """Consume the confirmation link and open the session."""
    _require_password_mode()
    email = _consume_token(session, token=token, provider=CF_CONFIRM)
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not user.external_id or not user.password_hash:
        session.rollback()
        raise BadRequestError(_EXPIRED)
    user.email_confirmed_at = datetime.now(UTC)
    session.commit()
    return _token_payload(user.external_id)


def request_password_reset(
    session: Session,
    *,
    email: str,
    client_ip: str,
) -> None:
    """Email a reset link only when a confirmed Career Forge password exists."""
    _require_password_mode()
    otp_service._check_rate_limit(email=email, client_ip=client_ip, key_prefix="cf-forgot:")
    user = session.scalar(select(User).where(User.email == email))
    if (
        user is None
        or user.email_confirmed_at is None
        or not user.password_hash
    ):
        return
    raw = _store_link(session, email=email, provider=CF_RESET)
    locale = user.ui_locale
    session.commit()
    try:
        _deliver(
            to_email=email,
            url=_link_url("/account/reset", raw),
            kind="reset",
            locale=locale,
        )
    except MailDeliveryError:
        logger.warning("Career Forge password reset email failed for %s", email)


def reset_password(
    session: Session,
    *,
    token: str,
    password: str,
) -> dict[str, str | int]:
    """Store a new password from a reset link and open a session on this browser."""
    _require_password_mode()
    _require_password_length(password)
    email = _consume_token(session, token=token, provider=CF_RESET)
    user = session.scalar(select(User).where(User.email == email))
    if user is None or not user.external_id or user.email_confirmed_at is None:
        session.rollback()
        raise BadRequestError(_EXPIRED)
    user.password_hash = hash_password(password)
    session.commit()
    return _token_payload(user.external_id)


def sign_in(
    session: Session,
    *,
    email: str,
    password: str,
    client_ip: str,
) -> dict[str, str | int]:
    """Open a session with a confirmed Career Forge password."""
    _require_password_mode()
    otp_service._check_rate_limit(email=email, client_ip=client_ip, key_prefix="cf-signin:")
    user = session.scalar(select(User).where(User.email == email))
    if (
        user is None
        or not user.external_id
        or not user.password_hash
        or not verify_password(password, user.password_hash)
    ):
        raise InvalidCredentialsError()
    if user.email_confirmed_at is None:
        raise EmailUnconfirmedError()
    return _token_payload(user.external_id)


def claim_pending_signup(session: Session, user: User) -> None:
    """Borderless sign-in confirms a pending signup and drops its password.

    A Career Forge password that was already confirmed stays.
    """
    if user.email_confirmed_at is not None or not user.password_hash or not user.email:
        return
    now = datetime.now(UTC)
    user.password_hash = None
    user.email_confirmed_at = now
    _retire_open_links(session, email=user.email, provider=CF_CONFIRM, now=now)
