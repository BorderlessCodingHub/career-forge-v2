"""Roadmap HTTP routes — HAC-9."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def get_roadmap() -> dict[str, str]:
    return {"status": "not_implemented", "issue": "HAC-9"}
