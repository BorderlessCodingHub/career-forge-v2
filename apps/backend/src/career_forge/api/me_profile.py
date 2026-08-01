"""Bearer-scoped profile + optional email (CAR-29)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from career_forge.api.deps import ExternalId
from career_forge.db.session import get_db
from career_forge.schemas.me_profile import (
    MeEmailUpdateRequest,
    MeEmailUpdateResponse,
    MeProfileResponse,
)
from career_forge.services import me_profile as me_profile_service

router = APIRouter()


@router.get("/profile", response_model=MeProfileResponse)
def get_my_profile(
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> MeProfileResponse:
    return me_profile_service.get_me_profile(db, external_id)


@router.patch("/email", response_model=MeEmailUpdateResponse)
def update_my_email(
    body: MeEmailUpdateRequest,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> MeEmailUpdateResponse:
    email = me_profile_service.update_me_email(db, external_id, body.email)
    return MeEmailUpdateResponse(email=email)
