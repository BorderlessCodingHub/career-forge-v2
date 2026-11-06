"""sealed Borderless OAuth refresh token — LABS01-199."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "033_borderless_refresh_token"
down_revision: Union[str, None] = "032_learner_feedback_notes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("borderless_refresh_token", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "borderless_refresh_token")
