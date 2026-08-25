"""Operational Reference embed allowlist and audit (CAR-89)."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "019_embed_allowlist"
down_revision: Union[str, None] = "018_billing_pilot_emails"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "embed_hosts",
        sa.Column("host", sa.String(length=253), primary_key=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "created_by_operator_id",
            sa.BigInteger(),
            sa.ForeignKey("operators.id"),
            nullable=False,
        ),
        sa.CheckConstraint("host = lower(host)", name="ck_embed_host_lowercase"),
        sa.CheckConstraint("host NOT LIKE 'www.%'", name="ck_embed_host_no_www"),
    )
    op.create_table(
        "embed_host_audit",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("host", sa.String(length=253), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column(
            "operator_id",
            sa.BigInteger(),
            sa.ForeignKey("operators.id"),
            nullable=False,
        ),
        sa.Column("actor_email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "action IN ('add', 'remove')",
            name="ck_embed_host_audit_action",
        ),
    )
    op.create_index(
        "ix_embed_host_audit_host",
        "embed_host_audit",
        ["host"],
    )
    op.create_index(
        "ix_embed_host_audit_created_at",
        "embed_host_audit",
        ["created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_embed_host_audit_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'embed_host_audit is append-only';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER embed_host_audit_append_only
        BEFORE UPDATE OR DELETE ON embed_host_audit
        FOR EACH ROW EXECUTE FUNCTION reject_embed_host_audit_mutation()
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER embed_host_audit_append_only ON embed_host_audit"
    )
    op.execute("DROP FUNCTION reject_embed_host_audit_mutation()")
    op.drop_index(
        "ix_embed_host_audit_created_at",
        table_name="embed_host_audit",
    )
    op.drop_index(
        "ix_embed_host_audit_host",
        table_name="embed_host_audit",
    )
    op.drop_table("embed_host_audit")
    op.drop_table("embed_hosts")
