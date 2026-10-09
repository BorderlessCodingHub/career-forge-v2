"""Learner email copy (CAR-131).

English is the reviewed catalog. The pt-BR strings are a machine draft.
Add ``"pt-BR"`` to ``REVIEWED_LOCALES`` only after a person edits that draft.
Until then a stored pt-BR locale still sends English.
"""

from __future__ import annotations

REVIEWED_LOCALES = frozenset({"en"})

_OTP = {
    "en": (
        "Your Career Forge code",
        "Your verification code is {code}. It expires in {minutes} minutes.",
    ),
    "pt-BR": (
        "Seu código do Career Forge",
        "Seu código de verificação é {code}. Ele expira em {minutes} minutos.",
    ),
}

_RESUME = {
    "en": (
        "Your Career Forge resume link",
        "Use this single-use link to resume your Career Forge roadmap "
        "(expires in about {days} days):\n\n{url}\n",
    ),
    "pt-BR": (
        "Seu link para retomar o Career Forge",
        "Use este link de uso único para retomar sua trilha no Career Forge "
        "(expira em cerca de {days} dias):\n\n{url}\n",
    ),
}

_CONTINUITY_IDLE = {
    "en": (
        "Your roadmap is here",
        "Your roadmap is ready when you are.\n\n{url}\n",
    ),
    "pt-BR": (
        "Sua trilha está aqui",
        "Sua trilha está pronta quando você estiver.\n\n{url}\n",
    ),
}

_CONTINUITY_NODE = {
    "en": (
        "Continue with {title}",
        "{title} is the next node on your roadmap.\n\n{url}\n",
    ),
    "pt-BR": (
        "Continue com {title}",
        "{title} é o próximo nó da sua trilha.\n\n{url}\n",
    ),
}

_BILLING = {
    "en": (
        "A charge for Career Forge failed",
        "A charge for Career Forge failed. "
        "You can keep using Career Forge. "
        "This link updates your card:\n\n{url}\n",
    ),
    "pt-BR": (
        "Uma cobrança do Career Forge falhou",
        "Uma cobrança do Career Forge falhou. "
        "Você pode continuar usando o Career Forge. "
        "Este link atualiza seu cartão:\n\n{url}\n",
    ),
}


def email_locale(stored: str | None) -> str:
    """Locale to send. Missing, unknown, and unreviewed values stay English."""
    if stored in REVIEWED_LOCALES:
        return stored
    return "en"


def _render(template: tuple[str, str], **values: object) -> tuple[str, str]:
    subject, text = template
    return subject.format(**values), text.format(**values)


def otp_letter(*, code: str, minutes: int, locale: str | None) -> tuple[str, str]:
    return _render(_OTP[email_locale(locale)], code=code, minutes=minutes)


def resume_letter(*, url: str, days: int, locale: str | None) -> tuple[str, str]:
    return _render(_RESUME[email_locale(locale)], url=url, days=days)


def continuity_idle_letter(*, url: str, locale: str | None) -> tuple[str, str]:
    return _render(_CONTINUITY_IDLE[email_locale(locale)], url=url)


def continuity_node_letter(
    *,
    title: str,
    url: str,
    locale: str | None,
) -> tuple[str, str]:
    return _render(_CONTINUITY_NODE[email_locale(locale)], title=title, url=url)


def billing_letter(*, url: str, locale: str | None) -> tuple[str, str]:
    return _render(_BILLING[email_locale(locale)], url=url)


def operator_otp_letter(*, code: str, minutes: int) -> tuple[str, str]:
    """Operator console code. Always English, ignoring any learner locale."""
    return (
        "Your Operator console code",
        (
            f"Your Operator console verification code is {code}. "
            "This is not your learner Email identity login. "
            f"It expires in {minutes} minutes."
        ),
    )
