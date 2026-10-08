"""Customer Portal session and the failed-charge spell on the webhook (CAR-126)."""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services.billing_email import apply_billing_email
from career_forge.services.stripe_billing import (
    HttpStripeBillingClient,
    apply_stripe_event,
    set_stripe_client,
)


def _sign(secret: str, payload: bytes, timestamp: int) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


class _Mailer:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str, str]] = []

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
        if self.fail:
            raise RuntimeError("mailer down")
        self.sent.append((to_email, subject, text))


def _past_due(customer: str, previous: str) -> dict:
    return {
        "type": "customer.subscription.updated",
        "data": {
            "object": {"id": "sub_spell", "customer": customer, "status": "past_due"},
            "previous_attributes": {"status": previous},
        },
    }


def test_portal_session_asks_stripe_for_a_payment_method_update() -> None:
    seen: dict[str, object] = {}

    def post(path: str, secret: str, fields: dict[str, str], timeout: float) -> str:
        seen["path"] = path
        seen["secret"] = secret
        seen["fields"] = fields
        seen["timeout"] = timeout
        return json.dumps({"url": "https://billing.stripe.com/p/session/test"})

    client = HttpStripeBillingClient(secret_key="sk_test", price_id="price_test", post=post)
    url = client.create_portal_session(
        customer_id="cus_1",
        return_url="http://localhost:3300/career-forge/roadmap",
    )

    assert url == "https://billing.stripe.com/p/session/test"
    assert seen["path"] == "/billing_portal/sessions"
    assert seen["fields"] == {
        "customer": "cus_1",
        "return_url": "http://localhost:3300/career-forge/roadmap",
        "flow_data[type]": "payment_method_update",
    }


def test_past_due_stays_entitled_and_one_letter_covers_the_spell() -> None:
    mailer = _Mailer()
    with SessionLocal() as session:
        user = ensure_user(session, "billing-spell-user")
        user.email = "spell@example.com"
        user.billing_entitled = True
        user.stripe_customer_id = "cus_spell"
        user.stripe_subscription_status = "active"
        user.billing_email_spell_open = False
        user.roadmap_presence_at = None
        user.continuity_accepted_presence_at = None
        session.commit()

        opened = _past_due("cus_spell", "active")
        apply_stripe_event(session, opened)
        rejected = apply_billing_email(
            session,
            opened,
            mailer,
            frontend_url="http://localhost:3300/career-forge",
        )
        session.commit()
        session.refresh(user)

        assert rejected is False
        assert user.billing_entitled is True
        assert user.stripe_subscription_status == "past_due"
        assert user.billing_email_spell_open is True
        assert user.roadmap_presence_at is None
        assert user.continuity_accepted_presence_at is None
        assert len(mailer.sent) == 1
        assert "http://localhost:3300/career-forge/billing/card" in mailer.sent[0][2]

        retry = _past_due("cus_spell", "past_due")
        apply_stripe_event(session, retry)
        apply_billing_email(session, retry, mailer)
        session.commit()
        assert len(mailer.sent) == 1

        apply_billing_email(
            session,
            {
                "type": "invoice.payment_failed",
                "data": {
                    "object": {
                        "customer": "cus_spell",
                        "billing_reason": "subscription_cycle",
                    }
                },
            },
            mailer,
        )
        session.commit()
        assert len(mailer.sent) == 1

        apply_billing_email(
            session,
            {"type": "invoice.paid", "data": {"object": {"customer": "cus_spell"}}},
            mailer,
        )
        session.commit()
        session.refresh(user)
        assert user.billing_email_spell_open is False

        again = _past_due("cus_spell", "active")
        apply_stripe_event(session, again)
        apply_billing_email(session, again, mailer)
        session.commit()
        assert len(mailer.sent) == 2


def test_a_base_member_does_not_get_the_billing_email() -> None:
    mailer = _Mailer()
    with SessionLocal() as session:
        user = ensure_user(session, "billing-base-user")
        user.email = "base@example.com"
        user.membership_label = "base"
        user.billing_entitled = True
        user.stripe_customer_id = "cus_base"
        user.billing_email_spell_open = False
        session.commit()
        event = _past_due("cus_base", "active")
        apply_stripe_event(session, event)
        apply_billing_email(session, event, mailer)
        session.commit()
        session.refresh(user)
        assert user.billing_entitled is True
        assert user.billing_email_spell_open is False
        assert mailer.sent == []


