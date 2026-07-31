"""Bearer-scoped forge artifact list + open (CAR-25)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from career_forge.api.deps import ExternalId
from career_forge.db.session import get_db
from career_forge.schemas.forge_artifacts import ForgeArtifactListResponse, ForgeArtifactSummary
from career_forge.schemas.roadmap import RoadmapResponse
from career_forge.services import forge_artifacts as forge_artifacts_service

router = APIRouter()


@router.get("/forges", response_model=ForgeArtifactListResponse)
def list_my_forges(
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> ForgeArtifactListResponse:
    rows = forge_artifacts_service.list_forges(db, external_id)
    return ForgeArtifactListResponse(
        items=[ForgeArtifactSummary.model_validate(forge_artifacts_service.artifact_summary(row)) for row in rows],
    )


@router.post("/forges/{public_id}/open", response_model=RoadmapResponse)
def open_my_forge(
    public_id: UUID,
    external_id: ExternalId,
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    return forge_artifacts_service.open_forge(db, external_id, public_id)
