"""operators — Borderless Operator console identity (CAR-75)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base

DeskRoles = str  # access | editor | both


class Operator(Base):
    """Operator seat — distinct from ``users`` (learner Email identity)."""

    __tablename__ = "operators"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    desk_roles: Mapped[str] = mapped_column(String(16), nullable=False, default="both")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
