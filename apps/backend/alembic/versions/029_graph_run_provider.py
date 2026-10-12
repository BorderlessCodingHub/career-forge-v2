"""graph_runs.run_provider — CAR-136 capture at GraphRun creation."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "029_graph_run_provider"
down_revision: Union[str, None] = "028_provider_switch"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "graph_runs",
        sa.Column(
            "run_provider",
            sa.String(length=16),
            nullable=False,
            server_default="direct",
        ),
    )
    op.create_check_constraint(
        "ck_graph_runs_run_provider",
        "graph_runs",
        "run_provider IN ('direct', 'gateway')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_graph_runs_run_provider", "graph_runs", type_="check")
    op.drop_column("graph_runs", "run_provider")
