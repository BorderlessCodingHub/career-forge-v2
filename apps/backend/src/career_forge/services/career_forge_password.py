"""Career Forge password (CAR-129).

Distinct from the Borderless password. The first access, and a forgotten
password, prove the inbox with a one-time code. Later access uses the stored
password. Learner OTP verify stays closed in password mode.
"""

from __future__ import annotations

import base64
import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.email_otp import EmailOtp
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import BadRequestError, GoneError, InvalidCredentialsError
from career_forge.identity_method import BORDERLESS_PASSWORD
from career_forge.services import otp as otp_service
from career_forge.services.mailer import Mailer, get_mailer

CF_PASSWORD_PROVIDER = "cf_password"
PASSWORD_MIN_LENGTH = 8
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1


def _generate_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


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


def _user_for_email(session: Session, email: str) -> User:
    user = session.scalar(select(User).where(User.email == email))
    if user is None:
        external_id = f"user-{uuid.uuid4()}"
        user = ensure_user(session, external_id, display_name=email.split("@", 1)[0])
        user.email = email
        return user
    if not user.external_id:
        user.external_id = f"user-{uuid.uuid4()}"
    return user


def _consume_code(session: Session, *, email: str, code: str) -> None:
    now = datetime.now(UTC)
    row = session.scalar(
        select(EmailOtp)
        .where(
            EmailOtp.email == email,
            EmailOtp.provider == CF_PASSWORD_PROVIDER,
            EmailOtp.consumed_at.is_(None),
        )
        .order_by(EmailOtp.created_at.desc()),
    )
    if row is None or row.expires_at <= now or row.code_hash != otp_service._hash_code(code.strip()):
        if row is not None and row.expires_at <= now:
            row.consumed_at = now
            session.commit()
        raise BadRequestError("invalid or expired code")
    row.consumed_at = now
    session.flush()


def request_code(
    session: Session,
    *,
    email: str,
    client_ip: str,
    mailer: Mailer | None = None,
) -> int:
    """Send a one-time code to prove the inbox. Does not open a session."""
    _require_password_mode()
    otp_service._check_rate_limit(email=email, client_ip=client_ip, key_prefix="cf-account:")
    code = _generate_code()
    now = datetime.now(UTC)
    session.execute(
        update(EmailOtp)
        .where(
            EmailOtp.email == email,
            EmailOtp.provider == CF_PASSWORD_PROVIDER,
            EmailOtp.consumed_at.is_(None),
        )
        .values(consumed_at=now),
    )
    session.add(
        EmailOtp(
            email=email,
            provider=CF_PASSWORD_PROVIDER,
            code_hash=otp_service._hash_code(code),
            expires_at=now + timedelta(seconds=settings.otp_ttl_seconds),
        ),
    )
    session.commit()
    stored_locale = session.scalar(select(User.ui_locale).where(User.email == email))
    (mailer or get_mailer()).send_otp(to_email=email, code=code, locale=stored_locale)
    return settings.otp_ttl_seconds


def set_password(
    session: Session,
    *,
    email: str,
    code: str,
    password: str,
) -> dict[str, str | int]:
    """Store a Career Forge password after the inbox code. Same user if the email exists."""
    _require_password_mode()
    if len(password) < PASSWORD_MIN_LENGTH:
        raise BadRequestError("password must be at least 8 characters")
    _consume_code(session, email=email, code=code)
    user = _user_for_email(session, email)
    user.password_hash = hash_password(password)
    session.commit()
    assert user.external_id
    return _token_payload(user.external_id)


def sign_in(
    session: Session,
    *,
    email: str,
    password: str,
    client_ip: str,
) -> dict[str, str | int]:
    """Open a session with the stored Career Forge password."""
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
    return _token_payload(user.external_id)
