"""Access overrides, Stripe status, and append-only audit (CAR-77)."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "016_operator_access"
down_revision: Union[str, None] = "015_operators"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("operator_membership_label", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("stripe_subscription_status", sa.String(length=32), nullable=True),
    )
    op.create_table(
        "operator_access_audit",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("actor_type", sa.String(length=16), nullable=False),
        sa.Column(
            "operator_id",
            sa.BigInteger(),
            sa.ForeignKey("operators.id"),
            nullable=True,
        ),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=False,
        ),
        sa.Column("learner_email", sa.String(length=255), nullable=False),
        sa.Column("field", sa.String(length=64), nullable=False),
        sa.Column("before_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("after_value", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_operator_access_audit_actor_type",
        "operator_access_audit",
        ["actor_type"],
    )
    op.create_index(
        "ix_operator_access_audit_learner_id",
        "operator_access_audit",
        ["learner_id"],
    )
    op.create_index(
        "ix_operator_access_audit_created_at",
        "operator_access_audit",
        ["created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_operator_access_audit_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'operator_access_audit is append-only';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER operator_access_audit_append_only
        BEFORE UPDATE OR DELETE ON operator_access_audit
        FOR EACH ROW EXECUTE FUNCTION reject_operator_access_audit_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER operator_access_audit_append_only ON operator_access_audit"
    )
    op.execute("DROP FUNCTION reject_operator_access_audit_mutation()")
    op.drop_index(
        "ix_operator_access_audit_created_at",
        table_name="operator_access_audit",
    )
    op.drop_index(
        "ix_operator_access_audit_learner_id",
        table_name="operator_access_audit",
    )
    op.drop_index(
        "ix_operator_access_audit_actor_type",
        table_name="operator_access_audit",
    )
    op.drop_table("operator_access_audit")
    op.drop_column("users", "stripe_subscription_status")
    op.drop_column("users", "operator_membership_label")
