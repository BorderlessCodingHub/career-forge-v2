"""Membership soft label — stub allowlist + HTTP client (CAR-45).

Seams: MembershipClient.lookup(email) → MembershipRecord;
OTP verify persists label/entitled on the user (read via GET /me/profile).
"""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from career_forge.config import settings
from career_forge.services import otp as otp_service
from career_forge.services.membership import (
    BorderlessMembershipClient,
    MembershipRecord,
    StubMembershipClient,
    apply_membership_label,
    parse_stub_allowlist,
)


def test_stub_unknown_email_is_external() -> None:
    client = StubMembershipClient(allowlist={"ana@borderless.com": "base"})
    record = client.lookup("unknown@example.com")
    assert record == MembershipRecord(active=False, program=None)
    assert record.label == "external"
    assert record.entitled is False


def test_stub_active_base_is_entitled() -> None:
    client = StubMembershipClient(allowlist={"ana@borderless.com": "base"})
    record = client.lookup("ana@borderless.com")
    assert record == MembershipRecord(active=True, program="base")
    assert record.label == "base"
    assert record.entitled is True


def test_stub_active_psp_is_entitled() -> None:
    client = StubMembershipClient(allowlist={"psp@borderless.com": "psp"})
    record = client.lookup("PSP@borderless.com")
    assert record.label == "psp"
    assert record.entitled is True


def test_stub_inactive_program_is_external() -> None:
    record = MembershipRecord(active=False, program="base")
    assert record.label == "external"
    assert record.entitled is False


def test_parse_stub_allowlist_maps_email_to_program() -> None:
    parsed = parse_stub_allowlist(
        "ana@borderless.com:base, psp@borderless.com:psp, bad:skip, x@y.com:gold",
    )
    assert parsed == {
        "ana@borderless.com": "base",
        "psp@borderless.com": "psp",
    }


def test_http_client_maps_active_base_member() -> None:
    def fetch(url: str, token: str, timeout: float) -> str:
        assert token == "staging-token"
        assert "email=ana%40borderless.com" in url
        assert url.startswith("https://members.example/v1/members?")
        assert timeout == 5.0
        return json.dumps({"active": True, "program": "base"})

    client = BorderlessMembershipClient(
        url="https://members.example/v1/members",
        token="staging-token",
        fetch=fetch,
    )
    record = client.lookup("ana@borderless.com")
    assert record == MembershipRecord(active=True, program="base")
    assert record.label == "base"
    assert record.entitled is True


def test_http_client_unknown_or_inactive_is_external() -> None:
    def fetch(url: str, token: str, timeout: float) -> str:
        return json.dumps({"active": False, "program": "psp"})

    client = BorderlessMembershipClient(
        url="https://members.example/members",
        token="t",
        fetch=fetch,
    )
    record = client.lookup("ext@example.com")
    assert record.label == "external"
    assert record.entitled is False


def test_http_client_fail_open_on_error() -> None:
    def fetch(url: str, token: str, timeout: float) -> str:
        raise OSError("connection refused")

    client = BorderlessMembershipClient(
        url="https://members.example/members",
        token="t",
        fetch=fetch,
    )
    record = client.lookup("ana@borderless.com")
    assert record == MembershipRecord(active=False, program=None)
    assert record.label == "external"


def test_http_client_invalid_payload_is_external() -> None:
    def fetch(url: str, token: str, timeout: float) -> str:
        return json.dumps({"active": True, "program": "gold"})

    client = BorderlessMembershipClient(
        url="https://members.example/members",
        token="t",
        fetch=fetch,
    )
    record = client.lookup("ana@borderless.com")
    assert record.label == "external"
    assert record.entitled is False


def test_apply_membership_fail_open_when_http_misconfigured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "membership_backend", "http")
    monkeypatch.setattr(settings, "borderless_members_url", "")
    monkeypatch.setattr(settings, "borderless_members_token", "")

    class _User:
        membership_label = "base"
        membership_entitled = True

    user = _User()
    record = apply_membership_label(user, "ana@borderless.com")  # type: ignore[arg-type]
    assert record.label == "external"
    assert user.membership_label == "external"
    assert user.membership_entitled is False


def _auth_headers(raw_client: TestClient, external_id: str) -> dict[str, str]:
    res = raw_client.post("/auth/anon/mint", json={"external_id": external_id})
    assert res.status_code == 200
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


def test_otp_verify_writes_base_label_and_entitled(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "membership_backend", "stub")
    monkeypatch.setattr(
        settings,
        "membership_stub_allowlist",
        "base-pilot@example.com:base",
    )
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "121212")
    headers = _auth_headers(raw_client, "user-member-base")

    assert (
        raw_client.post(
            "/auth/otp/request",
            json={"email": "base-pilot@example.com"},
            headers=headers,
        ).status_code
        == 200
    )
    verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": "base-pilot@example.com", "code": "121212"},
        headers=headers,
    )
    assert verify.status_code == 200

    profile = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {verify.json()['access_token']}"},
    )
    assert profile.status_code == 200
    body = profile.json()
    assert body["membership_label"] == "base"
    assert body["membership_entitled"] is True


def test_otp_verify_unknown_email_is_external(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "membership_backend", "stub")
    monkeypatch.setattr(settings, "membership_stub_allowlist", "")
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "343434")
    headers = _auth_headers(raw_client, "user-member-ext")

    raw_client.post(
        "/auth/otp/request",
        json={"email": "external-pilot@example.com"},
        headers=headers,
    )
    verify = raw_client.post(
        "/auth/otp/verify",
        json={"email": "external-pilot@example.com", "code": "343434"},
        headers=headers,
    )
    assert verify.status_code == 200

    profile = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {verify.json()['access_token']}"},
    )
    body = profile.json()
    assert body["membership_label"] == "external"
    assert body["membership_entitled"] is False


def test_otp_login_reresolves_label_on_existing_owner(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "membership_backend", "stub")
    monkeypatch.setattr(settings, "membership_stub_allowlist", "")
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "565656")
    owner = _auth_headers(raw_client, "user-member-reresolve")

    raw_client.post(
        "/auth/otp/request",
        json={"email": "flip@example.com"},
        headers=owner,
    )
    first = raw_client.post(
        "/auth/otp/verify",
        json={"email": "flip@example.com", "code": "565656"},
        headers=owner,
    )
    assert first.status_code == 200
    assert first.json()["status"] == "promoted"

    empty = raw_client.get(
        "/me/profile",
        headers={"Authorization": f"Bearer {first.json()['access_token']}"},
    )
    assert empty.json()["membership_label"] == "external"

    monkeypatch.setattr(settings, "membership_stub_allowlist", "flip@example.com:psp")
    monkeypatch.setattr(otp_service, "_generate_otp_code", lambda: "787878")
    anon = _auth_headers(raw_client, "user-member-reresolve-anon")
    raw_client.post(
        "/auth/otp/request",
        json={"email": "flip@example.com"},
        headers=anon,
    )
    conflict = raw_client.post(
        "/auth/otp/verify",
        json={"email": "flip@example.com", "code": "787878"},
        headers=anon,
    )
    assert conflict.status_code == 409
    token = conflict.json()["detail"]["existing"]["access_token"]

    profile = raw_client.get("/me/profile", headers={"Authorization": f"Bearer {token}"})
    body = profile.json()
    assert body["membership_label"] == "psp"
    assert body["membership_entitled"] is True
