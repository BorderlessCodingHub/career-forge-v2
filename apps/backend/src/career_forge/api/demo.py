"""Demo mode bootstrap endpoints — HAC-12."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from career_forge.db.session import get_db
from career_forge.schemas.demo import DemoAnaResponse
from career_forge.services.demo import get_demo_ana

router = APIRouter()


@router.get("/ana", response_model=DemoAnaResponse)
def demo_ana(session: Session = Depends(get_db)) -> DemoAnaResponse:
    """Return seeded Ana user with diagnosis, roadmap, and validation history."""
    return get_demo_ana(session)
