import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from career_forge.db.base import Base

GAP_SEVERITIES = ("low", "medium", "high")
GAP_STATUSES = ("open", "resolved")
GAP_SOURCES = ("mock_interview", "validation")


class KnowledgeGap(Base):
    """Structured, searchable learner knowledge gap — the adaptive memory (HAC-67).

    One row per (user, skill node, concept). Written by the async gap classifier
    after a mock interview / validation; read by mentor, next mock, and the
    roadmap drawer. Resolved when a later attempt demonstrates the concept.
    """

    __tablename__ = "knowledge_gaps"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "skill_node_id", "concept", name="uq_knowledge_gap_user_node_concept"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    skill_node_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("skill_nodes.id", ondelete="CASCADE"), nullable=False, index=True
    )
    concept: Mapped[str] = mapped_column(String(160), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    suggested_remediation: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open", index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="mock_interview")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship(back_populates="knowledge_gaps")


from career_forge.db.models.user import User  # noqa: E402
