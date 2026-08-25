"""HTTP contracts for the operational Reference embed allowlist."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EmbedHostCreate(BaseModel):
    host: str = Field(min_length=1, max_length=253)


class EmbedHostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    host: str
    created_at: datetime


class OperatorEmbedHostListResponse(BaseModel):
    hosts: list[EmbedHostResponse]


class LearnerEmbedHostListResponse(BaseModel):
    hosts: list[str]
