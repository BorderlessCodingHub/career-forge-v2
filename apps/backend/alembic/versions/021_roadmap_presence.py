"""roadmap presence and continuity send stamp — CAR-123."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "021_roadmap_presence"
down_revision: Union[str, None] = "020_user_borderless_user_id"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("roadmap_presence_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "continuity_accepted_presence_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "continuity_accepted_presence_at")
    op.drop_column("users", "roadmap_presence_at")
