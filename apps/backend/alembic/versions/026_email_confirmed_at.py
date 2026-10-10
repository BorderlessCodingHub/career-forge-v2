"""email confirmed at — CAR-129 magic link."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "026_email_confirmed_at"
down_revision: Union[str, None] = "025_career_forge_password"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("email_confirmed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.execute(
        "UPDATE users SET email_confirmed_at = created_at "
        "WHERE password_hash IS NOT NULL AND email_confirmed_at IS NULL"
    )


def downgrade() -> None:
    op.drop_column("users", "email_confirmed_at")
