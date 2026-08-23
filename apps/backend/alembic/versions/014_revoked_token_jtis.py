"""revoked_token_jtis — JWT jti denylist for sign-out (CAR-69)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "014_revoked_token_jtis"
down_revision: Union[str, None] = "013_user_billing"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "revoked_token_jtis",
        sa.Column("jti", sa.String(length=36), nullable=False),
        sa.Column("exp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("jti"),
    )
    op.create_index(
        "ix_revoked_token_jtis_exp",
        "revoked_token_jtis",
        ["exp"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_revoked_token_jtis_exp", table_name="revoked_token_jtis")
    op.drop_table("revoked_token_jtis")
