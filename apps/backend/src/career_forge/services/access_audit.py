"""Shared append-only audit operations for entitlement actors (CAR-77)."""

from __future__ import annotations

import uuid
from typing import Any, Literal

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from career_forge.db.models.operator_access_audit import OperatorAccessAudit
from career_forge.db.models.user import User

AccessActorType = Literal["operator", "stripe", "system"]


def append_access_audit(
    session: Session,
    *,
    actor_type: AccessActorType,
    user: User,
    field: str,
    before: Any,
    after: Any,
    operator_id: int | None = None,
    actor_email: str | None = None,
) -> OperatorAccessAudit:
    if not user.email:
        raise ValueError("audited learner must have an email")
    row = OperatorAccessAudit(
        actor_type=actor_type,
        operator_id=operator_id,
        actor_email=actor_email,
        learner_id=user.id,
        learner_email=user.email,
        field=field,
        before_value=before,
        after_value=after,
        action="clear" if after is None else "set",
    )
    session.add(row)
    return row


def list_access_audit(
    session: Session,
    *,
    learner_id: uuid.UUID | None = None,
    actor_type: AccessActorType | None = None,
    limit: int = 50,
) -> list[OperatorAccessAudit]:
    statement: Select[tuple[OperatorAccessAudit]] = select(OperatorAccessAudit)
    if learner_id is not None:
        statement = statement.where(OperatorAccessAudit.learner_id == learner_id)
    if actor_type is not None:
        statement = statement.where(OperatorAccessAudit.actor_type == actor_type)
    statement = statement.order_by(
        OperatorAccessAudit.created_at.desc(),
        OperatorAccessAudit.id.desc(),
    ).limit(limit)
    return list(session.scalars(statement))
