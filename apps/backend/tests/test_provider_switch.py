"""Provider switch persistence and write guards (CAR-135).

Seam: GET/PUT /operator/access/provider-switch.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from sqlalchemy import delete

from career_forge.config import settings
from career_forge.db.models.provider_switch import ProviderSwitch
from career_forge.db.session import SessionLocal
from career_forge.services import operator_otp as operator_otp_service

_SWITCH = "/operator/access/provider-switch"
_ALLOWLIST = (
    "access@borderless.com:access,"
    "editor@borderless.com:editor,"
    "both@borderless.com:both"
)


def _login(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    *,
    email: str,
    allowlist: str,
) -> TestClient:
    monkeypatch.setattr(settings, "operator_allowlist", allowlist)
    monkeypatch.setattr(operator_otp_service, "_generate_otp_code", lambda: "424242")
    requested = raw_client.post("/operator/auth/otp/request", json={"email": email})
    assert requested.status_code == 200, requested.text
    verified = raw_client.post(
        "/operator/auth/otp/verify",
        json={"email": email, "code": "424242"},
    )
    assert verified.status_code == 200, verified.text
    return raw_client


@pytest.fixture(autouse=True)
def _no_stored_provider_switch() -> None:
    with SessionLocal() as session:
        session.execute(delete(ProviderSwitch))
        session.commit()


@pytest.fixture
def access_operator(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    return _login(
        raw_client,
        monkeypatch,
        email="access@borderless.com",
        allowlist=_ALLOWLIST,
    )


def test_access_operator_arms_the_provider_switch(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")

    armed = access_operator.put(_SWITCH, json={"on": True})
    again = access_operator.get(_SWITCH)

    assert armed.status_code == 200, armed.text
    body = armed.json()
    assert body["on"] is True
    assert body["run_provider"] == "gateway"
    assert body["operator_email"] == "access@borderless.com"
    assert body["written_at"]
    assert again.json() == body


def test_access_operator_disarms_the_provider_switch(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    armed = access_operator.put(_SWITCH, json={"on": True})
    assert armed.status_code == 200, armed.text

    disarmed = access_operator.put(_SWITCH, json={"on": False})
    again = access_operator.get(_SWITCH)

    assert disarmed.status_code == 200, disarmed.text
    body = disarmed.json()
    assert body["on"] is False
    assert body["run_provider"] == "direct"
    assert body["operator_email"] == "access@borderless.com"
    assert body["written_at"] != armed.json()["written_at"]
    assert again.json() == body


def test_arm_is_refused_when_the_model_gateway_key_is_missing(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    refused = access_operator.put(_SWITCH, json={"on": True})
    stored = access_operator.get(_SWITCH)

    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == (
        "The Model gateway is not configured. "
        "Set OPENROUTER_API_KEY before turning the Provider switch on."
    )
    assert stored.json()["run_provider"] == "direct"
    assert stored.json()["operator_email"] is None


def test_empty_model_gateway_key_does_not_arm_the_provider_switch(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "   ")

    refused = access_operator.put(_SWITCH, json={"on": True})
    stored = access_operator.get(_SWITCH)

    assert refused.status_code == 409, refused.text
    assert "OPENROUTER_API_KEY" in refused.json()["detail"]
    assert stored.json()["on"] is False
    assert stored.json()["operator_email"] is None


def test_disarm_is_refused_when_the_direct_provider_key_is_missing(
    access_operator: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    armed = access_operator.put(_SWITCH, json={"on": True})
    assert armed.status_code == 200, armed.text
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    refused = access_operator.put(_SWITCH, json={"on": False})
    stored = access_operator.get(_SWITCH)

    assert refused.status_code == 409, refused.text
    assert refused.json()["detail"] == (
        "The Direct provider is not configured. "
        "Set OPENAI_API_KEY before turning the Provider switch off."
    )
    assert stored.json() == armed.json()


def test_editor_alone_cannot_write_the_provider_switch(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    editor = _login(
        raw_client,
        monkeypatch,
        email="editor@borderless.com",
        allowlist=_ALLOWLIST,
    )
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")

    refused = editor.put(_SWITCH, json={"on": True})

    assert refused.status_code == 403, refused.text
    assert refused.json()["detail"]["code"] == "access_desk_forbidden"
    access = _login(
        raw_client,
        monkeypatch,
        email="access@borderless.com",
        allowlist=_ALLOWLIST,
    )
    stored = access.get(_SWITCH)
    assert stored.status_code == 200, stored.text
    assert stored.json()["run_provider"] == "direct"
    assert stored.json()["operator_email"] is None


def test_operator_who_holds_both_desks_replaces_the_recorded_write(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-test")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    access = _login(
        raw_client,
        monkeypatch,
        email="access@borderless.com",
        allowlist=_ALLOWLIST,
    )
    armed = access.put(_SWITCH, json={"on": True})
    assert armed.status_code == 200, armed.text

    both = _login(
        raw_client,
        monkeypatch,
        email="both@borderless.com",
        allowlist=_ALLOWLIST,
    )
    disarmed = both.put(_SWITCH, json={"on": False})
    again = both.get(_SWITCH)

    assert disarmed.status_code == 200, disarmed.text
    body = disarmed.json()
    assert body["on"] is False
    assert body["run_provider"] == "direct"
    assert body["operator_email"] == "both@borderless.com"
    assert body["written_at"] != armed.json()["written_at"]
    assert again.json() == body


def test_missing_row_reads_as_the_direct_provider(access_operator: TestClient) -> None:
    response = access_operator.get(_SWITCH)

    assert response.status_code == 200, response.text
    assert response.json() == {
        "on": False,
        "run_provider": "direct",
        "operator_email": None,
        "written_at": None,
    }
