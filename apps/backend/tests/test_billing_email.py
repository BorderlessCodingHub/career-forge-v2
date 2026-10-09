"""Billing email — one accepted send per failed-charge spell (CAR-126).

Seam: billing_notice / spell_should_send / billing_message / try_send.
A Continuity quiet stretch is a different track.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from career_forge.services.billing_email import (
    FailedCharge,
    billing_message,
    billing_notice,
    portal_return_url,
    spell_should_send,
    try_send,
)


def _charge(**overrides: object) -> FailedCharge:
    base = FailedCharge(
        email="ana@example.com",
        entitled=True,
        external=True,
        status="past_due",
        previous_status="active",
        spell_open=False,
    )
    return replace(base, **overrides)  # type: ignore[arg-type]


def test_entering_past_due_opens_one_spell_while_entitlement_holds() -> None:
    notice = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "past_due"},
                "previous_attributes": {"status": "active"},
            },
        }
    )

    assert notice.action == "send"
    assert notice.customer_id == "cus_1"
    assert spell_should_send(_charge()) is True


def test_a_retry_inside_the_spell_does_not_send_again() -> None:
    notice = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "past_due"},
                "previous_attributes": {"status": "past_due"},
            },
        }
    )

    assert notice.action == "ignore"
    assert spell_should_send(_charge(previous_status="past_due")) is False
    assert spell_should_send(_charge(spell_open=True)) is False


def test_a_failed_invoice_does_not_open_a_spell_by_itself() -> None:
    """Retries, a first checkout that never succeeds, and a charge that
    removes entitlement in the same moment are not this email."""
    for reason in ("subscription_cycle", "subscription_create"):
        notice = billing_notice(
            {
                "type": "invoice.payment_failed",
                "data": {
                    "object": {
                        "customer": "cus_1",
                        "billing_reason": reason,
                        "paid": False,
                    }
                },
            }
        )
        assert notice.action == "ignore"


def test_leaving_grace_or_a_paid_invoice_closes_the_spell_without_mail() -> None:
    canceled = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "canceled"},
                "previous_attributes": {"status": "past_due"},
            },
        }
    )
    unpaid = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "unpaid"},
                "previous_attributes": {"status": "active"},
            },
        }
    )
    paid = billing_notice(
        {
            "type": "invoice.paid",
            "data": {"object": {"customer": "cus_1", "billing_reason": "subscription_cycle"}},
        }
    )
    deleted = billing_notice(
        {
            "type": "customer.subscription.deleted",
            "data": {"object": {"customer": "cus_1", "status": "canceled"}},
        }
    )
    recovered = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "active"},
                "previous_attributes": {"status": "past_due"},
            },
        }
    )

    assert canceled.action == "close"
    assert unpaid.action == "close"
    assert paid.action == "close"
    assert deleted.action == "close"
    assert recovered.action == "close"
    assert spell_should_send(_charge(status="canceled", entitled=False)) is False
    assert spell_should_send(_charge(status="unpaid", entitled=False)) is False
    assert spell_should_send(_charge(entitled=False)) is False
    assert spell_should_send(_charge(external=False)) is False
    assert spell_should_send(_charge(email=None)) is False
    assert spell_should_send(_charge(email="  ")) is False
    assert spell_should_send(_charge(previous_status="incomplete")) is False


def test_a_first_checkout_that_never_succeeds_does_not_send() -> None:
    notice = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "past_due"},
                "previous_attributes": {"status": "incomplete"},
            },
        }
    )
    unrelated = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"customer": "cus_1", "status": "incomplete"},
                "previous_attributes": {"status": "incomplete"},
            },
        }
    )

    assert notice.action == "ignore"
    assert unrelated.action == "ignore"


def test_missing_previous_status_still_opens_the_spell_once() -> None:
    notice = billing_notice(
        {
            "type": "customer.subscription.updated",
            "data": {"object": {"customer": "cus_1", "status": "past_due"}},
        }
    )

    assert notice.action == "send"
    assert spell_should_send(_charge(previous_status=None)) is True


def test_portal_returns_to_the_roadmap_or_to_product_entry() -> None:
    origin = "http://localhost:3300/career-forge"
    assert portal_return_url(has_roadmap=True, frontend_url=origin) == f"{origin}/roadmap"
    assert portal_return_url(has_roadmap=False, frontend_url=f"{origin}/") == f"{origin}/"


def test_unreviewed_locale_keeps_the_english_billing_letter() -> None:
    subject, text, url = billing_message(
        "http://localhost:3300/career-forge/",
        locale="pt-BR",
    )

    assert subject == "A charge for Career Forge failed"
    assert "You can keep using Career Forge." in text
    assert url == "http://localhost:3300/career-forge/billing/card"


def test_letter_says_the_charge_failed_and_the_card_link_is_ours() -> None:
    subject, text, url = billing_message("http://localhost:3300/career-forge/")
    folded = f"{subject}\n{text}".lower()

    assert url == "http://localhost:3300/career-forge/billing/card"
    assert url in text
    assert "charge" in folded and "failed" in folded
    assert "keep using career forge" in folded
    assert "card" in folded
    assert "behind" not in folded
    assert "next node" not in folded
    assert "access ended" not in folded
    assert "billing.stripe.com" not in folded
    assert "unsubscribe" not in folded


class _Mailer:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str, str]] = []

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
        if self.fail:
            raise RuntimeError("mailer down")
        self.sent.append((to_email, subject, text))


def test_rejected_send_does_not_spend_the_spell() -> None:
    mailer = _Mailer(fail=True)

    updated, accepted = try_send(
        _charge(),
        mailer,
        frontend_url="http://localhost:3300/career-forge",
    )

    assert accepted is False
    assert updated.spell_open is False


def test_reviewed_locale_changes_the_letter_and_still_opens_the_spell(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "career_forge.services.learner_mail.REVIEWED_LOCALES",
        frozenset({"en", "pt-BR"}),
    )
    mailer = _Mailer()

    updated, accepted = try_send(
        _charge(),
        mailer,
        frontend_url="http://localhost:3300/career-forge",
        locale="pt-BR",
    )

    assert accepted is True
    assert updated.spell_open is True
    assert mailer.sent[0][1] == "Uma cobrança do Career Forge falhou"
    assert "continuar usando o Career Forge" in mailer.sent[0][2]


def test_accepted_send_opens_the_spell() -> None:
    mailer = _Mailer()

    updated, accepted = try_send(
        _charge(),
        mailer,
        frontend_url="http://localhost:3300/career-forge",
    )

    assert accepted is True
    assert updated.spell_open is True
    assert mailer.sent[0][0] == "ana@example.com"
    assert "http://localhost:3300/career-forge/billing/card" in mailer.sent[0][2]


def test_try_send_refuses_a_charge_that_should_not_mail() -> None:
    with pytest.raises(ValueError):
        try_send(
            _charge(status="canceled", entitled=False),
            _Mailer(),
            frontend_url="http://localhost:3300/career-forge",
        )
