"""Operator-owned metadata sidecar for git-owned canonical skill content."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from career_forge.db.base import Base


class SkillContent(Base):
    __tablename__ = "skill_content"

    skill_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    published: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
