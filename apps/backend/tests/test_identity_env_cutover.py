"""CAR-107 — repo env defaults stay non-breaking; Labs cutover is explicit."""

from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def _assignments(rel: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in (REPO / rel).read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value
    return out


def test_example_env_keeps_identity_method_empty() -> None:
    for rel in (".env.example", ".env.production.example"):
        assigned = _assignments(rel)
        assert assigned["IDENTITY_METHOD"] == ""
        assert "BORDERLESS_ACCOUNT_URL" not in assigned
        assert assigned["BORDERLESS_SIGNIN_URL"] == (
            "https://api.borderlesscoding.com/api/auth/signin"
        )
        assert assigned["BORDERLESS_SIGNUP_URL"] == (
            "https://platform.borderlesscoding.com/sign-up"
        )
        assert assigned["BORDERLESS_FORGOT_PASSWORD_URL"] == (
            "https://platform.borderlesscoding.com/forgot-password"
        )
        assert assigned["MEMBERSHIP_BACKEND"] == "stub"
        assert "BORDERLESS_MEMBERS_URL" in assigned


def test_deploy_labs_cutover_checklist() -> None:
    text = (REPO / "docs/DEPLOY-LABS-MANUAL.md").read_text(encoding="utf-8")
    assert "IDENTITY_METHOD=borderless_password" in text
    assert "Never treat IDENTITY_EMAIL_OTP=false as password" in text
    assert "BORDERLESS_SIGNIN_URL" in text
    assert "MEMBERSHIP_BACKEND=stub" in text
    assert "not a cutover requirement" in text
    assert "Do not set BORDERLESS_ACCOUNT_URL" in text
