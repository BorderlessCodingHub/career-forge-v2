"""Validation HTTP routes — HAC-10."""

from fastapi import APIRouter

router = APIRouter()


@router.post("/")
def run_validation() -> dict[str, str]:
    return {"status": "not_implemented", "issue": "HAC-10"}
