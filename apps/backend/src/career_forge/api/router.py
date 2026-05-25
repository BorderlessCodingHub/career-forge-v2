"""Thin HTTP routers — no business logic."""

from fastapi import APIRouter

from career_forge.api import (
    demo,
    diagnosis,
    diagnosis_interview,
    forge,
    health,
    mentor,
    mentor_report,
    mock_interview,
    roadmap,
    validation,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(demo.router, prefix="/demo", tags=["demo"])
api_router.include_router(diagnosis.router, prefix="/diagnosis", tags=["diagnosis"])
api_router.include_router(
    diagnosis_interview.router,
    prefix="/diagnosis",
    tags=["diagnosis-interview"],
)
api_router.include_router(forge.router, prefix="/forge", tags=["forge"])
api_router.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
api_router.include_router(validation.router, prefix="/validation", tags=["validation"])
api_router.include_router(mentor.router, prefix="/mentor", tags=["mentor"])
api_router.include_router(
    mentor_report.router,
    prefix="/mentor-report",
    tags=["mentor-report"],
)
api_router.include_router(mock_interview.router, prefix="/mock-interview", tags=["mock-interview"])
