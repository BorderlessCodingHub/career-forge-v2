"""borderless profile access token and membership read latch — CAR-128."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "024_borderless_profile_access"
down_revision: Union[str, None] = "023_ui_locale"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("borderless_access_token", sa.Text(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column(
            "borderless_access_unrenewable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "membership_read_failed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "membership_read_failed_at")
    op.drop_column("users", "borderless_access_unrenewable")
    op.drop_column("users", "borderless_access_token")
