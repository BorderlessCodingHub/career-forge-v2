from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SkillNode(Base):
    """Static catalog node — seeded from data/roadmap.json."""

    __tablename__ = "skill_nodes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    track_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str | None] = mapped_column(String(32), nullable=True)
    side: Mapped[str | None] = mapped_column(String(8), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    prerequisites: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    outcomes: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rubric: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user_instances: Mapped[list["UserSkillNode"]] = relationship(
        back_populates="skill_node", cascade="all, delete-orphan"
    )


from app.models.user_skill_node import UserSkillNode  # noqa: E402
