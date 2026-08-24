"""Operator console HTTP routes — identity and shell contracts."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import (
    OperatorPrincipal,
    operator_cookie_params,
    revoke_operator_session,
)
from career_forge.config import settings
from career_forge.db.session import get_db
from career_forge.schemas.operator_auth import (
    OperatorMeResponse,
    OperatorOtpRequestBody,
    OperatorOtpRequestResponse,
    OperatorOtpVerifyBody,
    OperatorOtpVerifyResponse,
    OperatorSeatListResponse,
    OperatorSeatResponse,
)
from career_forge.services.operator_allowlist import desks_for_roles, list_operator_seat_emails
from career_forge.services.operator_otp import request_operator_otp, verify_operator_otp

router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def get_operator_principal(request: Request) -> OperatorPrincipal:
    principal = getattr(request.state, "operator_principal", None)
    if principal is None:
        raise HTTPException(status_code=401, detail="Operator session required")
    return principal


@router.post("/auth/otp/request", response_model=OperatorOtpRequestResponse)
def operator_otp_request(
    body: OperatorOtpRequestBody,
    request: Request,
    db: Session = Depends(get_db),
) -> OperatorOtpRequestResponse:
    expires_in = request_operator_otp(
        db,
        email=body.email,
        client_ip=_client_ip(request),
    )
    return OperatorOtpRequestResponse(email=body.email, expires_in=expires_in)


@router.post("/auth/otp/verify", response_model=OperatorOtpVerifyResponse)
def operator_otp_verify(
    body: OperatorOtpVerifyBody,
    db: Session = Depends(get_db),
) -> Response:
    payload, token = verify_operator_otp(
        db,
        email=body.email,
        code=body.code,
    )
    response = JSONResponse(content=payload)
    cookie = operator_cookie_params(max_age=payload["expires_in"])
    response.set_cookie(value=token, **cookie)
    return response


@router.post("/auth/sign-out", status_code=204)
def operator_sign_out(
    request: Request,
    db: Session = Depends(get_db),
    _principal: OperatorPrincipal = Depends(get_operator_principal),
) -> Response:
    token = request.cookies.get(settings.operator_cookie_name)
    if isinstance(token, str) and token.strip():
        try:
            revoke_operator_session(db, token.strip())
            db.commit()
        except ValueError as exc:
            db.rollback()
            raise HTTPException(status_code=401, detail="Invalid operator session") from exc
    response = Response(status_code=204)
    cookie = operator_cookie_params()
    response.delete_cookie(key=str(cookie["key"]), path=str(cookie["path"]))
    return response


@router.get("/me", response_model=OperatorMeResponse)
def operator_me(
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorMeResponse:
    return OperatorMeResponse(
        email=principal.email,
        operator_id=principal.operator_id,
        desk_roles=principal.desk_roles,
        desks=desks_for_roles(principal.desk_roles),
    )


@router.get("/seats", response_model=OperatorSeatListResponse)
def operator_seats(
    db: Session = Depends(get_db),
    _principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorSeatListResponse:
    return OperatorSeatListResponse(
        seats=[
            OperatorSeatResponse(email=email)
            for email in list_operator_seat_emails(db)
        ],
    )
