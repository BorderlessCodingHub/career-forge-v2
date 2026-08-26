"""Canonical skill content — one published piece per skill_id (ADR-004)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CanonicalRef(BaseModel):
    """Live-resolved pointer stored as skill_id only on the graph."""

    skill_id: str
    title: str


class CanonicalPage(BaseModel):
    """Published git body + live sidecar metadata."""

    skill_id: str
    title: str
    url: str | None = None
    body_markdown: str = Field(min_length=1)
