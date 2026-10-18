"""Learner letters carry an absolute URL (learner-mail-absolute-links spec)."""

from __future__ import annotations

import logging

import pytest

from career_forge.errors import MailDeliveryError
from career_forge.services.learner_letter_url import learner_letter_url
from career_forge.services.learner_mail import (
    billing_letter,
    confirm_letter,
    continuity_idle_letter,
    reset_letter,
    resume_letter,
)

_LABS = "https://labs.borderlesscoding.com/career-forge"
_LOCAL = "http://localhost:3300/career-forge"


def test_smtp_confirm_link_is_the_labs_url_on_its_own_line() -> None:
    url = learner_letter_url(
        "/account/confirm?token=abc",
        base=_LABS,
        mailer_backend="smtp",
    )
    _subject, text = confirm_letter(url=url, hours=24, locale="en")

    assert "\n\nhttps://labs.borderlesscoding.com/career-forge/account/confirm?token=abc\n\n" in text


@pytest.mark.parametrize("backend", ["smtp", "resend", "ses"])
def test_leaving_mailers_use_the_labs_origin_for_every_letter(backend: str) -> None:
    confirm = learner_letter_url("/account/confirm?token=abc", base=_LABS + "/", mailer_backend=backend)
    reset = learner_letter_url("/account/reset?token=abc", base=_LABS, mailer_backend=backend)
    resume = learner_letter_url("/resume/raw-token", base=_LABS, mailer_backend=backend)
    roadmap = learner_letter_url("/roadmap?from=continuity", base=_LABS, mailer_backend=backend)
    card = learner_letter_url("/billing/card", base=_LABS, mailer_backend=backend)

    assert confirm == f"{_LABS}/account/confirm?token=abc"
    assert reset == f"{_LABS}/account/reset?token=abc"
    assert resume == f"{_LABS}/resume/raw-token"
    assert roadmap == f"{_LABS}/roadmap?from=continuity"
    assert card == f"{_LABS}/billing/card"
    assert _LABS in reset_letter(url=reset, hours=24, locale="pt-BR")[1]
    assert _LABS in resume_letter(url=resume, days=14, locale="en")[1]
    assert _LABS in continuity_idle_letter(url=roadmap, locale="en")[1]
    assert _LABS in billing_letter(url=card, locale="en")[1]


def test_log_mailer_keeps_the_localhost_confirm_url() -> None:
    url = learner_letter_url(
        "/account/confirm?token=abc",
        base=_LOCAL,
        mailer_backend="log",
    )

    assert url == "http://localhost:3300/career-forge/account/confirm?token=abc"


def test_log_line_contains_the_localhost_confirm_url(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from career_forge.config import settings
    from career_forge.services.mailer import LogMailer

    monkeypatch.setattr(settings, "frontend_url", _LOCAL)
    monkeypatch.setattr(settings, "mailer_backend", "log")
    url = learner_letter_url(
        "/account/confirm?token=abc",
        base=settings.frontend_url,
        mailer_backend=settings.mailer_backend,
    )

    with caplog.at_level(logging.INFO, logger="career_forge.services.mailer"):
        LogMailer().send_account_link(
            to_email="ada@example.com",
            url=url,
            kind="confirm",
            hours=24,
        )

    assert "http://localhost:3300/career-forge/account/confirm?token=abc" in caplog.text


@pytest.mark.parametrize("backend", ["smtp", "resend", "ses", "log", "other"])
@pytest.mark.parametrize(
    "base",
    [
        "",
        "/account/confirm?token=abc",
        "https://labs.borderlesscoding.com",
        "https://labs.borderlesscoding.com/career-forge/extra",
        "https://user:secret@labs.borderlesscoding.com/career-forge",
        "https://labs.borderlesscoding.com/career-forge?next=/",
        "https://labs.borderlesscoding.com/career-forge#top",
    ],
)
def test_an_illegal_base_is_refused_before_a_url_exists(backend: str, base: str) -> None:
    with pytest.raises(MailDeliveryError):
        learner_letter_url("/account/confirm?token=abc", base=base, mailer_backend=backend)


@pytest.mark.parametrize("backend", ["smtp", "resend", "ses"])
def test_http_localhost_does_not_leave_through_a_real_mailer(backend: str) -> None:
    with pytest.raises(MailDeliveryError):
        learner_letter_url(
            "/account/confirm?token=abc",
            base=_LOCAL,
            mailer_backend=backend,
        )
