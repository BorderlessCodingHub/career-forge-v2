"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from career_forge.api.router import api_router
from career_forge.config import settings
from career_forge.errors import DomainError
from career_forge.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


async def _domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    """Map transport-agnostic domain errors to HTTP, preserving status codes."""
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


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
    app.add_exception_handler(DomainError, _domain_error_handler)
    return app


app = create_app()
