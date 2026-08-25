"""Operator console HTTP routes — identity, shell, Access, and Content desks."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import (
    OperatorPrincipal,
    operator_cookie_params,
    revoke_operator_session,
)
from career_forge.config import settings
from career_forge.db.models.user import User
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
from career_forge.schemas.operator_access import (
    BillingPilotEmailCreate,
    BillingPilotEmailListResponse,
    BillingPilotEmailResponse,
    OperatorAccessAuditListResponse,
    OperatorAccessAuditResponse,
    OperatorAccessPatch,
    OperatorCostPoolResponse,
    OperatorLearnerAccessResponse,
)
from career_forge.schemas.operator_content import (
    OperatorContentListResponse,
    OperatorContentPatch,
    OperatorContentSkillResponse,
)
from career_forge.services.access_audit import AccessActorType, list_access_audit
from career_forge.services.billing_pilot_emails import (
    add_pilot_email,
    list_pilot_emails,
    pilot_email_is_listed,
    remove_pilot_email,
)
from career_forge.services.operator_access import (
    get_learner_by_email,
    get_operator_cost_pool,
    require_access_role,
    stripe_billing_locked,
    write_operator_access,
)
from career_forge.services.operator_allowlist import desks_for_roles, list_operator_seat_emails
from career_forge.services.operator_content import (
    ContentSkillSnapshot,
    list_content_skills,
    update_content_skill,
)
from career_forge.services.operator_otp import request_operator_otp, verify_operator_otp

router = APIRouter()


def _content_response(skill: ContentSkillSnapshot) -> OperatorContentSkillResponse:
    return OperatorContentSkillResponse.model_validate(skill)


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


def _access_response(db: Session, user: User) -> OperatorLearnerAccessResponse:
    return OperatorLearnerAccessResponse(
        email=user.email,
        operator_membership_label=user.operator_membership_label,
        membership_label=user.membership_label,
        membership_entitled=bool(user.membership_entitled),
        billing_entitled=bool(user.billing_entitled),
        pilot_email_listed=pilot_email_is_listed(db, user.email),
        stripe_subscription_status=user.stripe_subscription_status,
        stripe_billing_locked=stripe_billing_locked(user),
    )


def _audit_response(rows: list[object]) -> OperatorAccessAuditListResponse:
    return OperatorAccessAuditListResponse(
        entries=[OperatorAccessAuditResponse.model_validate(row) for row in rows]
    )


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


@router.get("/content/skills", response_model=OperatorContentListResponse)
def get_operator_content_skills(
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorContentListResponse:
    return OperatorContentListResponse(
        skills=[
            _content_response(skill)
            for skill in list_content_skills(db, principal=principal)
        ]
    )


@router.patch(
    "/content/skills/{skill_id}",
    response_model=OperatorContentSkillResponse,
)
def patch_operator_content_skill(
    skill_id: str,
    body: OperatorContentPatch,
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorContentSkillResponse:
    skill = update_content_skill(
        db,
        principal=principal,
        skill_id=skill_id,
        patch=body,
    )
    db.commit()
    return _content_response(skill)


@router.get("/access/cost-pool", response_model=OperatorCostPoolResponse)
def get_operator_access_cost_pool(
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorCostPoolResponse:
    require_access_role(principal)
    return OperatorCostPoolResponse.model_validate(get_operator_cost_pool(db))


@router.get(
    "/access/pilot-emails",
    response_model=BillingPilotEmailListResponse,
)
def get_operator_pilot_emails(
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> BillingPilotEmailListResponse:
    require_access_role(principal)
    return BillingPilotEmailListResponse(
        emails=[
            BillingPilotEmailResponse.model_validate(row)
            for row in list_pilot_emails(db, principal=principal)
        ]
    )


@router.post(
    "/access/pilot-emails",
    response_model=BillingPilotEmailResponse,
)
def post_operator_pilot_email(
    body: BillingPilotEmailCreate,
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> BillingPilotEmailResponse:
    require_access_role(principal)
    row = add_pilot_email(db, principal=principal, email=body.email)
    db.commit()
    db.refresh(row)
    return BillingPilotEmailResponse.model_validate(row)


@router.delete("/access/pilot-emails/{email}", status_code=204)
def delete_operator_pilot_email(
    email: str,
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> Response:
    require_access_role(principal)
    try:
        remove_pilot_email(db, principal=principal, email=email)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    db.commit()
    return Response(status_code=204)


@router.get(
    "/access/learners/{learner_email}",
    response_model=OperatorLearnerAccessResponse,
)
def get_operator_learner_access(
    learner_email: str,
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorLearnerAccessResponse:
    require_access_role(principal)
    return _access_response(db, get_learner_by_email(db, learner_email))


@router.patch(
    "/access/learners/{learner_email}",
    response_model=OperatorLearnerAccessResponse,
)
def patch_operator_learner_access(
    learner_email: str,
    body: OperatorAccessPatch,
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorLearnerAccessResponse:
    user = write_operator_access(
        db,
        principal=principal,
        learner_email=learner_email,
        patch=body,
    )
    db.commit()
    db.refresh(user)
    return _access_response(db, user)


@router.get(
    "/access/learners/{learner_email}/audit",
    response_model=OperatorAccessAuditListResponse,
)
def get_operator_learner_audit(
    learner_email: str,
    limit: int = Query(default=50, ge=1, le=250),
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorAccessAuditListResponse:
    require_access_role(principal)
    user = get_learner_by_email(db, learner_email)
    return _audit_response(list_access_audit(db, learner_id=user.id, limit=limit))


@router.get("/access/audit", response_model=OperatorAccessAuditListResponse)
def get_recent_operator_access_audit(
    actor_type: AccessActorType | None = "operator",
    limit: int = Query(default=50, ge=1, le=250),
    db: Session = Depends(get_db),
    principal: OperatorPrincipal = Depends(get_operator_principal),
) -> OperatorAccessAuditListResponse:
    require_access_role(principal)
    return _audit_response(list_access_audit(db, actor_type=actor_type, limit=limit))
