"""Fundamentals — one published reading per Goal (ADR-010)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

FundamentalsLocale = Literal["en", "pt-BR"]


class FundamentalsGuide(BaseModel):
    """The edition a learner reads for one Goal."""

    goal_id: str
    locale: FundamentalsLocale
    body_markdown: str = Field(min_length=1)
