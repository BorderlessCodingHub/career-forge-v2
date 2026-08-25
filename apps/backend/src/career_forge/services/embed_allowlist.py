"""Persist and cache hostnames proven embeddable by a Content Operator."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from urllib.parse import urlsplit

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.embed_allowlist import EmbedHost, EmbedHostAudit
from career_forge.db.models.user_skill_node import UserSkillNode
from career_forge.services.operator_content import require_content_role
from career_forge.services.roadmap.evidence import read_evidence

_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")
_cache_lock = Lock()
_cached_hosts: tuple[str, ...] | None = None


@dataclass(frozen=True)
class PendingEmbedHost:
    host: str
    sample_url: str
    distinct_url_count: int


@dataclass
class _PendingHostGroup:
    sample_url: str
    sample_updated_at: datetime
    urls: set[str] = field(default_factory=set)


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


def _host_is_allowed(host: str, approved: set[str]) -> bool:
    return any(host == allowed or host.endswith(f".{allowed}") for allowed in approved)


def list_embed_hosts(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[EmbedHost]:
    require_content_role(principal)
    return list(session.scalars(select(EmbedHost).order_by(EmbedHost.host)))


def list_pending_embed_hosts(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[PendingEmbedHost]:
    """Aggregate unapproved Reference hosts from the current learner graph only."""
    require_content_role(principal)
    approved = set(session.scalars(select(EmbedHost.host)).all())
    grouped: dict[str, _PendingHostGroup] = {}
    rows = session.execute(
        select(UserSkillNode.evidence, UserSkillNode.updated_at).order_by(
            UserSkillNode.updated_at.desc(),
            UserSkillNode.id,
        )
    )
    for evidence, updated_at in rows:
        for reference in read_evidence(evidence).reference_items():
            raw_url = reference.get("url")
            if not isinstance(raw_url, str):
                continue
            try:
                parsed = urlsplit(raw_url)
                if parsed.scheme not in {"http", "https"} or not parsed.hostname:
                    continue
                host = normalize_embed_host(parsed.hostname)
            except (ValueError, UnicodeError):
                continue
            if _host_is_allowed(host, approved):
                continue
            group = grouped.setdefault(
                host,
                _PendingHostGroup(
                    sample_url=raw_url,
                    sample_updated_at=updated_at,
                ),
            )
            group.urls.add(raw_url)
            if updated_at > group.sample_updated_at:
                group.sample_url = raw_url
                group.sample_updated_at = updated_at

    return [
        PendingEmbedHost(
            host=host,
            sample_url=group.sample_url,
            distinct_url_count=len(group.urls),
        )
        for host, group in sorted(grouped.items())
    ]


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
