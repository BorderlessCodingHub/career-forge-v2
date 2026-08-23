"""revoked_token_jtis — JWT jti denylist for sign-out (CAR-69)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class RevokedTokenJti(Base):
    """Revoked access-token jti until natural ``exp`` — lazy cleanup on verify."""

    __tablename__ = "revoked_token_jtis"

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
