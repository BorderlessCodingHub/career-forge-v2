from fastapi import APIRouter

from app.database import check_database_connection

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    db_ok = check_database_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "service": "career-forge-api",
        "database": "connected" if db_ok else "unavailable",
    }
