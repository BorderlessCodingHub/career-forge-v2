"""provider switch — CAR-135 one stored choice."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "028_provider_switch"
down_revision: Union[str, None] = "027_lifetime_forge_started_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "provider_switch",
        sa.Column("id", sa.SmallInteger(), primary_key=True),
        sa.Column("run_provider", sa.String(length=16), nullable=False),
        sa.Column("operator_id", sa.BigInteger(), nullable=False),
        sa.Column("written_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_provider_switch_singleton"),
        sa.CheckConstraint(
            "run_provider IN ('direct', 'gateway')",
            name="ck_provider_switch_run_provider",
        ),
        sa.ForeignKeyConstraint(["operator_id"], ["operators.id"]),
    )


def downgrade() -> None:
    op.drop_table("provider_switch")
