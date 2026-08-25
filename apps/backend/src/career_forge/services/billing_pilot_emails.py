"""Operator-managed pilot billing grants (CAR-87)."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.billing_pilot_email import (
    BillingPilotEmail,
    BillingPilotEmailAudit,
)
from career_forge.services.operator_access import require_access_role


def normalize_pilot_email(email: str) -> str:
    normalized = email.strip().lower()
    if (
        not normalized
        or "@" not in normalized
        or normalized.startswith("@")
        or normalized.endswith("@")
        or len(normalized) > 255
    ):
        raise ValueError("valid email is required")
    return normalized


def pilot_email_is_listed(session: Session, email: str | None) -> bool:
    if not email:
        return False
    try:
        normalized = normalize_pilot_email(email)
    except ValueError:
        return False
    return session.get(BillingPilotEmail, normalized) is not None


def list_pilot_emails(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[BillingPilotEmail]:
    require_access_role(principal)
    return list(
        session.scalars(
            select(BillingPilotEmail).order_by(
                BillingPilotEmail.created_at.desc(),
                BillingPilotEmail.email,
            )
        )
    )


def add_pilot_email(
    session: Session,
    *,
    principal: OperatorPrincipal,
    email: str,
) -> BillingPilotEmail:
    require_access_role(principal)
    normalized = normalize_pilot_email(email)
    inserted_email = session.scalar(
        insert(BillingPilotEmail)
        .values(
            email=normalized,
            created_by_operator_id=principal.operator_id,
        )
        .on_conflict_do_nothing(index_elements=[BillingPilotEmail.email])
        .returning(BillingPilotEmail.email)
    )
    if inserted_email is not None:
        session.add(
            BillingPilotEmailAudit(
                email=normalized,
                action="add",
                operator_id=principal.operator_id,
                actor_email=principal.email,
            )
        )
        session.flush()
    row = session.get(BillingPilotEmail, normalized)
    if row is None:  # Defensive: INSERT/SELECT must be atomic in this transaction.
        raise RuntimeError("pilot email insert did not persist")
    return row


def remove_pilot_email(
    session: Session,
    *,
    principal: OperatorPrincipal,
    email: str,
) -> None:
    require_access_role(principal)
    normalized = normalize_pilot_email(email)
    removed = session.scalar(
        delete(BillingPilotEmail)
        .where(BillingPilotEmail.email == normalized)
        .returning(BillingPilotEmail.email)
    )
    if removed is None:
        return
    session.add(
        BillingPilotEmailAudit(
            email=normalized,
            action="delete",
            operator_id=principal.operator_id,
            actor_email=principal.email,
        )
    )
    session.flush()
