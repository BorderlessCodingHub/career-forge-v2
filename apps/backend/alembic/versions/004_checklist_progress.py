"""checklist_progress on user_skill_nodes — HAC-63."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "004_checklist_progress"
down_revision: Union[str, None] = "003_diagnosis_sessions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_skill_nodes",
        sa.Column(
            "checklist_progress",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("user_skill_nodes", "checklist_progress")
