"""CAR-43 — LangSmith link columns on graph_runs."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "010_graph_runs_langsmith"
down_revision: Union[str, None] = "009_forge_access_tokens"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "graph_runs",
        sa.Column("langsmith_trace_id", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "graph_runs",
        sa.Column("actual_cost_usd", sa.Float(), nullable=True),
    )
    op.add_column(
        "graph_runs",
        sa.Column(
            "token_usage",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )
    op.create_index(
        "ix_graph_runs_langsmith_trace_id",
        "graph_runs",
        ["langsmith_trace_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_graph_runs_langsmith_trace_id", table_name="graph_runs")
    op.drop_column("graph_runs", "token_usage")
    op.drop_column("graph_runs", "actual_cost_usd")
    op.drop_column("graph_runs", "langsmith_trace_id")