def test_a_charge_that_ends_entitlement_does_not_send() -> None:
    mailer = _Mailer()
    with SessionLocal() as session:
        user = ensure_user(session, "billing-ended-user")
        user.email = "ended@example.com"
        user.billing_entitled = True
        user.stripe_customer_id = "cus_ended"
        user.billing_email_spell_open = False
        session.commit()
        event = {
            "type": "customer.subscription.updated",
            "data": {
                "object": {"id": "sub_ended", "customer": "cus_ended", "status": "canceled"},
                "previous_attributes": {"status": "active"},
            },
        }
        apply_stripe_event(session, event)
        apply_billing_email(session, event, mailer)
        session.commit()
        session.refresh(user)
        assert user.billing_entitled is False
        assert user.billing_email_spell_open is False
        assert mailer.sent == []


def test_rejected_billing_email_leaves_the_spell_unspent(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_bill")
    monkeypatch.setattr(
        "career_forge.api.billing.get_mailer",
        lambda: _Mailer(fail=True),
    )
    with SessionLocal() as session:
        user = ensure_user(session, "billing-reject-user")
        user.email = "reject@example.com"
        user.billing_entitled = True
        user.stripe_customer_id = "cus_reject"
        user.billing_email_spell_open = False
        session.commit()

    event = _past_due("cus_reject", "active")
    payload = json.dumps(event).encode("utf-8")
    res = raw_client.post(
        "/billing/stripe/webhook",
        content=payload,
        headers={
            "Stripe-Signature": _sign("whsec_bill", payload, int(time.time())),
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 502, res.text
    with SessionLocal() as session:
        user = ensure_user(session, "billing-reject-user")
        assert user.billing_entitled is True
        assert user.stripe_subscription_status == "past_due"
        assert user.billing_email_spell_open is False


class _PortalStripe:
    def __init__(self) -> None:
        self.return_url: str | None = None

    def create_checkout_session(self, **kwargs: object) -> str:
        raise AssertionError(kwargs)

    def retrieve_checkout_session(self, session_id: str) -> dict:
        raise AssertionError(session_id)

    def create_portal_session(self, *, customer_id: str, return_url: str) -> str:
        assert customer_id == "cus_portal"
        self.return_url = return_url
        return "https://billing.stripe.com/p/session/fresh"


def _enable_stripe(monkeypatch: pytest.MonkeyPatch) -> _PortalStripe:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(settings, "stripe_price_id", "price_test")
    monkeypatch.setattr(settings, "frontend_url", "http://localhost:3300/career-forge")
    client = _PortalStripe()
    set_stripe_client(client)
    return client


def test_portal_503_when_stripe_unconfigured(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    headers = _auth_headers(raw_client, "portal-off")
    res = raw_client.post("/billing/portal", headers=headers)
    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "stripe_not_configured"


def test_portal_409_without_a_stripe_customer(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _enable_stripe(monkeypatch)
    headers = _auth_headers(raw_client, "portal-no-customer")
    res = raw_client.post("/billing/portal", headers=headers)
    assert res.status_code == 409
    assert res.json()["detail"]["code"] == "no_stripe_customer"


def test_portal_session_returns_to_product_entry_without_a_roadmap(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _enable_stripe(monkeypatch)
    headers = _auth_headers(raw_client, "portal-entry")
    with SessionLocal() as session:
        user = ensure_user(session, "portal-entry")
        user.stripe_customer_id = "cus_portal"
        user.roadmap_presence_at = None
        session.commit()
    res = raw_client.post("/billing/portal", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["portal_url"] == "https://billing.stripe.com/p/session/fresh"
    assert client.return_url == "http://localhost:3300/career-forge/"
    with SessionLocal() as session:
        user = ensure_user(session, "portal-entry")
        assert user.roadmap_presence_at is None


def test_portal_session_returns_to_the_roadmap_when_one_exists(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    client = _enable_stripe(monkeypatch)
    headers = _auth_headers(raw_client, "portal-roadmap")
    with SessionLocal() as session:
        user = ensure_user(session, "portal-roadmap")
        user.stripe_customer_id = "cus_portal"
        session.add(
            ForgeArtifact(
                user_id=user.id,
                graph_run_id="run-portal-roadmap",
                title="RAG",
                snapshot=[],
                is_active=True,
            )
        )
        session.commit()
    res = raw_client.post("/billing/portal", headers=headers)
    assert res.status_code == 200, res.text
    assert client.return_url == "http://localhost:3300/career-forge/roadmap"
