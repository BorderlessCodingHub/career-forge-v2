"""Authenticated principal resolved from a Bearer token."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AuthPrincipal:
    """Identity attached to a request after Bearer verification."""

    external_id: str
    provider: str
