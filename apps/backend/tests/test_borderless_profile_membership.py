"""Profile URL helper and the password-mode encryption key. Membership now comes from OAuth."""

from __future__ import annotations

import pytest

from career_forge.config import assert_borderless_token_key, settings
from career_forge.services.borderless_profile import borderless_profile_url


def test_profile_url_uses_the_signin_origin() -> None:
    assert (
        borderless_profile_url("https://api.borderlesscoding.com/api/auth/signin")
        == "https://api.borderlesscoding.com/api/users/profile"
    )


def test_password_mode_refuses_to_boot_without_a_token_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "identity_method", "borderless_password")
    monkeypatch.setattr(settings, "borderless_token_encryption_key", " ")
    with pytest.raises(RuntimeError, match="BORDERLESS_TOKEN_ENCRYPTION_KEY"):
        assert_borderless_token_key()
