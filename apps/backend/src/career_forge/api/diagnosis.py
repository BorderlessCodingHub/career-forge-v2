"""Diagnosis HTTP routes — HAC-8."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def create_diagnosis() -> dict[str, str]:
    return {"status": "not_implemented", "issue": "HAC-8"}
