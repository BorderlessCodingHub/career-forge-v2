"""Schemas for share / resume forge deep-links (CAR-27)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ForgeLinkMintResponse(BaseModel):
    token: str = Field(min_length=1)
    path: str = Field(min_length=1)


class ForgeShareRevokeResponse(BaseModel):
    revoked: int = Field(ge=0)


class ResumeConsumeResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    external_id: str
