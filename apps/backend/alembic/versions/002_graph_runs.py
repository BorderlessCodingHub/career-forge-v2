"""graph_runs table — HAC-32 GraphRun persistence stub."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "002_graph_runs"
down_revision: Union[str, None] = "001_initial_skill_graph"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "graph_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("graph_name", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("input", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("output", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("raw_events", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "normalized_events",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("error", sa.Text(), nullable=True),
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
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_graph_runs_graph_name", "graph_runs", ["graph_name"])
    op.create_index("ix_graph_runs_user_id", "graph_runs", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_graph_runs_user_id", table_name="graph_runs")
    op.drop_index("ix_graph_runs_graph_name", table_name="graph_runs")
    op.drop_table("graph_runs")
