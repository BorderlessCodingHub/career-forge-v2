"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from career_forge.api.router import api_router
from career_forge.config import settings
from career_forge.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Career Forge API",
        description="Skill graph adaptativo — diagnóstico, forge e validação de mastery.",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
