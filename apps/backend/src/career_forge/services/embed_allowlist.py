"""Persist and cache hostnames proven embeddable by a Content Operator."""

from __future__ import annotations

import re
from threading import Lock

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.embed_allowlist import EmbedHost, EmbedHostAudit
from career_forge.services.operator_content import require_content_role

_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_cache_lock = Lock()
_cached_hosts: tuple[str, ...] | None = None


def normalize_embed_host(value: str) -> str:
    host = value.strip().lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if not host or any(marker in host for marker in ("://", "/", "@", ":")):
        raise ValueError("valid hostname is required")
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError as exc:
        raise ValueError("valid hostname is required") from exc
    labels = host.split(".")
    if len(labels) < 2 or len(host) > 253 or any(
        not _HOST_LABEL.fullmatch(label) for label in labels
    ):
        raise ValueError("valid hostname is required")
    return host


def commit_embed_host_write(session: Session) -> None:
    """Commit a write and invalidate atomically relative to cached reads."""
    global _cached_hosts
    with _cache_lock:
        session.commit()
        _cached_hosts = None


def learner_embed_hosts(session: Session) -> tuple[str, ...]:
    global _cached_hosts
    with _cache_lock:
        if _cached_hosts is None:
            _cached_hosts = tuple(
                session.scalars(select(EmbedHost.host).order_by(EmbedHost.host)).all()
            )
        return _cached_hosts


def list_embed_hosts(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[EmbedHost]:
    require_content_role(principal)
    return list(session.scalars(select(EmbedHost).order_by(EmbedHost.host)))


def add_embed_host(
    session: Session,
    *,
    principal: OperatorPrincipal,
    host: str,
) -> EmbedHost:
    require_content_role(principal)
    normalized = normalize_embed_host(host)
    inserted_host = session.scalar(
        insert(EmbedHost)
        .values(
            host=normalized,
            created_by_operator_id=principal.operator_id,
        )
        .on_conflict_do_nothing(index_elements=[EmbedHost.host])
        .returning(EmbedHost.host)
    )
    if inserted_host is not None:
        session.add(
            EmbedHostAudit(
                host=normalized,
                action="add",
                operator_id=principal.operator_id,
                actor_email=principal.email,
            )
        )
        session.flush()
    row = session.get(EmbedHost, normalized)
    if row is None:
        raise RuntimeError("embed host insert did not persist")
    return row


def remove_embed_host(
    session: Session,
    *,
    principal: OperatorPrincipal,
    host: str,
) -> None:
    require_content_role(principal)
    normalized = normalize_embed_host(host)
    removed = session.scalar(
        delete(EmbedHost)
        .where(EmbedHost.host == normalized)
        .returning(EmbedHost.host)
    )
    if removed is None:
        return
    session.add(
        EmbedHostAudit(
            host=normalized,
            action="remove",
            operator_id=principal.operator_id,
            actor_email=principal.email,
        )
    )
    session.flush()
