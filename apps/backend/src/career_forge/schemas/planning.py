"""Adaptive planning after validation (HAC-11)."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TodayFocus(BaseModel):
    """Single focus block for the learner today."""

    node_id: str
    title: str
    duration_minutes: int = Field(ge=5, le=240)
    objective: str


class PlanUpdateResponse(BaseModel):
    """Mission banner + next step after graph adapts."""

    today_focus: TodayFocus
    next_mission: str = Field(
        description='Short mission line for MissionBanner, e.g. "HTTP básico — métodos (30 min)"',
    )
