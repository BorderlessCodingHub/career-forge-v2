"""Schemas for /me/forges (CAR-25)."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ForgeArtifactSummary(BaseModel):
    """List item — never exposes internal BIGSERIAL id."""

    public_id: UUID
    goal_id: str | None = None
    title: str
    is_active: bool
    created_at: datetime
    graph_run_id: str = Field(min_length=1)


class ForgeArtifactListResponse(BaseModel):
    items: list[ForgeArtifactSummary]


class ForgeArtifactUpdateRequest(BaseModel):
    """PATCH /me/forges/{public_id} — user-editable title (CAR-29)."""

    title: str = Field(min_length=1, max_length=200)
