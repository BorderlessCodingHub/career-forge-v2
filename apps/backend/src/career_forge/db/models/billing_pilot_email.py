"""Database-backed pilot billing grants and immutable audit (CAR-87)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class BillingPilotEmail(Base):
    __tablename__ = "billing_pilot_emails"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_billing_pilot_email_lowercase"),
    )

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_by_operator_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=True,
    )


class BillingPilotEmailAudit(Base):
    __tablename__ = "billing_pilot_email_audit"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    operator_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=True,
    )
    actor_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
