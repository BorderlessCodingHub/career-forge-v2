from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import health

app = FastAPI(
    title="Career Forge API",
    description="Skill graph adaptativo — diagnóstico, forge e validação de mastery.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)


# Extension points — HAC-6 (SQLAlchemy models) / HAC-7 (Pydantic contracts)
# from app.routers import skills, forge  # noqa: ERA001
