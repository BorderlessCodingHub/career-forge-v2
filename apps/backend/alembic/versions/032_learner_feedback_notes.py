"""learner_feedback_notes — LABS01-170 product notes."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "032_learner_feedback_notes"
down_revision: Union[str, None] = "031_user_phone"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "learner_feedback_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("path", sa.String(length=200), nullable=True),
        sa.Column("locale", sa.String(length=8), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("replied_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
    )
    op.create_index(
        "ix_learner_feedback_notes_user_created",
        "learner_feedback_notes",
        ["user_id", "created_at"],
    )
    op.create_index(
        "ix_learner_feedback_notes_created",
        "learner_feedback_notes",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_learner_feedback_notes_created",
        table_name="learner_feedback_notes",
    )
    op.drop_index(
        "ix_learner_feedback_notes_user_created",
        table_name="learner_feedback_notes",
    )
    op.drop_table("learner_feedback_notes")
