"""Schemas for Operator OTP identity (CAR-75)."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field, field_validator

from career_forge.schemas.otp import _normalize_otp_email

_OTP_CODE_RE = re.compile(r"^\d{6}$")


class OperatorOtpRequestBody(BaseModel):
    email: str = Field(min_length=3, max_length=255)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return _normalize_otp_email(value)


class OperatorOtpRequestResponse(BaseModel):
    email: str
    expires_in: int


class OperatorOtpVerifyBody(BaseModel):
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


class OperatorOtpVerifyResponse(BaseModel):
    provider: str
    email: str
    operator_id: int
    desk_roles: str
    desks: list[str]
    expires_in: int


class OperatorMeResponse(BaseModel):
    email: str
    operator_id: int
    desk_roles: str
    desks: list[str]
