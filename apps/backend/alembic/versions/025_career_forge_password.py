"""career forge password hash — CAR-129."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "025_career_forge_password"
down_revision: Union[str, None] = "024_borderless_profile_access"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
