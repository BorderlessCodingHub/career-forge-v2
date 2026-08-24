"""Append-only audit rows for learner access changes (CAR-77)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class OperatorAccessAudit(Base):
    __tablename__ = "operator_access_audit"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    actor_type: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    operator_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=True,
    )
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    learner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    learner_email: Mapped[str] = mapped_column(String(255), nullable=False)
    field: Mapped[str] = mapped_column(String(64), nullable=False)
    before_value: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    after_value: Mapped[Any | None] = mapped_column(JSONB, nullable=True)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
