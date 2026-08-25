"""Access desk writes + append-only audit (CAR-77).

Seams: PATCH/GET /operator/access/*, membership resolution, Stripe inbound writes.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from sqlalchemy.exc import DBAPIError

from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmailAudit
from career_forge.db.models.usage_monthly import GLOBAL_USAGE_USER_ID, UsageMonthly
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.services.cost_guard import current_year_month
from career_forge.services.entitlement import require_diagnosis_entitlement
from career_forge.services import operator_otp as operator_otp_service


@pytest.fixture
def access_operator(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    monkeypatch.setattr(
        settings,
        "operator_allowlist",
        "access@borderless.com:access,editor@borderless.com:editor",
    )
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "424242")
    requested = raw_client.post(
        "/operator/auth/otp/request",
        json={"email": "access@borderless.com"},
    )
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": "access@borderless.com", "code": "424242"},
    )
    assert verified.status_code == 200, verified.text
    return raw_client


def _create_learner(external_id: str, email: str) -> None:
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.email = email
        user.membership_label = "external"
        user.membership_entitled = False
        user.operator_membership_label = None
        user.billing_entitled = False
        user.stripe_customer_id = None
        user.stripe_subscription_id = None
        user.stripe_subscription_status = None
        session.commit()


def _learner_identity(prefix: str) -> tuple[str, str]:
    suffix = uuid.uuid4().hex
    return f"{prefix}-{suffix}", f"{prefix}-{suffix}@example.com"


def _login_operator(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    *,
    email: str,
) -> None:
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "525252")
    requested = raw_client.post("/operator/auth/otp/request", json={"email": email})
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": "525252"},
    )
    assert verified.status_code == 200, verified.text


def test_access_write_changes_membership_and_billing_with_field_audit(
    access_operator: TestClient,
) -> None:
    external_id, email = _learner_identity("car77-write")
    _create_learner(external_id, email)

    response = access_operator.patch(
        f"/operator/access/learners/{email}",
        json={"operator_membership_label": "base", "billing_entitled": True},
    )

    assert response.status_code == 200, response.text
    assert response.json() == {
        "email": email,
        "operator_membership_label": "base",
        "membership_label": "base",
        "membership_entitled": True,
        "billing_entitled": True,
        "pilot_email_listed": False,
        "stripe_subscription_status": None,
        "stripe_billing_locked": False,
    }

    trail = access_operator.get(f"/operator/access/learners/{email}/audit")
    assert trail.status_code == 200, trail.text
    entries = trail.json()["entries"]
    assert [entry["field"] for entry in entries] == [
        "billing_entitled",
        "operator_membership_label",
    ]
    assert entries[0]["before"] is False
    assert entries[0]["after"] is True
    assert entries[1]["before"] is None
    assert entries[1]["after"] == "base"
    assert all(entry["actor_type"] == "operator" for entry in entries)
    assert all(entry["actor_email"] == "access@borderless.com" for entry in entries)
    assert all(entry["learner_email"] == email for entry in entries)


def test_access_operator_manages_pre_otp_pilot_email_idempotently_with_audit(
    access_operator: TestClient,
) -> None:
    _external_id, email = _learner_identity("car87-pre-otp")

    first = access_operator.post(
        "/operator/access/pilot-emails",
        json={"email": email.upper()},
    )
    second = access_operator.post(
        "/operator/access/pilot-emails",
        json={"email": email},
    )

    assert first.status_code == 200, first.text
    assert second.status_code == 200, second.text
    assert first.json()["email"] == email
    assert second.json()["email"] == email
    assert access_operator.get(f"/operator/access/learners/{email}").status_code == 404
    listed = access_operator.get("/operator/access/pilot-emails")
    assert listed.status_code == 200, listed.text
    assert email in [row["email"] for row in listed.json()["emails"]]

    external_id = f"otp-{uuid.uuid4().hex}"
    _create_learner(external_id, email)
    learner = access_operator.get(f"/operator/access/learners/{email}")
    assert learner.status_code == 200, learner.text
    assert learner.json()["pilot_email_listed"] is True
    with SessionLocal() as session:
        decision = require_diagnosis_entitlement(session, external_id)
        audit = list(
            session.scalars(
                select(BillingPilotEmailAudit)
                .where(BillingPilotEmailAudit.email == email)
                .order_by(BillingPilotEmailAudit.id)
            )
        )
    assert decision.allowed is True
    assert decision.reason == "billing"
    assert [(row.action, row.actor_email) for row in audit] == [
        ("add", "access@borderless.com")
    ]
    with SessionLocal() as session:
        with pytest.raises(DBAPIError):
            session.execute(
                delete(BillingPilotEmailAudit).where(
                    BillingPilotEmailAudit.email == email
                )
            )


def test_pilot_email_revoke_does_not_clear_stripe_or_billing_flag(
    access_operator: TestClient,
) -> None:
    external_id, email = _learner_identity("car87-revoke")
    _create_learner(external_id, email)
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.billing_entitled = True
        user.stripe_subscription_status = "active"
        session.commit()
    added = access_operator.post(
        "/operator/access/pilot-emails",
        json={"email": email},
    )
    assert added.status_code == 200, added.text

    removed = access_operator.delete(f"/operator/access/pilot-emails/{email}")
    missing = access_operator.delete(f"/operator/access/pilot-emails/{email}")
    invalid = access_operator.delete("/operator/access/pilot-emails/not-an-email")

    assert removed.status_code == 204, removed.text
    assert missing.status_code == 204, missing.text
    assert invalid.status_code == 422, invalid.text
    state = access_operator.get(f"/operator/access/learners/{email}").json()
    assert state["pilot_email_listed"] is False
    assert state["billing_entitled"] is True
    assert state["stripe_subscription_status"] == "active"
    with SessionLocal() as session:
        audit = list(
            session.scalars(
                select(BillingPilotEmailAudit)
                .where(BillingPilotEmailAudit.email == email)
                .order_by(BillingPilotEmailAudit.id)
            )
        )
    assert [row.action for row in audit] == ["add", "delete"]


def test_access_operator_can_read_current_month_cost_pool(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "monthly_api_budget_brl", 500.0)
    year_month = current_year_month()
    with SessionLocal() as session:
        row = session.get(
            UsageMonthly,
            {"year_month": year_month, "user_id": GLOBAL_USAGE_USER_ID},
        )
        if row is None:
            row = UsageMonthly(
                year_month=year_month,
                user_id=GLOBAL_USAGE_USER_ID,
                billable_runs=0,
                forge_runs=0,
                estimated_cost_brl=0.0,
            )
            session.add(row)
        row.billable_runs = 12
        row.forge_runs = 3
        row.estimated_cost_brl = 187.4
        session.commit()

    response = access_operator.get("/operator/access/cost-pool")

    assert response.status_code == 200, response.text
    assert response.json() == {
        "year_month": year_month,
        "estimated_cost_brl": 187.4,
        "budget_brl": 500.0,
        "billable_runs": 12,
        "forge_runs": 3,
    }


def test_clearing_membership_override_restores_borderless_resolution(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    external_id, email = _learner_identity("car77-clear")
    _create_learner(external_id, email)
    monkeypatch.setattr(settings, "membership_backend", "stub")
    monkeypatch.setattr(settings, "membership_stub_allowlist", f"{email}:base")

    set_override = access_operator.patch(
        f"/operator/access/learners/{email}",
        json={"operator_membership_label": "psp"},
    )
    assert set_override.status_code == 200, set_override.text
    assert set_override.json()["membership_label"] == "psp"

    cleared = access_operator.patch(
        f"/operator/access/learners/{email}",
        json={"operator_membership_label": None},
    )

    assert cleared.status_code == 200, cleared.text
    assert cleared.json()["operator_membership_label"] is None
    assert cleared.json()["membership_label"] == "base"
    assert cleared.json()["membership_entitled"] is True
    trail = access_operator.get(f"/operator/access/learners/{email}/audit").json()["entries"]
    assert trail[0]["field"] == "operator_membership_label"
    assert trail[0]["before"] == "psp"
    assert trail[0]["after"] is None
    assert trail[0]["action"] == "clear"


def test_active_stripe_subscription_blocks_operator_billing_revoke(
    access_operator: TestClient,
) -> None:
    external_id, email = _learner_identity("car77-stripe-lock")
    _create_learner(external_id, email)
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.billing_entitled = True
        user.stripe_subscription_id = "sub_locked"
        user.stripe_subscription_status = "active"
        session.commit()

    response = access_operator.patch(
        f"/operator/access/learners/{email}",
        json={"billing_entitled": False},
    )

    assert response.status_code == 409, response.text
    state = access_operator.get(f"/operator/access/learners/{email}")
    assert state.status_code == 200, state.text
    assert state.json()["billing_entitled"] is True
    assert state.json()["stripe_billing_locked"] is True
    assert access_operator.get(
        f"/operator/access/learners/{email}/audit"
    ).json()["entries"] == []


def test_active_stripe_subscription_is_read_only_even_with_stale_false_row(
    access_operator: TestClient,
) -> None:
    external_id, email = _learner_identity("car77-stripe-read-only")
    _create_learner(external_id, email)
    with SessionLocal() as session:
        user = ensure_user(session, external_id)
        user.billing_entitled = False
        user.stripe_subscription_id = "sub_read_only"
        user.stripe_subscription_status = "trialing"
        session.commit()

    response = access_operator.patch(
        f"/operator/access/learners/{email}",
        json={"billing_entitled": True},
    )

    assert response.status_code == 409, response.text
    state = access_operator.get(f"/operator/access/learners/{email}").json()
    assert state["billing_entitled"] is False
    assert state["stripe_billing_locked"] is True


def test_editor_only_operator_cannot_read_or_write_access(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        settings,
        "operator_allowlist",
        "access@borderless.com:access,editor@borderless.com:editor",
    )
    _login_operator(raw_client, monkeypatch, email="editor@borderless.com")
    external_id, email = _learner_identity("car77-editor-forbidden")
    _create_learner(external_id, email)

    read = raw_client.get(f"/operator/access/learners/{email}")
    cost_pool = raw_client.get("/operator/access/cost-pool")
    write = raw_client.patch(
        f"/operator/access/learners/{email}",
        json={"billing_entitled": True},
    )
    pilot_list = raw_client.get("/operator/access/pilot-emails")
    pilot_add = raw_client.post(
        "/operator/access/pilot-emails",
        json={"email": email},
    )
    pilot_delete = raw_client.delete(f"/operator/access/pilot-emails/{email}")
    trail = raw_client.get(f"/operator/access/learners/{email}/audit")

    assert read.status_code == 403
    assert cost_pool.status_code == 403
    assert write.status_code == 403
    assert pilot_list.status_code == 403
    assert pilot_add.status_code == 403
    assert pilot_delete.status_code == 403
    assert trail.status_code == 403
    assert read.json()["detail"]["code"] == "access_desk_forbidden"

