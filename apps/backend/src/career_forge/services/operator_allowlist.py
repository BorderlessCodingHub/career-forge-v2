"""Env allowlist for Operator seats — upserts ``operators`` on OTP request (CAR-75)."""

from __future__ import annotations

from typing import Literal, cast

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.operator import Operator

DeskRoles = Literal["access", "editor", "both"]
_DESK_ROLES: frozenset[str] = frozenset({"access", "editor", "both"})


def parse_operator_allowlist(raw: str) -> dict[str, DeskRoles]:
    """Parse ``email:access|editor|both`` comma pairs. Missing role defaults to ``both``."""
    mapping: dict[str, DeskRoles] = {}
    for chunk in raw.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        if ":" in piece:
            email, role = piece.rsplit(":", 1)
            email_key = email.strip().lower()
            role_key = role.strip().lower()
            if not email_key:
                continue
            if role_key not in _DESK_ROLES:
                continue
            mapping[email_key] = cast(DeskRoles, role_key)
        else:
            email_key = piece.lower()
            if email_key:
                mapping[email_key] = "both"
    return mapping


def desks_for_roles(desk_roles: str) -> list[str]:
    """Map stored role grant to desk tab keys (Content desk = ``content`` in API)."""
    if desk_roles == "access":
        return ["access"]
    if desk_roles == "editor":
        return ["content"]
    return ["access", "content"]


def upsert_operator_from_allowlist(
    session: Session,
    *,
    email: str,
    allowlist: dict[str, DeskRoles],
) -> Operator | None:
    """Return operator row when ``email`` is allowlisted; sync ``desk_roles`` from env."""
    email_key = email.strip().lower()
    desk_roles = allowlist.get(email_key)
    if desk_roles is None:
        return None

    row = session.scalar(select(Operator).where(Operator.email == email_key))
    if row is None:
        row = Operator(email=email_key, desk_roles=desk_roles)
        session.add(row)
    else:
        row.desk_roles = desk_roles
    session.flush()
    return row
