"""Thin HTTP routers — no business logic."""

from fastapi import APIRouter

from career_forge.api import (
    auth,
    billing,
    demo,
    diagnosis,
    diagnosis_interview,
    forge,
    forge_links,
    health,
    knowledge_gaps,
    me_forges,
    me_profile,
    mentor,
    mentor_report,
    mock_interview,
    operator,
    reference,
    roadmap,
    tutor,
    validation,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(operator.router, prefix="/operator", tags=["operator"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["diagnosis"])
api_router.include_router(
    diagnosis_interview.router,
    prefix="/diagnosis",
    tags=["diagnosis-interview"],
)
api_router.include_router(forge.router, prefix="/forge", tags=["forge"])
api_router.include_router(me_forges.router, prefix="/me", tags=["me"])
api_router.include_router(me_profile.router, prefix="/me", tags=["me"])
api_router.include_router(forge_links.router, tags=["forge-links"])
api_router.include_router(reference.router, prefix="/reference", tags=["reference"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(validation.router, prefix="/validation", tags=["validation"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["mentor"])
api_router.include_router(
    mentor_report.router,
    prefix="/mentor-report",
    tags=["mentor-report"],
)
api_router.include_router(mock_interview.router, prefix="/mock-interview", tags=["mock-interview"])
api_router.include_router(
    knowledge_gaps.router, prefix="/knowledge-gaps", tags=["knowledge-gaps"]
)
api_router.include_router(tutor.router, prefix="/tutor", tags=["tutor"])
