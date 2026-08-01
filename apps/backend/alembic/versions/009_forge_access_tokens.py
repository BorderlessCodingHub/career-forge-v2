"""forge_access_tokens — share/resume deep-link tokens (CAR-27)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "009_forge_access_tokens"
down_revision: Union[str, None] = "008_forge_artifacts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "forge_access_tokens",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("artifact_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=16), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["artifact_id"],
            ["forge_artifacts.id"],
            ondelete="CASCADE",
        ),
        sa.UniqueConstraint("token_hash", name="uq_forge_access_tokens_token_hash"),
        sa.CheckConstraint(
            "role IN ('share', 'resume')",
            name="ck_forge_access_tokens_role",
        ),
    )
    op.create_index(
        "ix_forge_access_tokens_artifact_id_role",
        "forge_access_tokens",
        ["artifact_id", "role"],
    )
    op.create_index(
        "ix_forge_access_tokens_token_hash",
        "forge_access_tokens",
        ["token_hash"],
    )


def downgrade() -> None:
    op.drop_index("ix_forge_access_tokens_token_hash", table_name="forge_access_tokens")
    op.drop_index(
        "ix_forge_access_tokens_artifact_id_role",
        table_name="forge_access_tokens",
    )
    op.drop_table("forge_access_tokens")
