"""UI locale stored on the user (CAR-37)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from career_forge.schemas.me_profile import MeLocaleUpdateRequest


def test_locale_accepts_english_and_brazilian_portuguese() -> None:
    assert MeLocaleUpdateRequest(locale="en").locale == "en"
    assert MeLocaleUpdateRequest(locale="pt-BR").locale == "pt-BR"


def test_locale_rejects_anything_else() -> None:
    with pytest.raises(ValidationError):
        MeLocaleUpdateRequest(locale="pt")
    with pytest.raises(ValidationError):
        MeLocaleUpdateRequest(locale="fr")
