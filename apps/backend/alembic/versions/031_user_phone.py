"""users.phone — LABS01-168 optional contact number."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "031_user_phone"
down_revision: Union[str, None] = "030_diagnosis_session_provider"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=16), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "phone")
