"""Stripe checkout + webhook sync (CAR-46).

Seams: verify_webhook_signature / apply_stripe_event;
POST /billing/stripe/webhook (public); POST /billing/checkout + /billing/sync.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from career_forge.auth.providers import get_auth_provider
from career_forge.config import settings
from career_forge.db.models.operator_access_audit import OperatorAccessAudit
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.errors import BadRequestError
from career_forge.services.stripe_billing import (
    apply_stripe_event,
    set_stripe_client,
    verify_webhook_signature,
)


def _sign(secret: str, payload: bytes, timestamp: int) -> str:
    digest = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()
    return f"t={timestamp},v1={digest}"


def test_webhook_signature_accepts_valid_header() -> None:
    payload = b'{"type":"ping"}'
    header = _sign("whsec_test", payload, int(time.time()))
    verify_webhook_signature(payload, header, "whsec_test")


def test_webhook_signature_rejects_bad_hmac() -> None:
    payload = b'{"type":"ping"}'
    with pytest.raises(BadRequestError):
        verify_webhook_signature(payload, "t=1,v1=deadbeef", "whsec_test", now=1.0)


def test_checkout_completed_sets_billing_entitled() -> None:
    with SessionLocal() as session:
        user = ensure_user(session, "stripe-user-paid")
        user.billing_entitled = False
        user.stripe_customer_id = None
        user.stripe_subscription_id = None
        user.stripe_subscription_status = None
        session.commit()
        apply_stripe_event(
            session,
            {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "client_reference_id": "stripe-user-paid",
                        "customer": "cus_123",
                        "subscription": "sub_123",
                        "payment_status": "paid",
                        "status": "complete",
                    }
                },
            },
        )
        session.commit()
        session.refresh(user)
        assert user.billing_entitled is True
        assert user.stripe_customer_id == "cus_123"
        assert user.stripe_subscription_id == "sub_123"
        assert user.stripe_subscription_status == "active"
        audit = session.scalar(
            select(OperatorAccessAudit)
            .where(OperatorAccessAudit.learner_id == user.id)
            .order_by(OperatorAccessAudit.id.desc())
        )
        assert audit is not None
        assert audit.actor_type == "stripe"
        assert audit.field == "billing_entitled"
        assert audit.before_value is False
        assert audit.after_value is True


def test_checkout_completed_unpaid_does_not_entitle() -> None:
    with SessionLocal() as session:
        user = ensure_user(session, "stripe-user-unpaid")
        session.commit()
        apply_stripe_event(
            session,
            {
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "client_reference_id": "stripe-user-unpaid",
                        "customer": "cus_unpaid",
                        "payment_status": "unpaid",
                        "status": "open",
                    }
                },
            },
        )
        session.commit()
        session.refresh(user)
        assert user.billing_entitled is False


def test_subscription_deleted_revokes_billing() -> None:
    with SessionLocal() as session:
        user = ensure_user(session, "stripe-user-revoke")
        user.billing_entitled = True
        user.stripe_customer_id = "cus_rev"
        session.commit()
        apply_stripe_event(
            session,
            {
                "type": "customer.subscription.deleted",
                "data": {
                    "object": {
                        "id": "sub_rev",
                        "customer": "cus_rev",
                        "status": "canceled",
                    }
                },
            },
        )
        session.commit()
        session.refresh(user)
        assert user.billing_entitled is False
        assert user.stripe_subscription_status == "canceled"


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def test_webhook_http_sets_entitlement(raw_client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_http")
    with SessionLocal() as session:
        ensure_user(session, "stripe-http-user")
        session.commit()

    event = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "client_reference_id": "stripe-http-user",
                "customer": "cus_http",
                "subscription": "sub_http",
                "payment_status": "paid",
                "status": "complete",
            }
        },
    }
    payload = json.dumps(event).encode("utf-8")
    header = _sign("whsec_http", payload, int(time.time()))
    res = raw_client.post(
        "/billing/stripe/webhook",
        content=payload,
        headers={"Stripe-Signature": header, "Content-Type": "application/json"},
    )
    assert res.status_code == 200, res.text
    with SessionLocal() as session:
        user = ensure_user(session, "stripe-http-user")
        assert user.billing_entitled is True


def test_webhook_http_rejects_bad_signature(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_http")
    res = raw_client.post(
        "/billing/stripe/webhook",
        content=b'{"type":"ping"}',
        headers={"Stripe-Signature": "t=1,v1=nope", "Content-Type": "application/json"},
    )
    assert res.status_code == 400


def test_checkout_503_when_stripe_unconfigured(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "")
    monkeypatch.setattr(settings, "stripe_price_id", "")
    headers = _auth_headers(raw_client, "stripe-checkout-off")
    res = raw_client.post("/billing/checkout", headers=headers)
    assert res.status_code == 503
    assert res.json()["detail"]["code"] == "stripe_not_configured"


class _FakeStripe:
    def create_checkout_session(self, **kwargs: object) -> str:
        assert kwargs["external_id"] == "stripe-checkout-on"
        return "https://checkout.stripe.test/c/session"

    def retrieve_checkout_session(self, session_id: str) -> dict:
        assert session_id == "cs_test_1"
        return {
            "id": session_id,
            "status": "complete",
            "payment_status": "paid",
            "client_reference_id": "stripe-checkout-on",
            "customer": "cus_sync",
            "subscription": "sub_sync",
        }


def test_checkout_returns_url_when_configured(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(settings, "stripe_price_id", "price_test")
    set_stripe_client(_FakeStripe())
    headers = _auth_headers(raw_client, "stripe-checkout-on")
    res = raw_client.post("/billing/checkout", headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["checkout_url"] == "https://checkout.stripe.test/c/session"


def test_sync_polls_checkout_session(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(settings, "stripe_price_id", "price_test")
    set_stripe_client(_FakeStripe())
    headers = _auth_headers(raw_client, "stripe-checkout-on")
    res = raw_client.post("/billing/sync", json={"session_id": "cs_test_1"}, headers=headers)
    assert res.status_code == 200, res.text
    assert res.json()["billing_entitled"] is True
    with SessionLocal() as session:
        user = ensure_user(session, "stripe-checkout-on")
        assert user.billing_entitled is True
        assert user.stripe_customer_id == "cus_sync"


def test_paid_external_second_forge_allowed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from career_forge.ai.graphs.diagnosis import build_diagnosis_response
    from career_forge.schemas.diagnosis import DiagnosisRequest

    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user_id = "stripe-paid-forge"
    headers = _auth_headers(raw_client, user_id)
    with SessionLocal() as session:
        row = ensure_user(session, user_id)
        row.membership_label = "external"
        row.membership_entitled = False
        row.billing_entitled = True
        session.commit()

    diagnosis = build_diagnosis_response(
        DiagnosisRequest(
            goal_id="rag-engineer",
            motivation="I want to ship grounded RAG systems in production.",
            answers={"level": "beginner"},
        ),
    )
    body = {"user_id": user_id, "diagnosis": diagnosis.model_dump(mode="json")}
    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text
    second = raw_client.post("/forge/runs", json=body, headers=headers)
    assert second.status_code == 202, second.text
