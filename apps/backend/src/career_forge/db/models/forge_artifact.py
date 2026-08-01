"""forge_artifacts — product snapshot of completed forges (CAR-24 / ADR-003)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from career_forge.db.base import Base


class ForgeArtifact(Base):
    """Persisted forge roadmap snapshot — catalog for recovery (not graph_runs).

    ``id`` is an internal BIGSERIAL. External APIs must use ``public_id`` only.
    """

    __tablename__ = "forge_artifacts"
    __table_args__ = (UniqueConstraint("graph_run_id", name="uq_forge_artifacts_graph_run_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    public_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=False,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    graph_run_id: Mapped[str] = mapped_column(String(64), nullable=False)
    goal_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    snapshot: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="forge_artifacts")
    access_tokens: Mapped[list["ForgeAccessToken"]] = relationship(
        back_populates="artifact",
        cascade="all, delete-orphan",
    )


from career_forge.db.models.forge_access_token import ForgeAccessToken  # noqa: E402
from career_forge.db.models.user import User  # noqa: E402
