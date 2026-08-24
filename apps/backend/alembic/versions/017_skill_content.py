"""Content desk metadata sidecar (CAR-79)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "017_skill_content"
down_revision: Union[str, None] = "016_operator_access"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "skill_content",
        sa.Column(
            "skill_id",
            sa.String(length=64),
            primary_key=True,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("url", sa.Text(), nullable=True),
        sa.Column(
            "published",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("skill_content")
