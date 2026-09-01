"""Auth HTTP routes — anonymous mint + email OTP (CAR-23 / CAR-44)."""

from __future__ import annotations

import re
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import ANON_PROVIDER
from career_forge.auth.providers import get_auth_provider
from career_forge.auth.token_revocation import revoke_token
from career_forge.api.deps import get_principal, require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import get_db
from career_forge.schemas.otp import (
    IdentityModeResponse,
    OtpRequestBody,
    OtpRequestResponse,
    OtpVerifyBody,
    OtpVerifyResponse,
    PilotEnterBody,
)
from career_forge.services.otp import request_otp, verify_otp
from career_forge.services.pilot_enter import enter_pilot

router = APIRouter()

_EXTERNAL_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,63}$")


class AnonMintRequest(BaseModel):
    """Optional ``external_id`` migrates an existing localStorage anon id into a JWT."""

    external_id: str | None = Field(default=None, max_length=64)


class AnonMintResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    external_id: str
    provider: str = ANON_PROVIDER
    expires_in: int


def _normalize_external_id(raw: str | None) -> str:
    if raw is None or not raw.strip():
        return f"user-{uuid.uuid4().hex[:8]}"
    candidate = raw.strip()
    if not _EXTERNAL_ID_RE.match(candidate):
        return f"user-{uuid.uuid4().hex[:8]}"
    return candidate


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/anon/mint", response_model=AnonMintResponse)
def mint_anonymous_token(
    body: AnonMintRequest,
    db: Session = Depends(get_db),
) -> AnonMintResponse:
    """Mint an anonymous Bearer JWT and ensure ``users.external_id`` exists."""
    external_id = _normalize_external_id(body.external_id)
    ensure_user(db, external_id)
    db.commit()
    token = get_auth_provider().mint_anonymous(external_id)
    return AnonMintResponse(
        access_token=token,
        external_id=external_id,
        expires_in=settings.jwt_anon_ttl_days * 24 * 3600,
    )


@router.get("/identity-mode", response_model=IdentityModeResponse)
def identity_mode() -> IdentityModeResponse:
    """Public: whether learner entry requires OTP (CAR-100)."""
    return IdentityModeResponse(email_otp_required=settings.identity_email_otp)


def _resolve_enter_external_id(request: Request, body: PilotEnterBody) -> str:
    """Bearer, body ``external_id``, or a fresh id — enter does not require prior mint."""
    header = request.headers.get("authorization") or request.headers.get("Authorization")
    if header and header.lower().startswith("bearer "):
        token = header[7:].strip()
        if token:
            try:
                return get_auth_provider().verify(token).external_id
            except ValueError:
                pass
    if body.external_id:
        return _normalize_external_id(body.external_id)
    return _normalize_external_id(None)


@router.post("/pilot/enter", response_model=OtpVerifyResponse)
def pilot_enter(
    body: PilotEnterBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OtpVerifyResponse:
    """Mint email JWT when the address is on the pilot list (CAR-100 freeze)."""
    result = enter_pilot(
        db,
        email=body.email,
        client_ip=_client_ip(request),
        external_id=_resolve_enter_external_id(request, body),
    )
    return OtpVerifyResponse(**result)


@router.get("/session", status_code=204)
def auth_session(
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> Response:
    """Product-loop session check — 204 when email identity (and freeze list) pass."""
    return Response(status_code=204)


@router.post("/otp/request", response_model=OtpRequestResponse)
def otp_request(
    body: OtpRequestBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OtpRequestResponse:
    """Send a 6-digit OTP to ``email`` (dev: log mailer). Public + rate-limited."""
    expires_in = request_otp(
        db,
        email=body.email,
        client_ip=_client_ip(request),
    )
    return OtpRequestResponse(email=body.email, expires_in=expires_in)


def _resolve_verify_external_id(request: Request, body: OtpVerifyBody) -> str:
    """Bearer (anon promote) or body ``external_id`` (happy path without anon mint)."""
    header = request.headers.get("authorization") or request.headers.get("Authorization")
    if header and header.lower().startswith("bearer "):
        token = header[7:].strip()
        if token:
            try:
                principal = get_auth_provider().verify(token)
                return principal.external_id
            except ValueError:
                pass
    if body.external_id:
        return _normalize_external_id(body.external_id)
    raise HTTPException(
        status_code=401,
        detail="Missing Bearer token or external_id for OTP verify",
    )


@router.post("/otp/verify", response_model=OtpVerifyResponse)
def otp_verify(
    body: OtpVerifyBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OtpVerifyResponse:
    """Verify OTP → promote anon or 409 conflict payload for chooser."""
    external_id = _resolve_verify_external_id(request, body)
    result = verify_otp(
        db,
        external_id=external_id,
        email=body.email,
        code=body.code,
    )
    return OtpVerifyResponse(**result)


def _bearer_token(request: Request) -> str:
    header = request.headers.get("authorization") or request.headers.get("Authorization")
    if not header or not header.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization Bearer token")
    token = header[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization Bearer token")
    return token


@router.post("/sign-out", status_code=204)
def sign_out(
    request: Request,
    db: Session = Depends(get_db),
    _principal: AuthPrincipal = Depends(get_principal),
) -> Response:
    """Revoke the current access token jti (this device only)."""
    token = _bearer_token(request)
    try:
        revoke_token(db, token)
        db.commit()
    except ValueError as exc:
        db.rollback()
        raise HTTPException(status_code=401, detail="Invalid or expired Bearer token") from exc
    return Response(status_code=204)
