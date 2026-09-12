"""users.borderless_user_id — CAR-103 Borderless account mapping key."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "020_user_borderless_user_id"
down_revision: Union[str, None] = "019_embed_allowlist"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("borderless_user_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "uq_users_borderless_user_id",
        "users",
        ["borderless_user_id"],
        unique=True,
        postgresql_where=sa.text("borderless_user_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_users_borderless_user_id", table_name="users")
    op.drop_column("users", "borderless_user_id")
