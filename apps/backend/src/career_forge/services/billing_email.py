"""Billing email — one accepted send per failed-charge spell (CAR-126).

Continuity does not read or write this state, and this module does not
read or write a quiet stretch. Stripe Dashboard failed-payment emails
stay off; Career Forge sends this letter.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from typing import Any, Literal, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.config import settings
from career_forge.db.models.user import User

logger = logging.getLogger(__name__)

CARD_PATH = "/billing/card"
NoticeAction = Literal["send", "close", "ignore"]


@dataclass(frozen=True)
class BillingNotice:
    action: NoticeAction
    customer_id: str | None = None
    status: str = ""
    previous_status: str | None = None


@dataclass(frozen=True)
class FailedCharge:
    email: str | None
    entitled: bool
    external: bool
    status: str
    previous_status: str | None
    spell_open: bool


_RENEWAL_PREVIOUS = frozenset({"active", "trialing"})
_NOT_A_RENEWAL = frozenset({"past_due", "incomplete", "incomplete_expired"})
_SPELL_ENDS = frozenset({"active", "canceled", "unpaid", "incomplete_expired"})


class BillingMailer(Protocol):
    def send_billing(self, *, to_email: str, subject: str, text: str) -> None: ...


def billing_notice(event: dict[str, Any]) -> BillingNotice:
    """What a verified Stripe event means for the failed-charge spell.

    Mail when a renewal enters ``past_due`` (from active or trialing, or
    when the previous status was not on the event). A retry that is already
    ``past_due``, and a first checkout that never left ``incomplete``, do
    not. A later paid invoice, a return to ``active``, or a status that
    ends entitlement closes the spell without a letter.
    """
    event_type = event.get("type")
    data = event.get("data")
    if not isinstance(event_type, str) or not isinstance(data, dict):
        return BillingNotice("ignore")
    obj = data.get("object")
    if not isinstance(obj, dict):
        return BillingNotice("ignore")
    customer = obj.get("customer") if isinstance(obj.get("customer"), str) else None

    if event_type == "invoice.paid":
        return BillingNotice("close", customer_id=customer)
    if event_type == "customer.subscription.deleted":
        return BillingNotice("close", customer_id=customer)
    if event_type != "customer.subscription.updated":
        return BillingNotice("ignore", customer_id=customer)

    status = obj.get("status") if isinstance(obj.get("status"), str) else ""
    previous = _previous_status(data)
    if status == "past_due":
        if previous in _NOT_A_RENEWAL:
            return BillingNotice(
                "ignore",
                customer_id=customer,
                status=status,
                previous_status=previous,
            )
        return BillingNotice("send", customer_id=customer, status=status, previous_status=previous)
    if status in _SPELL_ENDS:
        return BillingNotice("close", customer_id=customer, status=status, previous_status=previous)
    return BillingNotice("ignore", customer_id=customer, status=status, previous_status=previous)


def spell_should_send(charge: FailedCharge) -> bool:
    email = (charge.email or "").strip()
    if not email or charge.spell_open or not charge.entitled or not charge.external:
        return False
    if charge.status != "past_due":
        return False
    if charge.previous_status in _NOT_A_RENEWAL:
        return False
    if charge.previous_status is not None and charge.previous_status not in _RENEWAL_PREVIOUS:
        return False
    return True


def billing_message(frontend_url: str) -> tuple[str, str, str]:
    """Subject, body, and the Career Forge card URL. No opt-out."""
    url = f"{frontend_url.rstrip('/')}{CARD_PATH}"
    subject = "A charge for Career Forge failed"
    text = (
        "A charge for Career Forge failed. "
        "You can keep using Career Forge. "
        f"This link updates your card:\n\n{url}\n"
    )
    return subject, text, url


def portal_return_url(*, has_roadmap: bool, frontend_url: str) -> str:
    """After the Portal, the Roadmap the product already opens, or product entry."""
    base = frontend_url.rstrip("/")
    if has_roadmap:
        return f"{base}/roadmap"
    return f"{base}/"


def try_send(
    charge: FailedCharge,
    mailer: BillingMailer,
    *,
    frontend_url: str,
) -> tuple[FailedCharge, bool]:
    """Send one letter. A rejected send leaves the spell unspent."""
    if not spell_should_send(charge):
        raise ValueError("failed-charge spell should not send")
    email = (charge.email or "").strip()
    subject, text, _url = billing_message(frontend_url)
    try:
        mailer.send_billing(to_email=email, subject=subject, text=text)
    except Exception:
        logger.warning("billing email rejected for %s", email, exc_info=True)
        return charge, False
    return replace(charge, spell_open=True), True


def apply_billing_email(
    session: Session,
    event: dict[str, Any],
    mailer: BillingMailer,
    *,
    frontend_url: str | None = None,
) -> bool:
    """Apply one notice. Returns True when a send was rejected.

    Call after entitlement has been persisted for the same event. Does not
    commit. Does not stamp Roadmap presence.
    """
    notice = billing_notice(event)
    if notice.action == "ignore" or not notice.customer_id:
        return False
    user = session.scalar(
        select(User).where(User.stripe_customer_id == notice.customer_id).with_for_update()
    )
    if user is None:
        return False
    if notice.action == "close":
        user.billing_email_spell_open = False
        return False

    charge = FailedCharge(
        email=user.email,
        entitled=bool(user.billing_entitled),
        external=user.membership_label == "external",
        status=notice.status,
        previous_status=notice.previous_status,
        spell_open=bool(user.billing_email_spell_open),
    )
    if not spell_should_send(charge):
        return False
    origin = frontend_url if frontend_url is not None else settings.frontend_url
    updated, accepted = try_send(charge, mailer, frontend_url=origin)
    if not accepted:
        return True
    user.billing_email_spell_open = updated.spell_open
    return False


def _previous_status(data: dict[str, Any]) -> str | None:
    previous = data.get("previous_attributes")
    if not isinstance(previous, dict):
        return None
    status = previous.get("status")
    if isinstance(status, str) and status:
        return status
    return None
