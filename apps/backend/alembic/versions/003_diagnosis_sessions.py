"""diagnosis_sessions table — HAC-44 multi-turn interview persistence."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_diagnosis_sessions"
down_revision: Union[str, None] = "002_graph_runs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "diagnosis_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("intake", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("belief_state", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("cv_signals", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("transcript", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("round_count", sa.Integer(), nullable=False),
        sa.Column("diagnosis", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_diagnosis_sessions_user_id", "diagnosis_sessions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_diagnosis_sessions_user_id", table_name="diagnosis_sessions")
    op.drop_table("diagnosis_sessions")
