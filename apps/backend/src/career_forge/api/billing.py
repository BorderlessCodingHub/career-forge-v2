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
from career_forge.services.entitlement import stripe_configured
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
    db.commit()
    return {"received": True}


def _json_object(payload: bytes) -> dict[str, Any]:
    try:
        parsed = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BadRequestError("invalid Stripe event JSON") from exc
    if not isinstance(parsed, dict):
        raise BadRequestError("invalid Stripe event JSON")
    return parsed
