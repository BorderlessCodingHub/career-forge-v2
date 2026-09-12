"""CAR-102 — IDENTITY_METHOD + GET /auth/identity-mode."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from career_forge.identity_method import (
    BORDERLESS_PASSWORD,
    EMAIL_OTP,
    PILOT_ENTER,
    email_otp_required_for_legacy_clients,
    resolve_identity_method,
)
from career_forge.config import Settings, settings


def test_resolve_empty_follows_identity_email_otp() -> None:
    assert (
        resolve_identity_method(identity_method="", identity_email_otp=True) == EMAIL_OTP
    )
    assert (
        resolve_identity_method(identity_method="  ", identity_email_otp=False)
        == PILOT_ENTER
    )


def test_resolve_explicit_wins_over_legacy_flag() -> None:
    assert (
        resolve_identity_method(
            identity_method="borderless_password",
            identity_email_otp=False,
        )
        == BORDERLESS_PASSWORD
    )
    assert (
        resolve_identity_method(identity_method="PILOT_ENTER", identity_email_otp=True)
        == PILOT_ENTER
    )


def test_legacy_false_is_never_password() -> None:
    assert (
        resolve_identity_method(identity_method="", identity_email_otp=False)
        == PILOT_ENTER
    )


def test_resolve_rejects_unknown_method() -> None:
    with pytest.raises(ValueError, match="IDENTITY_METHOD"):
        resolve_identity_method(identity_method="oauth", identity_email_otp=True)


def test_settings_rejects_unknown_identity_method() -> None:
    with pytest.raises(ValidationError):
        Settings(identity_method="oauth")


def test_legacy_email_otp_required_hides_password_from_old_clients() -> None:
    assert email_otp_required_for_legacy_clients(EMAIL_OTP) is True
    assert email_otp_required_for_legacy_clients(BORDERLESS_PASSWORD) is True
    assert email_otp_required_for_legacy_clients(PILOT_ENTER) is False


@pytest.mark.parametrize(
    ("method", "otp_flag", "expected"),
    [
        ("", True, {"email_otp_required": True, "method": "email_otp"}),
        ("", False, {"email_otp_required": False, "method": "pilot_enter"}),
        (
            "borderless_password",
            False,
            {"email_otp_required": True, "method": "borderless_password"},
        ),
        (
            "email_otp",
            False,
            {"email_otp_required": True, "method": "email_otp"},
        ),
        (
            "pilot_enter",
            True,
            {"email_otp_required": False, "method": "pilot_enter"},
        ),
    ],
)
def test_identity_mode_three_methods(
    raw_client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    otp_flag: bool,
    expected: dict[str, object],
) -> None:
    monkeypatch.setattr(settings, "identity_method", method)
    monkeypatch.setattr(settings, "identity_email_otp", otp_flag)
    res = raw_client.get("/auth/identity-mode")
    assert res.status_code == 200, res.text
    assert res.json() == expected
