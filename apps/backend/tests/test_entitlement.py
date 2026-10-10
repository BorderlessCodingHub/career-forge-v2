"""Product entitlement — one forge, then the subscription (CAR-130)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.run import GraphRun, InMemoryGraphRunStore, get_graph_run_store
from career_forge.config import settings
from career_forge.db.models.billing_pilot_email import BillingPilotEmail
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID
from career_forge.auth.providers import get_auth_provider
from career_forge.errors import (
    MONTHLY_FORGE_CEILING_MESSAGE,
    PAYWALL_MESSAGE,
    MonthlyForgeCeilingError,
    PaywallError,
)
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.db.models.usage_monthly import GLOBAL_USAGE_USER_ID
from career_forge.services.cost_guard import CostGuard, InMemoryUsageStore, current_year_month
from career_forge.services.cost_guard import set_cost_guard
from career_forge.services.entitlement import ForgeHistory, evaluate_entitlement


def test_unpaid_external_may_start_one_forge_before_any_completion() -> None:
    decision = evaluate_entitlement(
        user_id="ext-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="ext@example.com",
        forge_count=0,
        forge_history=ForgeHistory(),
    )
    assert decision.allowed is True
    assert decision.reason == "allowance"


def test_spent_allowance_paywalls_until_a_subscription() -> None:
    decision = evaluate_entitlement(
        user_id="ext-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="ext@example.com",
        forge_count=1,
        forge_history=ForgeHistory(external_start=True),
    )
    assert decision.allowed is False
    assert decision.reason == "paywall"


def test_completed_forge_spends_the_allowance_even_without_an_external_start() -> None:
    decision = evaluate_entitlement(
        user_id="ext-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="ext@example.com",
        forge_count=1,
        forge_history=ForgeHistory(completed_any=True),
    )
    assert decision.allowed is False
    assert decision.reason == "paywall"


def test_active_base_never_hits_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="base-1",
        membership_label="base",
        membership_entitled=True,
        billing_entitled=False,
        email="ana@borderless.com",
        forge_count=8,
    )
    assert decision.allowed is True
    assert decision.reason == "membership"


def test_active_psp_never_hits_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="psp-1",
        membership_label="psp",
        membership_entitled=True,
        billing_entitled=False,
        email="psp@borderless.com",
        forge_count=3,
    )
    assert decision.allowed is True
    assert decision.reason == "membership"


def test_included_program_refuses_the_third_completed_forge_this_utc_month() -> None:
    decision = evaluate_entitlement(
        user_id="base-1",
        membership_label="base",
        membership_entitled=True,
        billing_entitled=False,
        email="ana@borderless.com",
        forge_count=2,
        forge_history=ForgeHistory(completed_any=True, completed_this_utc_month=2),
    )
    assert decision.allowed is False
    assert decision.reason == "monthly_ceiling"


def test_included_program_allows_a_forge_after_the_utc_month_turns() -> None:
    decision = evaluate_entitlement(
        user_id="psp-1",
        membership_label="psp",
        membership_entitled=True,
        billing_entitled=False,
        email="psp@borderless.com",
        forge_count=2,
        forge_history=ForgeHistory(completed_any=True, completed_this_utc_month=0),
    )
    assert decision.allowed is True
    assert decision.reason == "membership"


def test_subscribed_external_sits_outside_the_monthly_ceiling() -> None:
    decision = evaluate_entitlement(
        user_id="paid-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=True,
        email="paid@example.com",
        forge_count=4,
        forge_history=ForgeHistory(
            completed_any=True,
            external_start=True,
            completed_this_utc_month=3,
        ),
    )
    assert decision.allowed is True
    assert decision.reason == "billing"


def test_stripe_billing_entitled_external_skips_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="paid-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=True,
        email="paid@example.com",
        forge_count=4,
    )
    assert decision.allowed is True
    assert decision.reason == "billing"


def test_active_stripe_subscription_wins_over_stale_billing_row() -> None:
    decision = evaluate_entitlement(
        user_id="paid-active-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        stripe_subscription_status="active",
        email="paid-active@example.com",
        forge_count=4,
    )
    assert decision.allowed is True
    assert decision.reason == "billing"
    assert decision.billing_entitled is True


def test_pilot_listed_email_skips_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="pilot-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="pilot@example.com",
        forge_count=2,
        pilot_email_listed=True,
    )
    assert decision.allowed is True
    assert decision.reason == "billing"


def test_demo_ana_is_excluded_from_paywall() -> None:
    decision = evaluate_entitlement(
        user_id=DEMO_ANA_EXTERNAL_ID,
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email=None,
        forge_count=9,
        run_input={},
    )
    assert decision.allowed is True
    assert decision.reason == "excluded"


def test_synthetic_gate_run_is_excluded_from_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="gate-runner",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email=None,
        forge_count=2,
        run_input={"_cost": {"synthetic_gate": True}},
    )
    assert decision.allowed is True
    assert decision.reason == "excluded"


def _diagnosis_payload(user_id: str) -> dict:
    diagnosis = build_diagnosis_response(
        DiagnosisRequest(
            goal_id="rag-engineer",
            motivation="I want to ship grounded RAG systems in production.",
            answers={"level": "beginner"},
        ),
    )
    return {
        "user_id": user_id,
        "diagnosis": diagnosis.model_dump(mode="json"),
    }


def _email_auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    token = get_auth_provider().mint_email(external_id)
    return {"Authorization": f"Bearer {token}"}


def _anon_auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200, res.text
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_memory_store_counts_forge_runs_per_user() -> None:
    store = InMemoryGraphRunStore()
    store.save(GraphRun(graph_name="roadmap_forge", user_id="a", input={}))
    store.save(GraphRun(graph_name="roadmap_forge", user_id="a", input={}))
    store.save(GraphRun(graph_name="mentor", user_id="a", input={}))
    store.save(GraphRun(graph_name="roadmap_forge", user_id="b", input={}))
    assert store.count_for_user("a", graph_name="roadmap_forge") == 2
    assert store.count_for_user("b", graph_name="roadmap_forge") == 1
    assert store.count_for_user("a", graph_name="mentor") == 1


def _previous_utc_month(now: datetime) -> datetime:
    month = now.month - 1
    year = now.year
    if month == 0:
        month = 12
        year -= 1
    return now.replace(year=year, month=month, day=1)


def _save_forge(user_id: str, *, status: str, when: datetime | None = None) -> None:
    get_graph_run_store().save(
        GraphRun(
            graph_name="roadmap_forge",
            user_id=user_id,
            status=status,  # type: ignore[arg-type]
            completed_at=when if status == "completed" else None,
            input={"goal_id": "rag-engineer"},
        )
    )


def test_external_first_forge_is_allowed_and_the_next_is_paywalled(
    raw_client: TestClient,
) -> None:
    user = "paywall-ext-http"
    headers = _email_auth_headers(raw_client, user)
    body = _diagnosis_payload(user)

    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text

    other_goal = _diagnosis_payload(user)
    other_goal["diagnosis"]["goal_id"] = "agent-engineer"
    second = raw_client.post("/forge/runs", json=other_goal, headers=headers)
    assert second.status_code == 402, second.text
    detail = second.json()["detail"]
    assert detail["code"] == "paywall"
    assert detail["message"] == PAYWALL_MESSAGE
    assert detail["checkout_available"] is False

    roadmap = raw_client.get("/roadmap/current", headers=headers)
    assert roadmap.status_code == 200, roadmap.text


def test_base_member_forge_skips_paywall(
    raw_client: TestClient,
) -> None:
    user = "paywall-base-http"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()

    body = _diagnosis_payload(user)
    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text
    second = raw_client.post("/forge/runs", json=body, headers=headers)
    assert second.status_code == 202, second.text


def test_legacy_env_allowlist_is_ignored_at_runtime(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("ENTITLEMENT_BILLING_ALLOWLIST", "pilot@example.com")
    user = "paywall-allow-http"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = "pilot@example.com"
        row.membership_label = "external"
        row.membership_entitled = False
        session.commit()

    body = _diagnosis_payload(user)
    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text
    second = raw_client.post("/forge/runs", json=body, headers=headers)
    assert second.status_code == 402, second.text


def test_database_pilot_email_skips_http_paywall(raw_client: TestClient) -> None:
    user = "paywall-db-pilot-http"
    email = "db-pilot@example.com"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = email
        row.membership_label = "external"
        row.membership_entitled = False
        session.merge(BillingPilotEmail(email=email))
        session.commit()

    body = _diagnosis_payload(user)
    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text


def test_cost_cap_still_applies_after_entitlement(
    raw_client: TestClient,
) -> None:
    user = "paywall-cap-http"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "psp"
        row.membership_entitled = True
        session.commit()

    store = InMemoryUsageStore()
    store.increment(current_year_month(), user, forge_runs=2)
    set_cost_guard(CostGuard(store=store, cfg=settings))

    body = _diagnosis_payload(user)
    blocked = raw_client.post("/forge/runs", json=body, headers=headers)
    assert blocked.status_code == 429, blocked.text
    assert blocked.json()["detail"]["code"] == "per_user_cap"


def test_paywall_error_shape() -> None:
    err = PaywallError(checkout_available=True)
    assert err.status_code == 402
    assert err.code == "paywall"
    assert err.checkout_available is True
    assert str(err) == PAYWALL_MESSAGE
    assert "USD $7/mo" in PAYWALL_MESSAGE
    lowered = PAYWALL_MESSAGE.lower()
    assert "free forge used" not in lowered
    assert "subscribe to continue" not in lowered
    assert "start diagnosis" not in lowered


def test_password_mode_profile_base_is_included() -> None:
    decision = evaluate_entitlement(
        user_id="pw-1",
        membership_label="base",
        membership_entitled=True,
        billing_entitled=False,
        email="pw@example.com",
        forge_count=0,
        identity_method="borderless_password",
    )
    assert decision.allowed is True
    assert decision.reason == "membership"


def test_password_mode_borderless_link_without_included_label_gets_one_forge() -> None:
    decision = evaluate_entitlement(
        user_id="pw-free",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="free@example.com",
        forge_count=0,
        identity_method="borderless_password",
    )
    assert decision.allowed is True
    assert decision.reason == "allowance"


def test_password_mode_spent_external_is_paywalled() -> None:
    decision = evaluate_entitlement(
        user_id="pw-free",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="free@example.com",
        forge_count=1,
        forge_history=ForgeHistory(external_start=True),
        identity_method="borderless_password",
    )
    assert decision.allowed is False
    assert decision.reason == "paywall"


def test_password_mode_paid_external_is_allowed() -> None:
    decision = evaluate_entitlement(
        user_id="pw-paid",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=True,
        stripe_subscription_status="active",
        email="paid@example.com",
        forge_count=0,
        pilot_email_listed=True,
        identity_method="borderless_password",
    )
    assert decision.allowed is True
    assert decision.reason == "billing"


def test_password_mode_still_excludes_demo_ana() -> None:
    decision = evaluate_entitlement(
        user_id=DEMO_ANA_EXTERNAL_ID,
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email=None,
        forge_count=9,
        run_input={},
        identity_method="borderless_password",
    )
    assert decision.allowed is True
    assert decision.reason == "excluded"


def test_otp_mode_unspent_external_may_start_one_forge() -> None:
    decision = evaluate_entitlement(
        user_id="otp-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="otp@example.com",
        forge_count=0,
        identity_method="email_otp",
    )
    assert decision.allowed is True
    assert decision.reason == "allowance"


def test_password_mode_borderless_id_alone_gets_one_forge_then_the_paywall(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    user = "pw-entitled-http"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = "pw-entitled@example.com"
        row.borderless_user_id = "bl-entitled-108"
        row.membership_label = "external"
        row.membership_entitled = False
        session.commit()

    first = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert first.status_code == 202, first.text
    second = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert second.status_code == 402, second.text
    assert second.json()["detail"]["code"] == "paywall"


def test_password_mode_paid_account_without_borderless_link_is_allowed(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    user = "pw-stale-http"
    email = "pw-stale@example.com"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.email = email
        row.membership_label = "external"
        row.membership_entitled = False
        row.billing_entitled = True
        row.stripe_subscription_status = "active"
        session.merge(BillingPilotEmail(email=email))
        session.commit()

    first = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert first.status_code == 202, first.text


def test_password_mode_cost_cap_still_applies(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    user = "pw-cap-http"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.borderless_user_id = "bl-cap-108"
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()

    store = InMemoryUsageStore()
    store.increment(current_year_month(), user, forge_runs=2)
    set_cost_guard(CostGuard(store=store, cfg=settings))

    blocked = raw_client.post(
        "/forge/runs",
        json=_diagnosis_payload(user),
        headers=headers,
    )
    assert blocked.status_code == 429, blocked.text
    assert blocked.json()["detail"]["code"] == "per_user_cap"


def _interview_body(user: str) -> dict:
    return {
        "user_id": user,
        "goal_id": "rag-engineer",
        "motivation": "I want to build production RAG systems with evals.",
        "years_xp": "0-1",
    }


def test_diagnosis_repeats_until_the_forge_starts(raw_client: TestClient) -> None:
    user = "allowance-diag"
    headers = _email_auth_headers(raw_client, user)
    first = raw_client.post(
        "/diagnosis/interview/start",
        json=_interview_body(user),
        headers=headers,
    )
    assert first.status_code == 200, first.text
    second = raw_client.post(
        "/diagnosis/interview/start",
        json=_interview_body(user),
        headers=headers,
    )
    assert second.status_code == 200, second.text

    started = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert started.status_code == 202, started.text

    blocked = raw_client.post(
        "/diagnosis/interview/start",
        json=_interview_body(user),
        headers=headers,
    )
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["detail"]["code"] == "paywall"


def test_completed_base_forge_spends_the_allowance_after_becoming_external(
    raw_client: TestClient,
) -> None:
    user = "base-then-free"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()
    _save_forge(user, status="completed", when=datetime.now(UTC))
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "external"
        row.membership_entitled = False
        session.commit()

    blocked = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["detail"]["code"] == "paywall"


def test_incomplete_base_forge_does_not_spend_the_allowance(
    raw_client: TestClient,
) -> None:
    user = "base-open-forge"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()
    _save_forge(user, status="pending")
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "external"
        row.membership_entitled = False
        session.commit()

    first = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert first.status_code == 202, first.text
    second = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert second.status_code == 402, second.text


def test_cancel_does_not_restore_another_free_forge(raw_client: TestClient) -> None:
    user = "cancel-no-restore"
    headers = _email_auth_headers(raw_client, user)
    body = _diagnosis_payload(user)
    started = raw_client.post("/forge/runs", json=body, headers=headers)
    assert started.status_code == 202, started.text

    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.billing_entitled = True
        row.stripe_subscription_status = "active"
        session.commit()
    subscribed = raw_client.post("/forge/runs", json=body, headers=headers)
    assert subscribed.status_code == 202, subscribed.text

    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.billing_entitled = False
        row.stripe_subscription_status = "canceled"
        session.commit()
    blocked = raw_client.post("/forge/runs", json=body, headers=headers)
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["detail"]["code"] == "paywall"


def test_included_third_forge_waits_until_next_month_without_stripe(
    raw_client: TestClient,
) -> None:
    user = "base-month-cap"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "psp"
        row.membership_entitled = True
        session.commit()
    now = datetime.now(UTC)
    _save_forge(user, status="completed", when=now)
    _save_forge(user, status="completed", when=now)

    blocked = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert blocked.status_code == 409, blocked.text
    detail = blocked.json()["detail"]
    assert detail["code"] == "monthly_forge_ceiling"
    assert detail["message"] == MONTHLY_FORGE_CEILING_MESSAGE
    assert "checkout_available" not in detail
    lowered = detail["message"].lower()
    assert "usd" not in lowered
    assert "subscri" not in lowered
    assert "stripe" not in lowered

    diagnosis = raw_client.post(
        "/diagnosis/interview/start",
        json=_interview_body(user),
        headers=headers,
    )
    assert diagnosis.status_code == 200, diagnosis.text


def test_included_forges_from_last_month_do_not_fill_this_month(
    raw_client: TestClient,
) -> None:
    user = "base-last-month"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()
    last_month = _previous_utc_month(datetime.now(UTC))
    _save_forge(user, status="completed", when=last_month)
    _save_forge(user, status="completed", when=last_month)

    started = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert started.status_code == 202, started.text


def test_two_open_included_forges_refuse_a_third_start(raw_client: TestClient) -> None:
    user = "base-open-slots"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "base"
        row.membership_entitled = True
        session.commit()
    _save_forge(user, status="pending")
    _save_forge(user, status="running")

    blocked = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert blocked.status_code == 409, blocked.text
    assert blocked.json()["detail"]["code"] == "monthly_forge_ceiling"


def test_failed_included_forges_do_not_fill_the_month(raw_client: TestClient) -> None:
    user = "base-failed-slots"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "psp"
        row.membership_entitled = True
        session.commit()
    _save_forge(user, status="failed")
    _save_forge(user, status="failed")

    started = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert started.status_code == 202, started.text


def test_subscribed_external_is_outside_the_monthly_ceiling(
    raw_client: TestClient,
) -> None:
    user = "paid-over-ceiling"
    headers = _email_auth_headers(raw_client, user)
    with SessionLocal() as session:
        row = ensure_user(session, user)
        row.membership_label = "external"
        row.membership_entitled = False
        row.billing_entitled = True
        row.stripe_subscription_status = "active"
        session.commit()
    now = datetime.now(UTC)
    for _ in range(3):
        _save_forge(user, status="completed", when=now)

    usage = InMemoryUsageStore()
    usage.increment(current_year_month(), user, forge_runs=2)
    set_cost_guard(CostGuard(store=usage, cfg=settings))

    started = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert started.status_code == 202, started.text

    usage.increment(
        current_year_month(),
        GLOBAL_USAGE_USER_ID,
        estimated_cost_brl=settings.monthly_api_budget_brl,
    )
    pooled = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert pooled.status_code == 429, pooled.text
    assert pooled.json()["detail"]["code"] == "global_pool"


def test_checkout_appears_when_the_allowance_is_spent(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "stripe_secret_key", "sk_test")
    monkeypatch.setattr(settings, "stripe_webhook_secret", "whsec_test")
    monkeypatch.setattr(settings, "stripe_price_id", "price_test")
    user = "checkout-when-spent"
    headers = _email_auth_headers(raw_client, user)

    before = raw_client.get("/me/profile", headers=headers)
    assert before.status_code == 200, before.text
    assert before.json()["checkout_available"] is False

    started = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert started.status_code == 202, started.text
    profile = raw_client.get("/me/profile", headers=headers)
    assert profile.json()["checkout_available"] is True

    blocked = raw_client.post("/forge/runs", json=_diagnosis_payload(user), headers=headers)
    assert blocked.status_code == 402, blocked.text
    assert blocked.json()["detail"]["checkout_available"] is True


def test_monthly_ceiling_error_offers_no_checkout() -> None:
    err = MonthlyForgeCeilingError()
    assert err.status_code == 409
    assert err.code == "monthly_forge_ceiling"
    assert str(err) == MONTHLY_FORGE_CEILING_MESSAGE
    assert not hasattr(err, "checkout_available")
