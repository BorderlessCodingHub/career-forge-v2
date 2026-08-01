"""Schemas for /me/profile + /me/email (CAR-29)."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.profile_diagnosis import DiagnosisMotorIntake

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"


class MeEmailUpdateRequest(BaseModel):
    """PATCH /me/email — optional recovery email (store only)."""

    email: str = Field(min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not _EMAIL_RE.match(cleaned):
            raise ValueError("invalid email address")
        if cleaned.endswith(_DEMO_EMAIL_SUFFIX):
            raise ValueError("demo synthetic emails are not allowed")
        return cleaned


class MeEmailUpdateResponse(BaseModel):
    email: str


class MeProfileResponse(BaseModel):
    """Bearer principal profile + confirmed diagnosis for re-forge (CAR-29)."""

    external_id: str
    email: str | None = None
    has_diagnosis: bool = False
    diagnosis: DiagnosisResponse | None = None
    intake: DiagnosisMotorIntake | None = None
