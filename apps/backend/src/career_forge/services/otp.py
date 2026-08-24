"""Email OTP request / verify with promote + conflict (CAR-44)."""

from __future__ import annotations

import hashlib
import secrets
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import TypedDict

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.email_otp import EMAIL_OTP_PROVIDER, EmailOtp
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import (
    BadRequestError,
    EmailOwnedConflictError,
    RateLimitedError,
)
from career_forge.services.mailer import Mailer, get_mailer
from career_forge.services.membership import MembershipClient, apply_membership_label


class OtpTokenPayload(TypedDict):
    access_token: str
    token_type: str
    external_id: str
    provider: str
    expires_in: int


class OtpPromoteResult(TypedDict):
    status: str
    access_token: str
    token_type: str
    external_id: str
    provider: str
    expires_in: int


# In-memory sliding windows: key → list of request timestamps (monotonic).
_rate_buckets: dict[str, list[float]] = defaultdict(list)


def reset_otp_rate_limiter() -> None:
    """Clear rate-limit buckets (tests)."""
    _rate_buckets.clear()


def _generate_otp_code() -> str:
    """Return a cryptographically random 6-digit code (tests may monkeypatch)."""
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


def _expires_in_seconds() -> int:
    return settings.jwt_anon_ttl_days * 24 * 3600


def _token_payload(external_id: str) -> OtpTokenPayload:
    token = get_auth_provider().mint_email(external_id)
    return {
        "access_token": token,
        "token_type": "bearer",
        "external_id": external_id,
        "provider": EMAIL_PROVIDER,
        "expires_in": _expires_in_seconds(),
    }


def _check_rate_limit(*, email: str, client_ip: str) -> None:
    now = time.monotonic()
    window = float(settings.otp_rate_limit_window_seconds)

    def _hit(key: str, limit: int) -> None:
        bucket = _rate_buckets[key]
        cutoff = now - window
        kept = [ts for ts in bucket if ts >= cutoff]
        _rate_buckets[key] = kept
        if len(kept) >= limit:
            raise RateLimitedError("too many OTP requests — try again later")
        kept.append(now)

    _hit(f"email:{email}", settings.otp_rate_limit_per_email)
    _hit(f"ip:{client_ip}", settings.otp_rate_limit_per_ip)


def request_otp(
    session: Session,
    *,
    email: str,
    client_ip: str,
    mailer: Mailer | None = None,
) -> int:
    """Store a hashed OTP for ``email`` and deliver via mailer. Returns TTL seconds."""
    _check_rate_limit(email=email, client_ip=client_ip)

    code = _generate_otp_code()
    code_hash = _hash_code(code)
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=settings.otp_ttl_seconds)

    session.execute(
        update(EmailOtp)
        .where(
            EmailOtp.email == email,
            EmailOtp.provider == EMAIL_OTP_PROVIDER,
            EmailOtp.consumed_at.is_(None),
        )
        .values(consumed_at=now),
    )
    session.add(
        EmailOtp(
            email=email,
            provider=EMAIL_OTP_PROVIDER,
            code_hash=code_hash,
            expires_at=expires_at,
        ),
    )
    session.commit()

    (mailer or get_mailer()).send_otp(to_email=email, code=code)
    return settings.otp_ttl_seconds


def verify_otp(
    session: Session,
    *,
    external_id: str,
    email: str,
    code: str,
    membership: MembershipClient | None = None,
) -> OtpPromoteResult:
    """Validate OTP then promote anon or raise conflict for chooser.

    Successful verify (promote or owned-email chooser) re-resolves membership.
    """
    now = datetime.now(UTC)
    row = session.scalar(
        select(EmailOtp)
        .where(
            EmailOtp.email == email,
            EmailOtp.provider == EMAIL_OTP_PROVIDER,
            EmailOtp.consumed_at.is_(None),
        )
        .order_by(EmailOtp.created_at.desc()),
    )
    if row is None:
        raise BadRequestError("invalid or expired code")
    if row.expires_at <= now:
        row.consumed_at = now
        session.commit()
        raise BadRequestError("invalid or expired code")
    if row.code_hash != _hash_code(code.strip()):
        raise BadRequestError("invalid or expired code")

    row.consumed_at = now
    session.flush()

    current = ensure_user(session, external_id)
    owner = session.scalar(
        select(User).where(User.email == email, User.id != current.id),
    )

    if owner is not None:
        if not owner.external_id:
            raise BadRequestError("email account is missing external_id")
        apply_membership_label(owner, email, membership)
        session.commit()
        raise EmailOwnedConflictError(_token_payload(owner.external_id))

    current.email = email
    apply_membership_label(current, email, membership)
    session.commit()

    payload = _token_payload(external_id)
    return {
        "status": "promoted",
        "access_token": payload["access_token"],
        "token_type": payload["token_type"],
        "external_id": payload["external_id"],
        "provider": payload["provider"],
        "expires_in": payload["expires_in"],
    }
