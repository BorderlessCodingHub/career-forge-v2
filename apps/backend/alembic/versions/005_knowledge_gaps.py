"""knowledge_gaps ledger — HAC-67 adaptive memory."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "005_knowledge_gaps"
down_revision: Union[str, None] = "004_checklist_progress"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "knowledge_gaps",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("skill_node_id", sa.String(length=64), nullable=False),
        sa.Column("concept", sa.String(length=160), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False, server_default="medium"),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("suggested_remediation", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="open"),
        sa.Column("source", sa.String(length=32), nullable=False, server_default="mock_interview"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["skill_node_id"], ["skill_nodes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id", "skill_node_id", "concept", name="uq_knowledge_gap_user_node_concept"
        ),
    )
    op.create_index(
        "ix_knowledge_gaps_user_id", "knowledge_gaps", ["user_id"], unique=False
    )
    op.create_index(
        "ix_knowledge_gaps_skill_node_id", "knowledge_gaps", ["skill_node_id"], unique=False
    )
    op.create_index(
        "ix_knowledge_gaps_status", "knowledge_gaps", ["status"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_knowledge_gaps_status", table_name="knowledge_gaps")
    op.drop_index("ix_knowledge_gaps_skill_node_id", table_name="knowledge_gaps")
    op.drop_index("ix_knowledge_gaps_user_id", table_name="knowledge_gaps")
    op.drop_table("knowledge_gaps")
