"""operators table + email_otps.provider namespace (CAR-75)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "015_operators"
down_revision: Union[str, None] = "014_revoked_token_jtis"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "operators",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("desk_roles", sa.String(length=16), nullable=False, server_default="both"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_operators_email", "operators", ["email"], unique=True)

    op.add_column(
        "email_otps",
        sa.Column(
            "provider",
            sa.String(length=16),
            nullable=False,
            server_default="email",
        ),
    )


def downgrade() -> None:
    op.drop_column("email_otps", "provider")
    op.drop_index("ix_operators_email", table_name="operators")
    op.drop_table("operators")
