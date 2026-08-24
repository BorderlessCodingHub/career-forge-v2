"""email_otps — hashed 6-digit codes for Career Forge IdP (CAR-44)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


EMAIL_OTP_PROVIDER = "email"
OPERATOR_OTP_PROVIDER = "operator"


class EmailOtp(Base):
    """Hashed 6-digit OTP — namespace ``provider`` separates learner vs Operator (CAR-75)."""

    __tablename__ = "email_otps"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(16), nullable=False, default=EMAIL_OTP_PROVIDER)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    consumed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
