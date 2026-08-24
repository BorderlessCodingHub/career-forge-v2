"""Operator console session — path-scoped cookie JWT (CAR-75)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import jwt
from starlette.requests import Request
from sqlalchemy.orm import Session

from career_forge.auth.jwt_tokens import (
    OPERATOR_PROVIDER,
    decode_token,
    mint_operator_session_token,
)
from career_forge.auth.token_revocation import cleanup_expired_revocations, is_jti_revoked, revoke_jti
from career_forge.config import settings


@dataclass(frozen=True, slots=True)
class OperatorPrincipal:
    """Identity attached after ``cf_operator_session`` cookie verification."""

    email: str
    operator_id: int
    desk_roles: str


def _exp_from_payload(payload: dict) -> datetime:
    exp = payload.get("exp")
    if isinstance(exp, datetime):
        return exp if exp.tzinfo else exp.replace(tzinfo=UTC)
    if isinstance(exp, (int, float)):
        return datetime.fromtimestamp(exp, tz=UTC)
    raise ValueError("token missing exp")


def verify_operator_session_token(db: Session, token: str) -> OperatorPrincipal:
    """Decode cookie JWT, enforce ``provider=operator``, jti denylist."""
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise ValueError("invalid or expired operator session") from exc

    if payload.get("provider") != OPERATOR_PROVIDER:
        raise ValueError("not an operator session")

    sub = payload.get("sub")
    operator_id = payload.get("operator_id")
    email = payload.get("email")
    desk_roles = payload.get("desk_roles")
    jti = payload.get("jti")
    if not isinstance(sub, str) or not sub.strip():
        raise ValueError("token missing sub")
    if not isinstance(operator_id, int):
        try:
            operator_id = int(sub.strip())
        except ValueError as exc:
            raise ValueError("token missing operator_id") from exc
    if not isinstance(email, str) or not email.strip():
        raise ValueError("token missing email")
    if not isinstance(desk_roles, str) or desk_roles not in {"access", "editor", "both"}:
        raise ValueError("token missing desk_roles")
    if not isinstance(jti, str) or not jti.strip():
        raise ValueError("token missing jti")

    cleanup_expired_revocations(db)
    if is_jti_revoked(db, jti.strip()):
        raise ValueError("operator session revoked")

    return OperatorPrincipal(
        email=email.strip().lower(),
        operator_id=operator_id,
        desk_roles=desk_roles,
    )


def revoke_operator_session(db: Session, token: str) -> None:
    try:
        payload = decode_token(token)
    except jwt.PyJWTError as exc:
        raise ValueError("invalid or expired operator session") from exc
    jti = payload.get("jti")
    if not isinstance(jti, str) or not jti.strip():
        raise ValueError("token missing jti")
    cleanup_expired_revocations(db)
    revoke_jti(db, jti.strip(), _exp_from_payload(payload))


def operator_cookie_params(*, max_age: int | None = None) -> dict[str, object]:
    secure = settings.env.lower() not in {"local", "test"}
    ttl = max_age if max_age is not None else settings.operator_session_ttl_hours * 3600
    return {
        "key": settings.operator_cookie_name,
        "httponly": True,
        "secure": secure,
        "samesite": "lax",
        "path": settings.operator_cookie_path_resolved,
        "max_age": ttl,
    }


def attach_operator_principal(request: Request, db: Session) -> None:
    """Resolve operator cookie or reject learner Bearer on ``/operator/*`` (CAR-75)."""
    from starlette.requests import Request as StarletteRequest

    from career_forge.auth.jwt_tokens import ANON_PROVIDER, EMAIL_PROVIDER
    from career_forge.auth.providers import get_auth_provider
    from career_forge.errors import ForbiddenError

    req: StarletteRequest = request
    header = req.headers.get("authorization") or req.headers.get("Authorization")
    if header and header.lower().startswith("bearer "):
        token = header[7:].strip()
        if token:
            try:
                learner = get_auth_provider().verify(token)
            except ValueError:
                pass
            else:
                if learner.provider in {EMAIL_PROVIDER, ANON_PROVIDER}:
                    raise ForbiddenError(
                        "Learner session cannot access Operator APIs",
                        code="learner_session_forbidden",
                    )

    raw = req.cookies.get(settings.operator_cookie_name)
    if not raw:
        raise ValueError("operator session required")
    req.state.operator_principal = verify_operator_session_token(db, raw)
