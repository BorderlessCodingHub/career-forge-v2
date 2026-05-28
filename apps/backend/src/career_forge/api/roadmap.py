"""Roadmap HTTP routes — HAC-9."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from career_forge.db.session import get_db
from career_forge.schemas.roadmap import ChecklistToggleRequest, RoadmapResponse, RoadmapSyncRequest
from career_forge.services import roadmap as roadmap_service

router = APIRouter()


@router.get("/", response_model=RoadmapResponse)
def get_roadmap(
    user_id: str = "demo-ana",
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    try:
        return roadmap_service.get_user_roadmap(db, user_id)
    except Exception:
        db.rollback()
        return roadmap_service.build_roadmap_from_catalog()


@router.post("/sync", response_model=RoadmapResponse)
def sync_roadmap(
    body: RoadmapSyncRequest,
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    try:
        return roadmap_service.sync_user_graph(db, body.user_id, body.nodes)
    except Exception:
        db.rollback()
        return roadmap_service.build_roadmap_from_catalog(
            {
                node.node_id: {
                    "status": node.status,
                    "mastery_score": node.mastery_score,
                    "priority": node.priority,
                    "rationale": node.rationale,
                }
                for node in body.nodes
            },
        )


@router.patch("/nodes/{node_id}/checklist", response_model=RoadmapResponse)
def patch_node_checklist(
    node_id: str,
    body: ChecklistToggleRequest,
    db: Session = Depends(get_db),
) -> RoadmapResponse:
    try:
        return roadmap_service.toggle_checklist_item(
            db,
            body.user_id,
            node_id,
            body.item_type,
            body.item_id,
            body.done,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        return roadmap_service.build_roadmap_from_catalog()
