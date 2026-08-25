"""Operational allowlist for proven Reference embeds (CAR-89)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class EmbedHost(Base):
    __tablename__ = "embed_hosts"
    __table_args__ = (
        CheckConstraint("host = lower(host)", name="ck_embed_host_lowercase"),
        CheckConstraint("host NOT LIKE 'www.%'", name="ck_embed_host_no_www"),
    )

    host: Mapped[str] = mapped_column(String(253), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    created_by_operator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=False,
    )


class EmbedHostAudit(Base):
    __tablename__ = "embed_host_audit"
    __table_args__ = (
        CheckConstraint(
            "action IN ('add', 'remove')",
            name="ck_embed_host_audit_action",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    host: Mapped[str] = mapped_column(String(253), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(16), nullable=False)
    operator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=False,
    )
    actor_email: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
