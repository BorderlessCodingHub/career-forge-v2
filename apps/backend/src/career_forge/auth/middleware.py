"""Bearer auth middleware — reject missing/invalid tokens on protected paths."""

from __future__ import annotations

import re

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from career_forge.auth.providers import get_auth_provider

# SSE cannot send Authorization until CAR-26 stream tickets.
_PUBLIC_EXACT = frozenset(
    {
        "/health",
        "/openapi.json",
        "/docs",
        "/docs/oauth2-redirect",
        "/redoc",
        "/auth/anon/mint",
    }
)
_PUBLIC_PREFIXES = ("/docs", "/redoc")
_FORGE_STREAM_RE = re.compile(r"^/forge/[^/]+/stream$")


def is_public_path(path: str) -> bool:
    if path in _PUBLIC_EXACT:
        return True
    if any(path.startswith(prefix) for prefix in _PUBLIC_PREFIXES):
        return True
    if _FORGE_STREAM_RE.match(path):
        return True
    return False


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Require valid Bearer JWT; attach ``request.state.principal``."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if request.method == "OPTIONS" or is_public_path(request.url.path):
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
