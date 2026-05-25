"""SQLAlchemy model for persisted graph runs (Phase 2 wiring)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class GraphRunRecord(Base):
    """Persisted GraphRun — mirrors ``career_forge.ai.run.GraphRun``."""

    __tablename__ = "graph_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    graph_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    input: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    output: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    raw_events: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, nullable=False, default=list)
    normalized_events: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB, nullable=False, default=list
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
