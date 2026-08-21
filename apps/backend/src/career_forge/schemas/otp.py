"""Schemas for email OTP IdP (CAR-44)."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_DEMO_EMAIL_SUFFIX = "@demo.careerforge.local"
_OTP_CODE_RE = re.compile(r"^\d{6}$")


def _normalize_otp_email(value: str) -> str:
    cleaned = value.strip().lower()
    if not _EMAIL_RE.match(cleaned):
        raise ValueError("invalid email address")
    if cleaned.endswith(_DEMO_EMAIL_SUFFIX):
        raise ValueError("demo synthetic emails are not allowed")
    return cleaned


class OtpRequestBody(BaseModel):
    email: str = Field(min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_otp_email(value)


class OtpRequestResponse(BaseModel):
    ok: bool = True
    email: str
    expires_in: int


class OtpVerifyBody(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    code: str = Field(min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_otp_email(value)

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        cleaned = value.strip()
        if not _OTP_CODE_RE.match(cleaned):
            raise ValueError("code must be 6 digits")
        return cleaned


class OtpVerifyResponse(BaseModel):
    status: Literal["promoted"] = "promoted"
    access_token: str
    token_type: str = "bearer"
    external_id: str
    provider: str
    expires_in: int
