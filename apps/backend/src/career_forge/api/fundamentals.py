"""Learner Fundamentals — one published reading per Goal (ADR-010)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response

from career_forge.api.deps import require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.schemas.fundamentals import (
    FundamentalsCatalog,
    FundamentalsGuide,
    FundamentalsLocale,
    PublishedGoal,
)
from career_forge.services.fundamentals import list_published_goal_ids, require_fundamentals

router = APIRouter()


@router.get("", response_model=FundamentalsCatalog)
def list_fundamentals(
    response: Response,
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> FundamentalsCatalog:
    response.headers["Cache-Control"] = "no-store"
    return FundamentalsCatalog(
        goals=[PublishedGoal(goal_id=goal_id) for goal_id in list_published_goal_ids()]
    )


@router.get("/{goal_id}", response_model=FundamentalsGuide)
def read_fundamentals(
    goal_id: str,
    response: Response,
    locale: FundamentalsLocale = Query(...),
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> FundamentalsGuide:
    response.headers["Cache-Control"] = "no-store"
    return require_fundamentals(goal_id, locale)
