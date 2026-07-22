"""Cost instrumentation — graph_runs cost columns + usage_monthly (CAR-6)."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "007_cost_usage"
down_revision: Union[str, None] = "006_key_concepts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "graph_runs",
        sa.Column(
            "billable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
    )
    op.add_column(
        "graph_runs",
        sa.Column("exclude_reason", sa.String(length=32), nullable=True),
    )
    op.add_column(
        "graph_runs",
        sa.Column("estimated_cost_brl", sa.Float(), nullable=True),
    )

    op.create_table(
        "usage_monthly",
        sa.Column("year_month", sa.String(length=7), nullable=False),
        sa.Column("user_id", sa.String(length=64), nullable=False),
        sa.Column(
            "billable_runs",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "forge_runs",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "estimated_cost_brl",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.PrimaryKeyConstraint("year_month", "user_id"),
    )
    op.create_index(
        "ix_usage_monthly_year_month_user_id",
        "usage_monthly",
        ["year_month", "user_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_usage_monthly_year_month_user_id", table_name="usage_monthly")
    op.drop_table("usage_monthly")
    op.drop_column("graph_runs", "estimated_cost_brl")
    op.drop_column("graph_runs", "exclude_reason")
    op.drop_column("graph_runs", "billable")
