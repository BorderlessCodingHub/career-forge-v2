"""Monthly usage aggregates for cost pool + per-user forge caps (CAR-6)."""

from __future__ import annotations

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base

# Sentinel user_id for the global student pool row.
GLOBAL_USAGE_USER_ID = "__global__"


class UsageMonthly(Base):
    """Per calendar month counters — one row per (year_month, user_id)."""

    __tablename__ = "usage_monthly"

    year_month: Mapped[str] = mapped_column(String(7), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    billable_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    forge_runs: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    estimated_cost_brl: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
