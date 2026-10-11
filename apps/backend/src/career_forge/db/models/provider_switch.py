"""One stored Provider switch — CAR-135. No row means the Direct provider."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base

DIRECT_PROVIDER = "direct"
GATEWAY_PROVIDER = "gateway"
RunProvider = Literal["direct", "gateway"]
SINGLETON_ID = 1


class ProviderSwitch(Base):
    __tablename__ = "provider_switch"
    __table_args__ = (
        CheckConstraint(f"id = {SINGLETON_ID}", name="ck_provider_switch_singleton"),
        CheckConstraint(
            "run_provider IN ('direct', 'gateway')",
            name="ck_provider_switch_run_provider",
        ),
    )

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    run_provider: Mapped[str] = mapped_column(String(16), nullable=False)
    operator_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("operators.id"),
        nullable=False,
    )
    written_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
