"""DB-backed pilot billing emails and append-only audit (CAR-87)."""

from __future__ import annotations

import os
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "018_billing_pilot_emails"
down_revision: Union[str, None] = "017_skill_content"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _legacy_pilot_emails() -> list[str]:
    emails: set[str] = set()
    for chunk in os.getenv("ENTITLEMENT_BILLING_ALLOWLIST", "").split(","):
        email = chunk.strip().lower()
        if (
            "@" in email
            and not email.startswith("@")
            and not email.endswith("@")
            and len(email) <= 255
        ):
            emails.add(email)
    return sorted(emails)


def upgrade() -> None:
    pilot_emails = op.create_table(
        "billing_pilot_emails",
        sa.Column("email", sa.String(length=255), primary_key=True),
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
            nullable=True,
        ),
        sa.CheckConstraint(
            "email = lower(email)",
            name="ck_billing_pilot_email_lowercase",
        ),
    )
    pilot_email_audit = op.create_table(
        "billing_pilot_email_audit",
        sa.Column("id", sa.BigInteger(), sa.Identity(always=False), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=16), nullable=False),
        sa.Column(
            "operator_id",
            sa.BigInteger(),
            sa.ForeignKey("operators.id"),
            nullable=True,
        ),
        sa.Column("actor_email", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_billing_pilot_email_audit_email",
        "billing_pilot_email_audit",
        ["email"],
    )
    op.create_index(
        "ix_billing_pilot_email_audit_created_at",
        "billing_pilot_email_audit",
        ["created_at"],
    )
    op.execute(
        """
        CREATE FUNCTION reject_billing_pilot_email_audit_mutation()
        RETURNS trigger AS $$
        BEGIN
            RAISE EXCEPTION 'billing_pilot_email_audit is append-only';
        END;
        $$ LANGUAGE plpgsql
        """
    )
    op.execute(
        """
        CREATE TRIGGER billing_pilot_email_audit_append_only
        BEFORE UPDATE OR DELETE ON billing_pilot_email_audit
        FOR EACH ROW EXECUTE FUNCTION reject_billing_pilot_email_audit_mutation()
        """
    )

    emails = _legacy_pilot_emails()
    if emails:
        op.bulk_insert(
            pilot_emails,
            [
                {"email": email, "created_by_operator_id": None}
                for email in emails
            ],
        )
        op.bulk_insert(
            pilot_email_audit,
            [
                {
                    "email": email,
                    "action": "add",
                    "operator_id": None,
                    "actor_email": None,
                }
                for email in emails
            ],
        )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER billing_pilot_email_audit_append_only "
        "ON billing_pilot_email_audit"
    )
    op.execute("DROP FUNCTION reject_billing_pilot_email_audit_mutation()")
    op.drop_index(
        "ix_billing_pilot_email_audit_created_at",
        table_name="billing_pilot_email_audit",
    )
    op.drop_index(
        "ix_billing_pilot_email_audit_email",
        table_name="billing_pilot_email_audit",
    )
    op.drop_table("billing_pilot_email_audit")
    op.drop_table("billing_pilot_emails")
