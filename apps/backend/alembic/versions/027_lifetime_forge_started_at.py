"""lifetime forge start — CAR-130 one forge then the subscription."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "027_lifetime_forge_started_at"
down_revision: Union[str, None] = "026_email_confirmed_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("lifetime_forge_started_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "lifetime_forge_started_at")
