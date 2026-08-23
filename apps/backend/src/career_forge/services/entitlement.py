"""Product entitlement — paywall before diagnosis and forge for unpaid external (CAR-57).

BASE/PSP membership skips Stripe. Paid/allowlisted ``external`` skips too.
Cost caps (FORGE_CAP_PER_USER_MONTH) still apply after this gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from career_forge.ai.run import GraphRun
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import PaywallError
from career_forge.services.cost_guard import resolve_exclude_reason

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"

EntitlementReason = Literal["ok", "paywall", "membership", "billing", "excluded"]


@dataclass(frozen=True)
class EntitlementDecision:
    allowed: bool
    reason: EntitlementReason
    membership_label: str = "external"
    membership_entitled: bool = False
    billing_entitled: bool = False
    free_forges_used: int = 0


def parse_billing_allowlist(raw: str) -> set[str]:
    """Parse comma-separated emails. Invalid fragments are skipped."""
    emails: set[str] = set()
    for chunk in raw.split(","):
        email = chunk.strip().lower()
        if "@" not in email or email.startswith("@") or email.endswith("@"):
            continue
        emails.add(email)
    return emails


def _usable_email(email: str | None) -> str | None:
    if not email or email.endswith(_DEMO_EMAIL_SUFFIX):
        return None
    return email.strip().lower()


def evaluate_entitlement(
    *,
    user_id: str,
    membership_label: str,
    membership_entitled: bool,
    billing_entitled: bool,
    email: str | None,
    forge_count: int,
    run_input: dict | None = None,
    billing_allowlist: set[str] | None = None,
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

    allowlist = billing_allowlist or set()
    usable = _usable_email(email)
    billed = billing_entitled or (usable in allowlist if usable else False)

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


def _entitlement_for_user(
    session: Session,
    external_id: str,
    *,
    forge_count: int = 0,
    run_input: dict | None = None,
) -> EntitlementDecision:
    user = ensure_user(session, external_id)
    return evaluate_entitlement(
        user_id=external_id,
        membership_label=user.membership_label,
        membership_entitled=bool(user.membership_entitled),
        billing_entitled=bool(user.billing_entitled),
        email=user.email,
        forge_count=forge_count,
        run_input=run_input,
        billing_allowlist=parse_billing_allowlist(settings.entitlement_billing_allowlist),
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
