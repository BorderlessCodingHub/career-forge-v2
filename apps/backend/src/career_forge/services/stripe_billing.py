"""Stripe checkout + webhook sync for Career Forge billing (CAR-46).

Thin HTTP adapter — no official Stripe SDK. Webhook HMAC is the source of
truth; ``retrieve_checkout_session`` is the polling path after success_url.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable
from urllib import error, parse, request

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.config import settings
from career_forge.db.models.user import User
from career_forge.db.repositories.user import get_by_external_id
from career_forge.errors import BadRequestError
from career_forge.services.entitlement import stripe_configured

logger = logging.getLogger(__name__)

_ACTIVE_STATUSES = frozenset({"active", "trialing", "past_due"})
STRIPE_API = "https://api.stripe.com/v1"


@runtime_checkable
class StripeBillingClient(Protocol):
    def create_checkout_session(
        self,
        *,
        external_id: str,
        email: str | None,
        success_url: str,
        cancel_url: str,
    ) -> str: ...

    def retrieve_checkout_session(self, session_id: str) -> dict[str, Any]: ...


def _stripe_form_post(path: str, secret: str, fields: dict[str, str], timeout: float) -> str:
    body = parse.urlencode(fields).encode("utf-8")
    req = request.Request(
        f"{STRIPE_API}{path}",
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {secret}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raise OSError(f"stripe HTTP {exc.code}") from exc


def _stripe_get(path: str, secret: str, timeout: float) -> str:
    req = request.Request(
        f"{STRIPE_API}{path}",
        method="GET",
        headers={"Authorization": f"Bearer {secret}"},
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            return resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raise OSError(f"stripe HTTP {exc.code}") from exc


class HttpStripeBillingClient:
    def __init__(
        self,
        *,
        secret_key: str,
        price_id: str,
        timeout: float = 10.0,
        post: Callable[[str, str, dict[str, str], float], str] | None = None,
        get: Callable[[str, str, float], str] | None = None,
    ) -> None:
        self._secret = secret_key
        self._price_id = price_id
        self._timeout = timeout
        self._post = post or _stripe_form_post
        self._get = get or _stripe_get

    def create_checkout_session(
        self,
        *,
        external_id: str,
        email: str | None,
        success_url: str,
        cancel_url: str,
    ) -> str:
        fields = {
            "mode": "subscription",
            "success_url": success_url,
            "cancel_url": cancel_url,
            "client_reference_id": external_id,
            "line_items[0][price]": self._price_id,
            "line_items[0][quantity]": "1",
            "metadata[external_id]": external_id,
        }
        if email:
            fields["customer_email"] = email
        payload = json.loads(self._post("/checkout/sessions", self._secret, fields, self._timeout))
        url = payload.get("url")
        if not isinstance(url, str) or not url:
            raise OSError("stripe checkout session missing url")
        return url

    def retrieve_checkout_session(self, session_id: str) -> dict[str, Any]:
        raw = self._get(f"/checkout/sessions/{session_id}", self._secret, self._timeout)
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise OSError("stripe checkout session invalid")
        return payload


_client: StripeBillingClient | None = None


def get_stripe_client() -> StripeBillingClient:
    global _client
    if _client is not None:
        return _client
    if not stripe_configured():
        raise RuntimeError("Stripe is not configured")
    return HttpStripeBillingClient(
        secret_key=settings.stripe_secret_key.strip(),
        price_id=settings.stripe_price_id.strip(),
    )


def set_stripe_client(client: StripeBillingClient | None) -> None:
    global _client
    _client = client


def parse_stripe_signature_header(header: str) -> tuple[int, list[str]]:
    timestamp: int | None = None
    signatures: list[str] = []
    for piece in header.split(","):
        key, _, value = piece.partition("=")
        key = key.strip()
        value = value.strip()
        if key == "t" and value.isdigit():
            timestamp = int(value)
        elif key == "v1" and value:
            signatures.append(value)
    if timestamp is None or not signatures:
        raise BadRequestError("invalid Stripe-Signature header")
    return timestamp, signatures


def verify_webhook_signature(
    payload: bytes,
    header: str,
    secret: str,
    *,
    now: float | None = None,
    tolerance_s: int = 300,
) -> None:
    timestamp, signatures = parse_stripe_signature_header(header)
    stamp = now if now is not None else time.time()
    if abs(stamp - timestamp) > tolerance_s:
        raise BadRequestError("Stripe-Signature timestamp outside tolerance")
    expected = hmac.new(
        secret.encode("utf-8"),
        f"{timestamp}.".encode("utf-8") + payload,
        hashlib.sha256,
    ).hexdigest()
    if not any(hmac.compare_digest(expected, candidate) for candidate in signatures):
        raise BadRequestError("invalid Stripe-Signature")


def _set_billing(
    user: User,
    *,
    entitled: bool,
    customer_id: str | None = None,
    subscription_id: str | None = None,
) -> None:
    user.billing_entitled = entitled
    if customer_id:
        user.stripe_customer_id = customer_id
    if subscription_id:
        user.stripe_subscription_id = subscription_id


def _find_user(session: Session, *, external_id: str | None, customer_id: str | None) -> User | None:
    if external_id:
        user = get_by_external_id(session, external_id)
        if user is not None:
            return user
    if customer_id:
        return session.scalar(select(User).where(User.stripe_customer_id == customer_id))
    return None


def apply_stripe_event(session: Session, event: dict[str, Any]) -> None:
    """Persist billing_entitled from a verified Stripe event payload."""
    event_type = event.get("type")
    data = event.get("data")
    if not isinstance(event_type, str) or not isinstance(data, dict):
        return
    obj = data.get("object")
    if not isinstance(obj, dict):
        return

    if event_type == "checkout.session.completed":
        paid = obj.get("payment_status") in {"paid", "no_payment_required"} or obj.get(
            "status"
        ) == "complete"
        if not paid:
            return
        metadata = obj.get("metadata") if isinstance(obj.get("metadata"), dict) else {}
        external_id = obj.get("client_reference_id") or metadata.get("external_id")
        if not isinstance(external_id, str) or not external_id:
            logger.warning("stripe checkout.session.completed missing client_reference_id")
            return
        user = _find_user(session, external_id=external_id, customer_id=None)
        if user is None:
            logger.warning("stripe checkout completed for unknown user %s", external_id)
            return
        customer = obj.get("customer") if isinstance(obj.get("customer"), str) else None
        subscription = obj.get("subscription") if isinstance(obj.get("subscription"), str) else None
        _set_billing(user, entitled=True, customer_id=customer, subscription_id=subscription)
        return

    if event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        customer = obj.get("customer") if isinstance(obj.get("customer"), str) else None
        subscription = obj.get("id") if isinstance(obj.get("id"), str) else None
        status = obj.get("status") if isinstance(obj.get("status"), str) else ""
        user = _find_user(session, external_id=None, customer_id=customer)
        if user is None:
            logger.warning("stripe subscription event for unknown customer %s", customer)
            return
        entitled = event_type != "customer.subscription.deleted" and status in _ACTIVE_STATUSES
        _set_billing(user, entitled=entitled, customer_id=customer, subscription_id=subscription)


def apply_checkout_session(session: Session, payload: dict[str, Any]) -> None:
    """Polling path: treat a retrieved Checkout Session like the webhook object."""
    apply_stripe_event(
        session,
        {"type": "checkout.session.completed", "data": {"object": payload}},
    )


def checkout_urls() -> tuple[str, str]:
    base = settings.frontend_url.rstrip("/")
    success = f"{base}/forge?billing=success&session_id={{CHECKOUT_SESSION_ID}}"
    cancel = f"{base}/forge?billing=cancel"
    return success, cancel
