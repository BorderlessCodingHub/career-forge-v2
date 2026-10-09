"""Learner email copy follows the locale stored on the user (CAR-131)."""

from __future__ import annotations

import pytest

from career_forge.services.learner_mail import (
    REVIEWED_LOCALES,
    billing_letter,
    continuity_idle_letter,
    continuity_node_letter,
    email_locale,
    operator_otp_letter,
    otp_letter,
    resume_letter,
)


def test_no_stored_locale_is_english() -> None:
    assert email_locale(None) == "en"
    assert email_locale("") == "en"
    assert email_locale("fr") == "en"


def test_stored_english_stays_english() -> None:
    assert email_locale("en") == "en"
    subject, text = otp_letter(code="424242", minutes=10, locale="en")
    assert subject == "Your Career Forge code"
    assert text == "Your verification code is 424242. It expires in 10 minutes."


def test_unreviewed_pt_br_stays_english() -> None:
    assert "pt-BR" not in REVIEWED_LOCALES
    assert email_locale("pt-BR") == "en"
    subject, _text = billing_letter(
        url="http://localhost:3300/career-forge/billing/card",
        locale="pt-BR",
    )
    assert subject == "A charge for Career Forge failed"


def test_reviewed_pt_br_uses_the_brazilian_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "career_forge.services.learner_mail.REVIEWED_LOCALES",
        frozenset({"en", "pt-BR"}),
    )

    otp_subject, otp_text = otp_letter(code="424242", minutes=10, locale="pt-BR")
    assert otp_subject == "Seu código do Career Forge"
    assert otp_text == (
        "Seu código de verificação é 424242. Ele expira em 10 minutos."
    )

    resume_subject, resume_text = resume_letter(
        url="https://labs.example/resume/abc",
        days=7,
        locale="pt-BR",
    )
    assert resume_subject == "Seu link para retomar o Career Forge"
    assert "trilha" in resume_text
    assert "https://labs.example/resume/abc" in resume_text
    assert "7" in resume_text

    idle_subject, idle_text = continuity_idle_letter(
        url="https://labs.example/roadmap?from=continuity",
        locale="pt-BR",
    )
    assert idle_subject == "Sua trilha está aqui"
    assert "pronta quando você estiver" in idle_text

    node_subject, node_text = continuity_node_letter(
        title="Retrieval",
        url="https://labs.example/roadmap?from=continuity&node=retrieval",
        locale="pt-BR",
    )
    assert node_subject == "Continue com Retrieval"
    assert "Retrieval é o próximo nó da sua trilha." in node_text

    bill_subject, bill_text = billing_letter(
        url="https://labs.example/billing/card",
        locale="pt-BR",
    )
    assert bill_subject == "Uma cobrança do Career Forge falhou"
    assert "Você pode continuar usando o Career Forge." in bill_text
    assert "https://labs.example/billing/card" in bill_text


def test_prod_mailers_send_the_resolved_letter_and_keep_operator_english(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from career_forge.services.mailer import ResendMailer, SesMailer

    monkeypatch.setattr(
        "career_forge.services.learner_mail.REVIEWED_LOCALES",
        frozenset({"en", "pt-BR"}),
    )
    for mailer in (ResendMailer(), SesMailer()):
        seen: dict[str, str] = {}

        def _capture(**kwargs: str) -> None:
            seen.update(kwargs)

        monkeypatch.setattr(mailer, "_send", _capture)
        mailer.send_operator_otp(to_email="op@example.com", code="111111")
        assert seen["subject"] == "Your Operator console code"
        assert "learner Email identity" in seen["text"]

        mailer.send_otp(to_email="ana@example.com", code="222222", locale=None)
        assert seen["subject"] == "Your Career Forge code"

        mailer.send_otp(to_email="ana@example.com", code="222222", locale="pt-BR")
        assert seen["subject"] == "Seu código do Career Forge"
        assert "222222" in seen["text"]

        mailer.send_resume_link(
            to_email="ana@example.com",
            resume_url="https://labs.example/resume/abc",
            locale="pt-BR",
        )
        assert seen["subject"] == "Seu link para retomar o Career Forge"
        assert "https://labs.example/resume/abc" in seen["text"]


def test_otp_and_billing_and_continuity_read_the_stored_locale(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from career_forge.db.repositories.user import ensure_user
    from career_forge.db.session import SessionLocal
    from career_forge.services.billing_email import apply_billing_email
    from career_forge.services.continuity import _stretch_for
    from career_forge.services.otp import request_otp

    otp_seen: dict[str, str | None] = {}

    class _OtpMailer:
        def send_otp(
            self, *, to_email: str, code: str, locale: str | None = None
        ) -> None:
            otp_seen["locale"] = locale

    monkeypatch.setattr(
        "career_forge.services.learner_mail.REVIEWED_LOCALES",
        frozenset({"en", "pt-BR"}),
    )
    billing_seen: list[str] = []

    class _BillingMailer:
        def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
            billing_seen.append(subject)

    with SessionLocal() as session:
        missing = request_otp(
            session,
            email="no-locale-car-131@example.com",
            client_ip="203.0.113.10",
            mailer=_OtpMailer(),
        )
        assert missing > 0
        assert otp_seen["locale"] is None

        user = ensure_user(session, "car-131-locale-user")
        user.email = "stored-locale-car-131@example.com"
        user.ui_locale = "pt-BR"
        user.membership_label = "external"
        user.billing_entitled = True
        user.stripe_customer_id = "cus_car_131"
        user.billing_email_spell_open = False
        session.commit()

        request_otp(
            session,
            email="stored-locale-car-131@example.com",
            client_ip="203.0.113.11",
            mailer=_OtpMailer(),
        )
        assert otp_seen["locale"] == "pt-BR"

        stretch = _stretch_for(session, user)
        assert stretch.locale == "pt-BR"

        apply_billing_email(
            session,
            {
                "type": "customer.subscription.updated",
                "data": {
                    "object": {
                        "id": "sub_car_131",
                        "customer": "cus_car_131",
                        "status": "past_due",
                    },
                    "previous_attributes": {"status": "active"},
                },
            },
            _BillingMailer(),
            frontend_url="http://localhost:3300/career-forge",
        )
        session.commit()
        session.refresh(user)
        spell_open = bool(user.billing_email_spell_open)

    assert billing_seen == ["Uma cobrança do Career Forge falhou"]
    assert spell_open is True


def test_operator_letter_stays_english() -> None:
    subject, text = operator_otp_letter(code="424242", minutes=10)
    assert subject == "Your Operator console code"
    assert text == (
        "Your Operator console verification code is 424242. "
        "This is not your learner Email identity login. "
        "It expires in 10 minutes."
    )
