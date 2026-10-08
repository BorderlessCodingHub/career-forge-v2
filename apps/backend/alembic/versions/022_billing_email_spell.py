"""billing email failed-charge spell — CAR-126."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "022_billing_email_spell"
down_revision: Union[str, None] = "021_roadmap_presence"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "billing_email_spell_open",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("users", "billing_email_spell_open")
