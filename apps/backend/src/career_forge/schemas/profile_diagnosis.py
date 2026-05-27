"""Confirmed diagnosis persistence — profile envelope for forge motor input (HAC-52)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from career_forge.schemas.diagnosis import DiagnosisResponse
from career_forge.schemas.diagnosis_interview import (
    CvAttachment,
    CvSignals,
    YearsXpRange,
)

PROFILE_DIAGNOSIS_VERSION = 2


class DiagnosisMotorIntake(BaseModel):
    """Onboarding + interview context aggregated for roadmap forge."""

    goal_id: str
    motivation: str
    years_xp: YearsXpRange | None = None
    cv: CvAttachment | None = None
    answers: dict[str, str] = Field(default_factory=dict)
    cv_signals: CvSignals | None = None


class ProfileDiagnosisRecord(BaseModel):
    """JSONB envelope stored on profiles.diagnosis."""

    version: Literal[2] = PROFILE_DIAGNOSIS_VERSION
    diagnosis: DiagnosisResponse
    intake: DiagnosisMotorIntake


class DiagnosisConfirmRequest(BaseModel):
    """POST /diagnosis/confirm — persist edited diagnosis + intake context."""

    user_id: str = Field(min_length=1, description="Client external_id (session user id)")
    diagnosis: DiagnosisResponse
    goal_id: str = Field(min_length=1)
    motivation: str = Field(min_length=1, max_length=280)
    years_xp: YearsXpRange | None = None
    cv: DiagnosisIntake.model_fields["cv"].annotation | None = None
    answers: dict[str, str] = Field(default_factory=dict)
    cv_signals: CvSignals | None = None
    display_name: str | None = Field(default=None, max_length=120)


class DiagnosisConfirmResponse(BaseModel):
    user_id: str
    profile_id: str
    status: Literal["confirmed"] = "confirmed"


def parse_profile_diagnosis(raw: dict[str, Any] | None) -> ProfileDiagnosisRecord | None:
    """Read v2 envelope or legacy v1 DiagnosisResponse-only blob."""
    if not raw:
        return None
    if raw.get("version") == PROFILE_DIAGNOSIS_VERSION and "diagnosis" in raw:
        return ProfileDiagnosisRecord.model_validate(raw)
    return ProfileDiagnosisRecord(
        diagnosis=DiagnosisResponse.model_validate(raw),
        intake=DiagnosisMotorIntake(
            goal_id=raw.get("profile", {}).get("track_id", "backend"),
            motivation="",
        ),
    )


def diagnosis_response_from_profile(raw: dict[str, Any] | None) -> DiagnosisResponse | None:
    record = parse_profile_diagnosis(raw)
    return record.diagnosis if record else None
