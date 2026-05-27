"""Resolve in-memory vs Postgres persistence for session/run stores."""

from __future__ import annotations

import os

from career_forge.config import settings


def resolve_persistence_backend(mode: str | None, *, env_var: str) -> str:
    """Return ``memory`` or ``postgres`` for a store mode env value."""
    normalized = (mode or os.getenv(env_var, "auto")).strip().lower()
    if normalized == "memory":
        return "memory"
    if normalized == "postgres":
        return "postgres"
    env_name = os.getenv("ENV", settings.env).strip().lower()
    if env_name == "production":
        return "postgres"
    return "memory"
