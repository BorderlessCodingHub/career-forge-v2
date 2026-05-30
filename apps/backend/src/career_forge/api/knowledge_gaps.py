"""Knowledge gap ledger HTTP routes — adaptive memory read surface (HAC-68)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from career_forge.db.session import get_db
from career_forge.schemas.knowledge_gap import KnowledgeGapItem
from career_forge.services import knowledge_gaps as knowledge_gaps_service

router = APIRouter()


@router.get("", response_model=list[KnowledgeGapItem])
def list_knowledge_gaps(
    user_id: str = Query("demo-ana", min_length=1),
    node_id: str | None = Query(None),
    db: Session = Depends(get_db),
) -> list[KnowledgeGapItem]:
    """Open knowledge gaps for a learner, optionally scoped to a node."""
    return knowledge_gaps_service.list_open_gaps(
        db,
        user_id=user_id,
        skill_node_id=node_id,
    )
