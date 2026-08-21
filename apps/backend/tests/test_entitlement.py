"""Entitlement paywall — 1 free forge then Stripe for external (CAR-46).

Seams: evaluate_entitlement(...) → EntitlementDecision;
POST /forge/runs raises PaywallError (HTTP 402) after the free forge.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from career_forge.ai.graphs.diagnosis import build_diagnosis_response
from career_forge.ai.run import GraphRun, InMemoryGraphRunStore
from career_forge.config import settings
from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal
from career_forge.demo.ana_state import DEMO_ANA_EXTERNAL_ID
from career_forge.errors import PAYWALL_MESSAGE, PaywallError
from career_forge.schemas.diagnosis import DiagnosisRequest
from career_forge.services.cost_guard import CostGuard, InMemoryUsageStore, current_year_month
from career_forge.services.cost_guard import set_cost_guard
from career_forge.services.entitlement import (
    evaluate_entitlement,
    parse_billing_allowlist,
)


def test_parse_billing_allowlist_normalizes_emails() -> None:
    parsed = parse_billing_allowlist(" Pilot@X.com , other@y.com, bad")
    assert parsed == {"pilot@x.com", "other@y.com"}


def test_external_first_forge_is_allowed() -> None:
    decision = evaluate_entitlement(
        user_id="ext-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="ext@example.com",
        forge_count=0,
    )
    assert decision.allowed is True
    assert decision.reason == "ok"


def test_external_second_forge_is_paywalled() -> None:
    decision = evaluate_entitlement(
        user_id="ext-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="ext@example.com",
        forge_count=1,
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


def test_allowlisted_email_skips_paywall() -> None:
    decision = evaluate_entitlement(
        user_id="pilot-1",
        membership_label="external",
        membership_entitled=False,
        billing_entitled=False,
        email="pilot@example.com",
        forge_count=2,
        billing_allowlist={"pilot@example.com"},
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


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
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


def test_external_second_forge_http_402(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "paywall-ext-http"
    headers = _auth_headers(raw_client, user)
    body = _diagnosis_payload(user)

    first = raw_client.post("/forge/runs", json=body, headers=headers)
    assert first.status_code == 202, first.text

    second = raw_client.post("/forge/runs", json=body, headers=headers)
    assert second.status_code == 402, second.text
    detail = second.json()["detail"]
    assert detail["code"] == "paywall"
    assert detail["message"] == PAYWALL_MESSAGE
    assert detail["checkout_available"] is False


def test_base_member_second_forge_skips_paywall(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "paywall-base-http"
    headers = _auth_headers(raw_client, user)
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


def test_allowlisted_external_skips_http_paywall(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "pilot@example.com")
    user = "paywall-allow-http"
    headers = _auth_headers(raw_client, user)
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
    assert second.status_code == 202, second.text


def test_cost_cap_still_applies_after_entitlement(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "entitlement_billing_allowlist", "")
    user = "paywall-cap-http"
    headers = _auth_headers(raw_client, user)
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
