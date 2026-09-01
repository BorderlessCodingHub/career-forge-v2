"""Bearer auth middleware — reject missing/invalid tokens on protected paths."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from career_forge.auth.operator_session import attach_operator_principal
from career_forge.auth.providers import get_auth_provider
from career_forge.db.session import SessionLocal
from career_forge.errors import DomainError, ForbiddenError

# Forge SSE stays Bearer-exempt; ticket is validated in the stream handler (CAR-26).
# Share/resume deep-links are public; token validity is enforced in handlers (CAR-27).
_PUBLIC_EXACT = frozenset(
    {
        "/health",
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/auth/anon/mint",
        "/auth/otp/request",
        "/auth/otp/verify",
        "/auth/identity-mode",
        "/auth/pilot/enter",
        "/billing/stripe/webhook",
        "/operator/auth/otp/request",
        "/operator/auth/otp/verify",
    }
)
_PUBLIC_PREFIXES = ("/docs", "/redoc")
_FORGE_STREAM_RE = re.compile(r"^/forge/[^/]+/stream$")
_PUBLIC_SHARE_RE = re.compile(r"^/public/share/[^/]+$")
_PUBLIC_RESUME_RE = re.compile(r"^/public/resume/[^/]+$")
_OPERATOR_PREFIX = "/operator"


def is_public_path(path: str) -> bool:
    if path in _PUBLIC_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES):
        return True
    if _FORGE_STREAM_RE.match(path):
        return True
    if _PUBLIC_SHARE_RE.match(path):
        return True
    if _PUBLIC_RESUME_RE.match(path):
        return True
    return False


def _is_operator_path(path: str) -> bool:
    return path == _OPERATOR_PREFIX or path.startswith(f"{_OPERATOR_PREFIX}/")


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Require valid Bearer JWT; attach ``request.state.principal``."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        if _is_operator_path(path):
            return await self._dispatch_operator(request, call_next, path)

        if is_public_path(path):
            return await call_next(request)

        header = request.headers.get("authorization") or request.headers.get("Authorization")
        if not header or not header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization Bearer token"},
            )
        token = header[7:].strip()
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization Bearer token"},
            )
        try:
            principal = get_auth_provider().verify(token)
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired Bearer token"},
            )
        request.state.principal = principal
        return await call_next(request)

    async def _dispatch_operator(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
        path: str,
    ) -> Response:
        if is_public_path(path):
            return await call_next(request)

        with SessionLocal() as db:
            try:
                attach_operator_principal(request, db)
                db.commit()
            except ForbiddenError as exc:
                db.rollback()
                return JSONResponse(
                    status_code=exc.status_code,
                    content={"detail": {"code": exc.code, "message": str(exc)}},
                )
            except ValueError as exc:
                db.rollback()
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Operator session required"},
                )
            except DomainError as exc:
                db.rollback()
                return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})

        return await call_next(request)
