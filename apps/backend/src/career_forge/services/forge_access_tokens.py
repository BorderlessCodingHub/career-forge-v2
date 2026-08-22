"""Share + resume forge deep-link tokens (CAR-27 / ADR-003 / CAR-47)."""

from __future__ import annotations

import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from career_forge.auth.jwt_tokens import EMAIL_PROVIDER, mint_anonymous_token
from career_forge.config import settings
from career_forge.db.models.forge_access_token import (
    ROLE_RESUME,
    ROLE_SHARE,
    ForgeAccessToken,
)
from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.repositories.user import ensure_user
from career_forge.errors import BadRequestError, GoneError, NotFoundError
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.services.forge_artifacts import (
    ForgeArtifactNotFoundError,
    roadmap_from_snapshot,
)
from career_forge.services.mailer import Mailer, get_mailer

_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"


class TokenMintResult(TypedDict):
    token: str
    path: str


class ResumeConsumeResult(TypedDict):
    access_token: str
    external_id: str
    token_type: str


class ResumeEmailResult(TypedDict):
    ok: bool
    email: str
    path: str


class ForgeAccessTokenNotFoundError(NotFoundError):
    """Share/resume token missing, revoked, or expired."""


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _mint_raw_token() -> str:
    return secrets.token_urlsafe(32)


def _owned_artifact(
    session: Session,
    external_id: str,
    public_id: uuid.UUID,
) -> ForgeArtifact:
    user = ensure_user(session, external_id)
    artifact = session.scalar(
        select(ForgeArtifact).where(
            ForgeArtifact.public_id == public_id,
            ForgeArtifact.user_id == user.id,
        ),
    )
    if artifact is None:
        raise ForgeArtifactNotFoundError("Forge artifact not found")
    return artifact


def create_share_token(
    session: Session,
    external_id: str,
    public_id: uuid.UUID,
) -> TokenMintResult:
    artifact = _owned_artifact(session, external_id, public_id)
    raw = _mint_raw_token()
    row = ForgeAccessToken(
        artifact_id=artifact.id,
        role=ROLE_SHARE,
        token_hash=_hash_token(raw),
        expires_at=None,
    )
    session.add(row)
    session.commit()
    return {"token": raw, "path": f"/share/{raw}"}


def create_resume_token(
    session: Session,
    external_id: str,
    public_id: uuid.UUID,
) -> TokenMintResult:
    artifact = _owned_artifact(session, external_id, public_id)
    raw = _mint_raw_token()
    ttl_days = settings.jwt_resume_ttl_days
    row = ForgeAccessToken(
        artifact_id=artifact.id,
        role=ROLE_RESUME,
        token_hash=_hash_token(raw),
        expires_at=datetime.now(UTC) + timedelta(days=ttl_days),
    )
    session.add(row)
    session.commit()
    return {"token": raw, "path": f"/resume/{raw}"}


def email_resume_link(
    session: Session,
    *,
    external_id: str,
    provider: str,
    public_id: uuid.UUID,
    mailer: Mailer | None = None,
) -> ResumeEmailResult:
    """Mint a resume token and email it to the OTP-verified account address.

    Requires ``provider=email`` (CAR-44). Optional CAR-29 email store alone is
    not sufficient. Persists the token only after the mailer accepts the send.
    """
    if provider != EMAIL_PROVIDER:
        raise BadRequestError(
            "verify your email with OTP before requesting a resume email",
        )

    user = ensure_user(session, external_id)
    email = user.email
    if not email or email.endswith(_DEMO_EMAIL_SUFFIX):
        raise BadRequestError("no verified email on this account")

    artifact = _owned_artifact(session, external_id, public_id)
    raw = _mint_raw_token()
    path = f"/resume/{raw}"
    resume_url = f"{settings.frontend_url.rstrip('/')}{path}"
    row = ForgeAccessToken(
        artifact_id=artifact.id,
        role=ROLE_RESUME,
        token_hash=_hash_token(raw),
        expires_at=datetime.now(UTC) + timedelta(days=settings.jwt_resume_ttl_days),
    )
    session.add(row)
    session.flush()
    try:
        (mailer or get_mailer()).send_resume_link(to_email=email, resume_url=resume_url)
        session.commit()
    except Exception as exc:
        session.rollback()
        raise BadRequestError(
            "failed to send resume email — try again later",
        ) from exc
    return {"ok": True, "email": email, "path": path}


def revoke_share_tokens(
    session: Session,
    external_id: str,
    public_id: uuid.UUID,
) -> int:
    artifact = _owned_artifact(session, external_id, public_id)
    now = datetime.now(UTC)
    rows = list(
        session.scalars(
            select(ForgeAccessToken).where(
                ForgeAccessToken.artifact_id == artifact.id,
                ForgeAccessToken.role == ROLE_SHARE,
                ForgeAccessToken.revoked_at.is_(None),
            ),
        ),
    )
    for row in rows:
        row.revoked_at = now
    session.commit()
    return len(rows)


def resolve_share(session: Session, token: str) -> RoadmapResponse:
    row = session.scalar(
        select(ForgeAccessToken)
        .options(joinedload(ForgeAccessToken.artifact))
        .where(
            ForgeAccessToken.token_hash == _hash_token(token),
            ForgeAccessToken.role == ROLE_SHARE,
        ),
    )
    if row is None or row.revoked_at is not None:
        raise ForgeAccessTokenNotFoundError("Share link not found")
    return roadmap_from_snapshot(row.artifact)


def consume_resume(session: Session, token: str) -> ResumeConsumeResult:
    row = session.scalar(
        select(ForgeAccessToken)
        .options(
            joinedload(ForgeAccessToken.artifact).joinedload(ForgeArtifact.user),
        )
        .where(
            ForgeAccessToken.token_hash == _hash_token(token),
            ForgeAccessToken.role == ROLE_RESUME,
        ),
    )
    if row is None or row.revoked_at is not None:
        raise ForgeAccessTokenNotFoundError("Resume link not found")

    if row.consumed_at is not None:
        raise GoneError("Resume link already used")

    now = datetime.now(UTC)
    if row.expires_at is not None:
        expires = row.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=UTC)
        if expires <= now:
            raise GoneError("Resume link expired")

    owner = row.artifact.user
    external_id = owner.external_id
    if not external_id:
        # Fallback: ensure a stable external_id exists for JWT sub.
        external_id = f"user-{owner.id.hex[:8]}"
        owner.external_id = external_id
        # Also keep ensure_user path warm for callers.
        ensure_user(session, external_id)

    row.consumed_at = now
    session.commit()

    access_token = mint_anonymous_token(external_id)
    return {
        "access_token": access_token,
        "external_id": external_id,
        "token_type": "bearer",
    }
