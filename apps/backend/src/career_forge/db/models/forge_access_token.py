"""forge_access_tokens — share / resume deep-links (CAR-27 / ADR-003)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from career_forge.db.base import Base

ROLE_SHARE = "share"
ROLE_RESUME = "resume"


class ForgeAccessToken(Base):
    """Opaque token row — URL carries raw token; DB stores SHA-256 hash only."""

    __tablename__ = "forge_access_tokens"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    artifact_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("forge_artifacts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    artifact: Mapped["ForgeArtifact"] = relationship(back_populates="access_tokens")


from career_forge.db.models.forge_artifact import ForgeArtifact  # noqa: E402
