"""forge_artifacts table — CAR-24 product snapshots for forge recovery."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008_forge_artifacts"
down_revision: Union[str, None] = "007_cost_usage"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forge_artifacts",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column(
            "public_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("graph_run_id", sa.String(length=64), nullable=False),
        sa.Column("goal_id", sa.String(length=64), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column(
            "snapshot",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("graph_run_id", name="uq_forge_artifacts_graph_run_id"),
        sa.UniqueConstraint("public_id", name="uq_forge_artifacts_public_id"),
    )
    op.create_index("ix_forge_artifacts_user_id", "forge_artifacts", ["user_id"])
    op.create_index("ix_forge_artifacts_public_id", "forge_artifacts", ["public_id"])


def downgrade() -> None:
    op.drop_index("ix_forge_artifacts_public_id", table_name="forge_artifacts")
    op.drop_index("ix_forge_artifacts_user_id", table_name="forge_artifacts")
    op.drop_table("forge_artifacts")
