"""Product entitlement — one forge, then the subscription (CAR-130).

External (FREE, no Borderless account, or a missing profile) may start one
forge in the life of the account, and only when no forge on that account has
been completed. Starting it spends the allowance. Diagnosis may be repeated
until that start.

BASE and PSP skip Stripe and may complete two forges in a UTC month. A
subscribed external sits outside that ceiling. The monthly API budget still
applies after this gate.

Password mode includes a linked learner only when the profile says BASE or
PSP, or the Operator desk overrides that label. ``borderless_user_id`` alone
does not include.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy.orm import Session

from career_forge.ai.run import ForgeRunStamp, GraphRun, get_graph_run_store
from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmail
from career_forge.db.models.user import User
from career_forge.db.repositories.user import ensure_user, get_by_external_id
from career_forge.errors import MonthlyForgeCeilingError, PaywallError
from career_forge.identity_method import BORDERLESS_PASSWORD, EMAIL_OTP, IdentityMethod
from career_forge.services.borderless_profile import sync_borderless_membership
from career_forge.services.cost_guard import (
    FORGE_GRAPH_NAME,
    current_year_month,
    get_cost_guard,
    resolve_exclude_reason,
)

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"
INCLUDED_MONTHLY_COMPLETED_FORGES = 2

EntitlementReason = Literal[
    "ok",
    "paywall",
    "membership",
    "billing",
    "excluded",
    "borderless",
    "allowance",
    "monthly_ceiling",
]
ACTIVE_STRIPE_SUBSCRIPTION_STATUSES = frozenset({"active", "trialing", "past_due"})


@dataclass(frozen=True)
class ForgeHistory:
    """What this account has already forged.

    ``completed_any`` spends the lifetime allowance, including a forge completed
    as BASE or PSP. ``external_start`` is a forge that started while the learner
    was external, including one that failed or was left. ``completed_this_utc_month``
    is the included-program ceiling.
    """

    completed_any: bool = False
    external_start: bool = False
    completed_this_utc_month: int = 0

    @property
    def lifetime_spent(self) -> bool:
        return self.completed_any or self.external_start


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
    forge_history: ForgeHistory | None = None,
) -> EntitlementDecision:
    """Pure decision: allow this diagnosis or forge, paywall, or monthly ceiling.

    ``identity_method`` does not change the allowance. Password mode resolves
    the included label before this call; a Borderless id alone is not included.
    ``forge_count`` is retained for callers and is not the allowance.
    """
    history = forge_history or ForgeHistory()
    if resolve_exclude_reason(user_id, run_input) is not None:
        return EntitlementDecision(
            allowed=True,
            reason="excluded",
            membership_label=membership_label,
            membership_entitled=membership_entitled,
            billing_entitled=billing_entitled,
            free_forges_used=1 if history.lifetime_spent else 0,
        )

    billed = _is_billed(
        billing_entitled=billing_entitled,
        email=email,
        pilot_email_listed=pilot_email_listed,
        stripe_subscription_status=stripe_subscription_status,
    )
    included = membership_entitled and membership_label in {"base", "psp"}
    used = 1 if history.lifetime_spent else 0

    if included:
        if history.completed_this_utc_month >= INCLUDED_MONTHLY_COMPLETED_FORGES:
            return EntitlementDecision(
                allowed=False,
                reason="monthly_ceiling",
                membership_label=membership_label,
                membership_entitled=True,
                billing_entitled=billed,
                free_forges_used=used,
            )
        return EntitlementDecision(
            allowed=True,
            reason="membership",
            membership_label=membership_label,
            membership_entitled=True,
            billing_entitled=billed,
            free_forges_used=used,
        )
    if billed:
        return EntitlementDecision(
            allowed=True,
            reason="billing",
            membership_label=membership_label,
            membership_entitled=membership_entitled,
            billing_entitled=True,
            free_forges_used=used,
        )
    if history.lifetime_spent:
        return EntitlementDecision(
            allowed=False,
            reason="paywall",
            membership_label=membership_label,
            membership_entitled=False,
            billing_entitled=False,
            free_forges_used=used,
        )
    return EntitlementDecision(
        allowed=True,
        reason="allowance",
        membership_label=membership_label,
        membership_entitled=False,
        billing_entitled=False,
        free_forges_used=0,
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


def _occupies_included_month(run: ForgeRunStamp, month: str) -> bool:
    """A forge uses one of the two BASE/PSP slots when it can still complete.

    Failed forges do not. A completion counts in its UTC month. A forge that
    has started and not finished counts in the month it started, so a third
    start cannot slip through before the first two finish.
    """
    if run.status == "failed":
        return False
    if run.status == "completed":
        when = run.completed_at or run.created_at
    else:
        when = run.created_at
    return current_year_month(when) == month


def forge_history_for(user: User, *, now: datetime | None = None) -> ForgeHistory:
    """Completed forges spend the allowance. An external start spends it too."""
    stamp = now or datetime.now(UTC)
    month = current_year_month(stamp)
    external_id = user.external_id or ""
    runs = get_graph_run_store().forge_stamps_for_user(
        external_id, graph_name=FORGE_GRAPH_NAME
    )
    completed_this_month = 0
    completed_any = False
    for run in runs:
        if run.status == "completed":
            completed_any = True
        if _occupies_included_month(run, month):
            completed_this_month += 1
    return ForgeHistory(
        completed_any=completed_any,
        external_start=user.lifetime_forge_started_at is not None,
        completed_this_utc_month=completed_this_month,
    )


def _entitlement_for_user(
    session: Session,
    external_id: str,
    *,
    forge_count: int = 0,
    run_input: dict | None = None,
) -> EntitlementDecision:
    user = ensure_user(session, external_id)
    identity_method = settings.resolved_identity_method()
    if identity_method == BORDERLESS_PASSWORD and user.borderless_access_token:
        sync_borderless_membership(user)
        session.commit()
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
        forge_history=forge_history_for(user),
    )


def _raise_if_blocked(decision: EntitlementDecision) -> EntitlementDecision:
    if decision.allowed:
        return decision
    if decision.reason == "monthly_ceiling":
        raise MonthlyForgeCeilingError()
    raise PaywallError(checkout_available=stripe_configured())


def require_product_entitlement(
    session: Session,
    external_id: str,
    *,
    forge_count: int = 0,
    run_input: dict | None = None,
) -> EntitlementDecision:
    """Raise when diagnosis or a forge must not start."""
    decision = _entitlement_for_user(
        session,
        external_id,
        forge_count=forge_count,
        run_input=run_input,
    )
    return _raise_if_blocked(decision)


def require_forge_entitlement(
    session: Session,
    run: GraphRun,
    *,
    forge_count: int,
) -> EntitlementDecision:
    """Raise when this account may not start a forge."""
    return require_product_entitlement(
        session,
        run.user_id,
        forge_count=forge_count,
        run_input=run.input if isinstance(run.input, dict) else None,
    )


def require_diagnosis_entitlement(session: Session, external_id: str) -> EntitlementDecision:
    """Raise when this account may not start diagnosis.

    The BASE/PSP monthly refusal is the third forge, not another diagnosis.
    """
    decision = _entitlement_for_user(session, external_id)
    if decision.reason == "monthly_ceiling":
        return EntitlementDecision(
            allowed=True,
            reason="membership",
            membership_label=decision.membership_label,
            membership_entitled=True,
            billing_entitled=decision.billing_entitled,
            free_forges_used=decision.free_forges_used,
        )
    return _raise_if_blocked(decision)


def authorize_forge_start(session: Session, run: GraphRun) -> EntitlementDecision:
    """Allow this forge, then spend the external allowance after the cost gate."""
    decision = require_forge_entitlement(session, run, forge_count=0)
    get_cost_guard().check(run, skip_per_user_cap=decision.reason == "billing")
    if decision.reason == "allowance":
        record_lifetime_forge_start(session, run.user_id)
    return decision


def record_lifetime_forge_start(session: Session, external_id: str) -> None:
    """Spend the one external forge at start, including failure or leaving.

    A second start that lost the race raises the paywall instead of saving
    another forge. Cancel does not clear this timestamp.
    """
    user = ensure_user(session, external_id)
    locked = session.get(User, user.id, with_for_update=True)
    if locked is None:
        raise PaywallError(checkout_available=stripe_configured())
    history = forge_history_for(locked)
    if history.lifetime_spent:
        session.rollback()
        raise PaywallError(checkout_available=stripe_configured())
    locked.lifetime_forge_started_at = datetime.now(UTC)
    session.commit()


def profile_checkout_available(session: Session, external_id: str) -> bool:
    """Checkout is offered once the lifetime forge is spent and Stripe is live.

    Uses the stored membership label. It does not read Borderless and does not
    create a user.
    """
    if not stripe_configured():
        return False
    user = get_by_external_id(session, external_id)
    if user is None:
        return False
    identity_method = settings.resolved_identity_method()
    if identity_method == BORDERLESS_PASSWORD:
        membership_label, membership_entitled = _password_mode_label(user)
    else:
        membership_label = user.membership_label
        membership_entitled = bool(user.membership_entitled)
    decision = evaluate_entitlement(
        user_id=external_id,
        membership_label=membership_label,
        membership_entitled=membership_entitled,
        billing_entitled=bool(user.billing_entitled),
        stripe_subscription_status=user.stripe_subscription_status,
        email=user.email,
        forge_count=0,
        pilot_email_listed=_pilot_email_is_listed(session, user.email),
        identity_method=identity_method,
        forge_history=forge_history_for(user),
    )
    return (not decision.allowed) and decision.reason == "paywall"
