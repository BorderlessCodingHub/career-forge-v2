"""Learner Fundamentals — one published reading per Goal (ADR-010)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Response

from career_forge.api.deps import require_email_provider
from career_forge.auth.principal import AuthPrincipal
from career_forge.schemas.fundamentals import FundamentalsGuide, FundamentalsLocale
from career_forge.services.fundamentals import require_fundamentals

router = APIRouter()


@router.get("/{goal_id}", response_model=FundamentalsGuide)
def read_fundamentals(
    goal_id: str,
    response: Response,
    locale: FundamentalsLocale = Query(...),
    _principal: AuthPrincipal = Depends(require_email_provider),
) -> FundamentalsGuide:
    response.headers["Cache-Control"] = "no-store"
    return require_fundamentals(goal_id, locale)
