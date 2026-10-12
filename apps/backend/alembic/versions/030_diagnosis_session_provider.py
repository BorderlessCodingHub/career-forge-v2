"""diagnosis_sessions.run_provider — CAR-137 pin at session start."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "030_diagnosis_session_provider"
down_revision: Union[str, None] = "029_graph_run_provider"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "diagnosis_sessions",
        sa.Column(
            "run_provider",
            sa.String(length=16),
            nullable=False,
            server_default="direct",
        ),
    )
    op.create_check_constraint(
        "ck_diagnosis_sessions_run_provider",
        "diagnosis_sessions",
        "run_provider IN ('direct', 'gateway')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_diagnosis_sessions_run_provider",
        "diagnosis_sessions",
        type_="check",
    )
    op.drop_column("diagnosis_sessions", "run_provider")
