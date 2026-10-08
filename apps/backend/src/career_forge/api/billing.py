"""Billing HTTP — Stripe checkout, webhook, and session sync (CAR-46)."""

from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from career_forge.api.deps import ExternalId
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import get_db
from career_forge.errors import BadRequestError
from career_forge.services.billing_email import apply_billing_email, portal_return_url
from career_forge.services.continuity import user_has_roadmap
from career_forge.services.entitlement import stripe_configured
from career_forge.services.mailer import get_mailer
from career_forge.services.stripe_billing import (
    apply_checkout_session,
    apply_stripe_event,
    checkout_urls,
    get_stripe_client,
    verify_webhook_signature,
)

router = APIRouter()

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"


class BillingCheckoutResponse(BaseModel):
    checkout_url: str


class BillingSyncRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=256)


class BillingSyncResponse(BaseModel):
    billing_entitled: bool


class BillingPortalResponse(BaseModel):
    portal_url: str


def _checkout_email(email: str | None) -> str | None:
    if not email or email.endswith(_DEMO_EMAIL_SUFFIX):
        return None
    return email


@router.post("/checkout", response_model=BillingCheckoutResponse)
def create_billing_checkout(
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> BillingCheckoutResponse:
    if not stripe_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "stripe_not_configured",
                "message": "Stripe checkout is not configured",
            },
        )
    user = ensure_user(db, external_id)
    success_url, cancel_url = checkout_urls()
    try:
        url = get_stripe_client().create_checkout_session(
            external_id=external_id,
            email=_checkout_email(user.email),
            success_url=success_url,
            cancel_url=cancel_url,
        )
    except OSError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return BillingCheckoutResponse(checkout_url=url)


@router.post("/sync", response_model=BillingSyncResponse)
def sync_billing_session(
    body: BillingSyncRequest,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> BillingSyncResponse:
    if not stripe_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "stripe_not_configured",
                "message": "Stripe checkout is not configured",
            },
        )
    try:
        payload = get_stripe_client().retrieve_checkout_session(body.session_id)
    except OSError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    if payload.get("client_reference_id") != external_id:
        raise HTTPException(status_code=403, detail="Checkout session belongs to another user")
    if payload.get("status") == "complete" or payload.get("payment_status") == "paid":
        apply_checkout_session(db, payload)
        db.commit()
    user = ensure_user(db, external_id)
    db.refresh(user)
    return BillingSyncResponse(billing_entitled=bool(user.billing_entitled))


@router.post("/portal", response_model=BillingPortalResponse)
def create_billing_portal(
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> BillingPortalResponse:
    """Fresh Customer Portal session for the payment-method update.

    Opening this route is not Roadmap presence. Stripe actions stay out of
    the Operator console.
    """
    if not stripe_configured():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "stripe_not_configured",
                "message": "Stripe checkout is not configured",
            },
        )
    user = ensure_user(db, external_id)
    if not user.stripe_customer_id:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "no_stripe_customer",
                "message": "No Career Forge subscription to update",
            },
        )
    return_url = portal_return_url(
        has_roadmap=user_has_roadmap(db, user),
        frontend_url=settings.frontend_url,
    )
    try:
        url = get_stripe_client().create_portal_session(
            customer_id=user.stripe_customer_id,
            return_url=return_url,
        )
    except OSError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return BillingPortalResponse(portal_url=url)


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
    stripe_signature: str | None = Header(default=None, alias="Stripe-Signature"),
) -> dict[str, Any]:
    secret = settings.stripe_webhook_secret.strip()
    if not secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing Stripe-Signature header")
    payload = await request.body()
    try:
        verify_webhook_signature(payload, stripe_signature, secret)
        event = _json_object(payload)
    except BadRequestError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    apply_stripe_event(db, event)
    rejected = apply_billing_email(db, event, get_mailer())
    db.commit()
    if rejected:
        raise HTTPException(status_code=502, detail="billing email was rejected")
    return {"received": True}


def _json_object(payload: bytes) -> dict[str, Any]:
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BadRequestError("invalid Stripe event JSON") from exc
    if not isinstance(parsed, dict):
        raise BadRequestError("invalid Stripe event JSON")
    return parsed
