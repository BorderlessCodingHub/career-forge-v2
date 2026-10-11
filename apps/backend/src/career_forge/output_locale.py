"""Stored account locale, normalized. No database and no service imports."""

from __future__ import annotations


def forge_output_locale(stored: str | None) -> str:
    """English until the learner has chosen Brazilian Portuguese."""
    if stored == "pt-BR":
        return "pt-BR"
    return "en"


def is_portuguese(locale: str | None) -> bool:
    """True only after the stored value has been normalized to pt-BR."""
    return forge_output_locale(locale) == "pt-BR"
