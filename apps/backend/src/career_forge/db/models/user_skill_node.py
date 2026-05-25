import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from career_forge.db.base import Base

SKILL_STATUSES = (
    "bloqueado",
    "recomendado",
    "em_estudo",
    "validar",
    "aprovado",
    "revisar",
)


class UserSkillNode(Base):
    """Per-user skill graph state — source of truth for roadmap UI."""

    __tablename__ = "user_skill_nodes"
    __table_args__ = (UniqueConstraint("user_id", "skill_node_id", name="uq_user_skill_node"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_node_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skill_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="bloqueado")
    mastery_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    priority: Mapped[str | None] = mapped_column(String(16), nullable=True)
    evidence: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="skill_nodes")
    skill_node: Mapped["SkillNode"] = relationship(back_populates="user_instances")
    validations: Mapped[list["Validation"]] = relationship(
        back_populates="user_skill_node", cascade="all, delete-orphan"
    )


from career_forge.db.models.skill_node import SkillNode  # noqa: E402
from career_forge.db.models.user import User  # noqa: E402
from career_forge.db.models.validation import Validation  # noqa: E402
