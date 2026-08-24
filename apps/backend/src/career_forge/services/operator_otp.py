"""Operator OTP request / verify — separate namespace from learner Email OTP (CAR-75)."""

from __future__ import annotations

import hashlib
import secrets
import time
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from typing import TypedDict

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import OPERATOR_PROVIDER
from career_forge.auth.operator_session import mint_operator_session_token
from career_forge.config import settings
from career_forge.db.models.email_otp import OPERATOR_OTP_PROVIDER, EmailOtp
from career_forge.db.models.operator import Operator
from career_forge.errors import BadRequestError, ForbiddenError, RateLimitedError
from career_forge.services.mailer import Mailer, get_mailer
from career_forge.services.operator_allowlist import parse_operator_allowlist, upsert_operator_from_allowlist


class OperatorSessionPayload(TypedDict):
    provider: str
    email: str
    operator_id: int
    desk_roles: str
    desks: list[str]
    expires_in: int


# Separate rate-limit namespace from learner OTP.
_rate_buckets: dict[str, list[float]] = defaultdict(list)


def reset_operator_otp_rate_limiter() -> None:
    _rate_buckets.clear()


def _generate_otp_code() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode("utf-8")).hexdigest()


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

    _hit(f"operator:email:{email}", settings.otp_rate_limit_per_email)
    _hit(f"operator:ip:{client_ip}", settings.otp_rate_limit_per_ip)


def request_operator_otp(
    session: Session,
    *,
    email: str,
    client_ip: str,
    mailer: Mailer | None = None,
) -> int:
    """Allowlisted email only — upsert ``operators`` then deliver OTP."""
    allowlist = parse_operator_allowlist(settings.operator_allowlist)
    operator = upsert_operator_from_allowlist(session, email=email, allowlist=allowlist)
    if operator is None:
        raise ForbiddenError(
            "email is not on the Operator allowlist",
            code="operator_not_allowlisted",
        )

    email_key = email.strip().lower()
    _check_rate_limit(email=email_key, client_ip=client_ip)

    code = _generate_otp_code()
    code_hash = _hash_code(code)
    now = datetime.now(UTC)
    expires_at = now + timedelta(seconds=settings.otp_ttl_seconds)

    session.execute(
        update(EmailOtp)
        .where(
            EmailOtp.email == email_key,
            EmailOtp.provider == OPERATOR_OTP_PROVIDER,
            EmailOtp.consumed_at.is_(None),
        )
        .values(consumed_at=now),
    )
    session.add(
        EmailOtp(
            email=email_key,
            provider=OPERATOR_OTP_PROVIDER,
            code_hash=code_hash,
            expires_at=expires_at,
        ),
    )
    session.commit()

    (mailer or get_mailer()).send_operator_otp(to_email=email_key, code=code)
    return settings.otp_ttl_seconds


def verify_operator_otp(
    session: Session,
    *,
    email: str,
    code: str,
) -> tuple[OperatorSessionPayload, str]:
    """Validate Operator OTP and return session payload + signed cookie token."""
    email_key = email.strip().lower()
    now = datetime.now(UTC)
    row = session.scalar(
        select(EmailOtp)
        .where(
            EmailOtp.email == email_key,
            EmailOtp.provider == OPERATOR_OTP_PROVIDER,
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

    operator = session.scalar(select(Operator).where(Operator.email == email_key))
    if operator is None:
        raise BadRequestError("operator seat not found")

    from career_forge.services.operator_allowlist import desks_for_roles

    token = mint_operator_session_token(
        email=operator.email,
        operator_id=operator.id,
        desk_roles=operator.desk_roles,
    )
    expires_in = settings.operator_session_ttl_hours * 3600
    payload: OperatorSessionPayload = {
        "provider": OPERATOR_PROVIDER,
        "email": operator.email,
        "operator_id": operator.id,
        "desk_roles": operator.desk_roles,
        "desks": desks_for_roles(operator.desk_roles),
        "expires_in": expires_in,
    }
    session.commit()
    return payload, token
