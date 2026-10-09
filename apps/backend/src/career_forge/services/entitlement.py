"""Product entitlement — paywall before diagnosis and forge for unpaid external (CAR-57).

OTP / ``pilot_enter``: BASE/PSP membership skips Stripe. Paid/pilot-listed
``external`` skips too.

Password mode (``IDENTITY_METHOD=borderless_password``, CAR-128): a linked
learner is included only when the Borderless profile says BASE or PSP, or the
Operator desk overrides that label. ``borderless_user_id`` alone does not
include. Unpaid ``external`` is paywalled. Active Stripe, ``billing_entitled``,
and the pilot list still allow. The lifetime forge is CAR-130.

Cost caps (FORGE_CAP_PER_USER_MONTH) still apply after this gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from career_forge.ai.run import GraphRun
from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmail
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import PaywallError
from career_forge.identity_method import BORDERLESS_PASSWORD, EMAIL_OTP, IdentityMethod
from career_forge.services.borderless_profile import sync_borderless_membership
from career_forge.services.cost_guard import resolve_exclude_reason

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"

EntitlementReason = Literal[
    "ok", "paywall", "membership", "billing", "excluded", "borderless"
]
ACTIVE_STRIPE_SUBSCRIPTION_STATUSES = frozenset({"active", "trialing", "past_due"})


@dataclass(frozen=True)
class EntitlementDecision:
    allowed: bool
    reason: EntitlementReason
    membership_label: str = "external"
    membership_entitled: bool = False
    billing_entitled: bool = False
    free_forges_used: int = 0


def stripe_subscription_is_active(status: str | None) -> bool:
    return status in ACTIVE_STRIPE_SUBSCRIPTION_STATUSES


def _usable_email(email: str | None) -> str | None:
    if not email or email.endswith(_DEMO_EMAIL_SUFFIX):
        return None
    return email.strip().lower()


def _pilot_email_is_listed(session: Session, email: str | None) -> bool:
    usable = _usable_email(email)
    return usable is not None and session.get(BillingPilotEmail, usable) is not None


def _is_billed(
    *,
    billing_entitled: bool,
    email: str | None,
    pilot_email_listed: bool,
    stripe_subscription_status: str | None,
) -> bool:
    return (
        stripe_subscription_is_active(stripe_subscription_status)
        or billing_entitled
        or (_usable_email(email) is not None and pilot_email_listed)
    )


def evaluate_entitlement(
    *,
    user_id: str,
    membership_label: str,
    membership_entitled: bool,
    billing_entitled: bool,
    email: str | None,
    forge_count: int,
    run_input: dict | None = None,
    pilot_email_listed: bool = False,
    stripe_subscription_status: str | None = None,
    identity_method: IdentityMethod = EMAIL_OTP,
) -> EntitlementDecision:
    """Pure decision: allow this forge, or paywall the caller."""
    if resolve_exclude_reason(user_id, run_input) is not None:
        return EntitlementDecision(
            allowed=True,
            reason="excluded",
            membership_label=membership_label,
            membership_entitled=membership_entitled,
            billing_entitled=billing_entitled,
            free_forges_used=forge_count,
        )

    if identity_method == BORDERLESS_PASSWORD:
        billed = _is_billed(
            billing_entitled=billing_entitled,
            email=email,
            pilot_email_listed=pilot_email_listed,
            stripe_subscription_status=stripe_subscription_status,
        )
        if membership_entitled and membership_label in {"base", "psp"}:
            return EntitlementDecision(
                allowed=True,
                reason="membership",
                membership_label=membership_label,
                membership_entitled=True,
                billing_entitled=billed,
                free_forges_used=forge_count,
            )
        if billed:
            return EntitlementDecision(
                allowed=True,
                reason="billing",
                membership_label=membership_label,
                membership_entitled=False,
                billing_entitled=True,
                free_forges_used=forge_count,
            )
        return EntitlementDecision(
            allowed=False,
            reason="paywall",
            membership_label=membership_label,
            membership_entitled=False,
            billing_entitled=False,
            free_forges_used=forge_count,
        )

    billed = _is_billed(
        billing_entitled=billing_entitled,
        email=email,
        pilot_email_listed=pilot_email_listed,
        stripe_subscription_status=stripe_subscription_status,
    )

    if membership_entitled and membership_label in {"base", "psp"}:
        return EntitlementDecision(
            allowed=True,
            reason="membership",
            membership_label=membership_label,
            membership_entitled=True,
            billing_entitled=billed,
            free_forges_used=forge_count,
        )
    if billed:
        return EntitlementDecision(
            allowed=True,
            reason="billing",
            membership_label=membership_label,
            membership_entitled=membership_entitled,
            billing_entitled=True,
            free_forges_used=forge_count,
        )
    return EntitlementDecision(
        allowed=False,
        reason="paywall",
        membership_label=membership_label,
        membership_entitled=membership_entitled,
        billing_entitled=False,
        free_forges_used=forge_count,
    )


def stripe_configured() -> bool:
    return bool(
        settings.stripe_secret_key.strip()
        and settings.stripe_webhook_secret.strip()
        and settings.stripe_price_id.strip()
    )


def _password_mode_label(user: User) -> tuple[str, bool]:
    """Included label for password mode: desk override, else a linked profile read."""
    override = user.operator_membership_label
    if override in {"base", "psp"}:
        return override, True
    linked = bool((user.borderless_user_id or "").strip())
    label = user.membership_label
    if linked and user.membership_entitled and label in {"base", "psp"}:
        return label, True
    return label, False


def _entitlement_for_user(
    session: Session,
    external_id: str,
    *,
    forge_count: int = 0,
    run_input: dict | None = None,
) -> EntitlementDecision:
    user = ensure_user(session, external_id)
    if user.borderless_access_token:
        sync_borderless_membership(user)
        session.commit()
    identity_method = settings.resolved_identity_method()
    if identity_method == BORDERLESS_PASSWORD:
        membership_label, membership_entitled = _password_mode_label(user)
    else:
        membership_label = user.membership_label
        membership_entitled = bool(user.membership_entitled)
    return evaluate_entitlement(
        user_id=external_id,
        membership_label=membership_label,
        membership_entitled=membership_entitled,
        billing_entitled=bool(user.billing_entitled),
        stripe_subscription_status=user.stripe_subscription_status,
        email=user.email,
        forge_count=forge_count,
        run_input=run_input,
        pilot_email_listed=_pilot_email_is_listed(session, user.email),
        identity_method=identity_method,
    )


def require_product_entitlement(
    session: Session,
    external_id: str,
    *,
    forge_count: int = 0,
    run_input: dict | None = None,
) -> EntitlementDecision:
    """Raise ``PaywallError`` when unpaid ``external`` starts diagnosis or forge."""
    decision = _entitlement_for_user(
        session,
        external_id,
        forge_count=forge_count,
        run_input=run_input,
    )
    if not decision.allowed:
        raise PaywallError(checkout_available=stripe_configured())
    return decision


def require_forge_entitlement(
    session: Session,
    run: GraphRun,
    *,
    forge_count: int,
) -> EntitlementDecision:
    """Raise ``PaywallError`` when unpaid ``external`` starts a forge."""
    return require_product_entitlement(
        session,
        run.user_id,
        forge_count=forge_count,
        run_input=run.input if isinstance(run.input, dict) else None,
    )


def require_diagnosis_entitlement(session: Session, external_id: str) -> EntitlementDecision:
    """Raise ``PaywallError`` when unpaid ``external`` starts diagnosis."""
    return require_product_entitlement(session, external_id)
