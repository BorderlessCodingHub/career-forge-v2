"""Learner identity entry method (CAR-102 / ADR-008).

``IDENTITY_METHOD`` wins when set. Otherwise ``IDENTITY_EMAIL_OTP`` maps
``true`` → ``email_otp`` and ``false`` → ``pilot_enter``. Never treat the
legacy flag as Borderless password.
"""

from __future__ import annotations

from typing import Literal

from career_forge.errors import GoneError

IdentityMethod = Literal["email_otp", "pilot_enter", "borderless_password"]

EMAIL_OTP: IdentityMethod = "email_otp"
PILOT_ENTER: IdentityMethod = "pilot_enter"
BORDERLESS_PASSWORD: IdentityMethod = "borderless_password"
IDENTITY_METHODS: frozenset[str] = frozenset(
    {EMAIL_OTP, PILOT_ENTER, BORDERLESS_PASSWORD}
)


def resolve_identity_method(
    *,
    identity_method: str,
    identity_email_otp: bool,
) -> IdentityMethod:
    """Return the active learner entry method."""
    raw = identity_method.strip().lower()
    if raw:
        if raw not in IDENTITY_METHODS:
            allowed = ", ".join(sorted(IDENTITY_METHODS))
            raise ValueError(
                f"IDENTITY_METHOD must be one of {allowed} (or empty); got {identity_method!r}"
            )
        return raw  # type: ignore[return-value]
    return EMAIL_OTP if identity_email_otp else PILOT_ENTER


LEARNER_OTP_GONE_MESSAGE = "Learner OTP is gone — use password signin"


def raise_if_learner_otp_gone(method: IdentityMethod) -> None:
    """CAR-105 — learner OTP/pilot are unavailable in Borderless password mode."""
    if method == BORDERLESS_PASSWORD:
        raise GoneError(LEARNER_OTP_GONE_MESSAGE)


def email_otp_required_for_legacy_clients(method: IdentityMethod) -> bool:
    """CAR-100 ``email_otp_required``: OTP UI unless pilot-enter freeze.

    ``borderless_password`` stays true so old IdentityGate shows OTP (now 410)
    instead of falling through to ``pilot/enter`` until CAR-106.
    """
    return method != PILOT_ENTER
