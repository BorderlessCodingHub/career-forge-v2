"""users.membership_label + membership_entitled — CAR-45 soft label."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "012_user_membership"
down_revision: Union[str, None] = "011_email_otps"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "membership_label",
            sa.String(length=16),
            nullable=False,
            server_default="external",
        ),
    )
    op.add_column(
        "users",
        sa.Column(
            "membership_entitled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "membership_entitled")
    op.drop_column("users", "membership_label")
