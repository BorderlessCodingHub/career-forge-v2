"""SQLAlchemy model for multi-turn diagnosis interview sessions (HAC-44)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class DiagnosisSessionRecord(Base):
    """Persisted DiagnosisSession between API turns."""

    __tablename__ = "diagnosis_sessions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="asking")
    intake: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    belief_state: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    cv_signals: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    transcript: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    round_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    diagnosis: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
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
