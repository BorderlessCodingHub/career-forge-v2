"""FastAPI application factory."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from career_forge.api.router import api_router
from career_forge.auth.middleware import BearerAuthMiddleware
from career_forge.config import settings
from career_forge.errors import (
    DomainError,
    EmailOwnedConflictError,
    ForbiddenError,
    PaywallError,
    QuotaExhaustedError,
)
from career_forge.logging_config import configure_logging


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging()
    yield


async def _domain_error_handler(_request: Request, exc: DomainError) -> JSONResponse:
    """Map transport-agnostic domain errors to HTTP, preserving status codes."""
    if isinstance(exc, QuotaExhaustedError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": {"message": str(exc), "code": exc.code}},
        )
    if isinstance(exc, PaywallError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "message": str(exc),
                    "code": exc.code,
                    "checkout_available": exc.checkout_available,
                }
            },
        )
    if isinstance(exc, EmailOwnedConflictError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "code": "email_owned",
                    "message": str(exc),
                    "existing": exc.existing,
                }
            },
        )
    if isinstance(exc, ForbiddenError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": {
                    "code": exc.code,
                    "message": str(exc),
                }
            },
        )
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


def create_app() -> FastAPI:
    app = FastAPI(
        title="Career Forge API",
        description="Adaptive skill graph — diagnosis, forge, and mastery validation.",
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
    # Added after CORS so it runs first on the request (Starlette reverse order).
    app.add_middleware(BearerAuthMiddleware)

    app.include_router(api_router)
    app.add_exception_handler(DomainError, _domain_error_handler)
    return app


app = create_app()
