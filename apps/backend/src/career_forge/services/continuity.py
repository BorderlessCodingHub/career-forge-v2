"""Continuity email — one accepted send per quiet stretch (CAR-123).

Billing email is a different track and does not read or write this state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Protocol
from urllib.parse import urlencode

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from career_forge.config import settings
from career_forge.db.models.forge_artifact import ForgeArtifact
from career_forge.db.models.user import User
from career_forge.db.models.user_skill_node import UserSkillNode
from career_forge.db.repositories.user import get_by_external_id

logger = logging.getLogger(__name__)

QUIET_STRETCH = timedelta(hours=168)


@dataclass(frozen=True)
class SpineNode:
    node_id: str
    title: str
    status: str


@dataclass(frozen=True)
class Stretch:
    presence_at: datetime | None
    accepted_presence_at: datetime | None
    email: str | None
    has_roadmap: bool


class ContinuityMailer(Protocol):
    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None: ...


def next_node(nodes: list[SpineNode] | tuple[SpineNode, ...]) -> SpineNode | None:
    """First spine node that is neither approved nor locked."""
    for node in nodes:
        if node.status in ("aprovado", "bloqueado"):
            continue
        return node
    return None


def is_due(stretch: Stretch, now: datetime) -> bool:
    email = (stretch.email or "").strip()
    if not email or not stretch.has_roadmap or stretch.presence_at is None:
        return False
    if now - stretch.presence_at < QUIET_STRETCH:
        return False
    return stretch.accepted_presence_at != stretch.presence_at


def continuity_message(
    node: SpineNode | None,
    *,
    frontend_url: str,
) -> tuple[str, str, str]:
    """Subject, body, and absolute URL. Copy does not say the learner is behind."""
    base = frontend_url.rstrip("/")
    if node is None:
        url = f"{base}/roadmap?from=continuity"
        subject = "Your roadmap is here"
        text = f"Your roadmap is ready when you are.\n\n{url}\n"
        return subject, text, url

    query = urlencode({"from": "continuity", "node": node.node_id})
    url = f"{base}/roadmap?{query}"
    subject = f"Continue with {node.title}"
    text = f"{node.title} is the next node on your roadmap.\n\n{url}\n"
    return subject, text, url


def try_send(
    stretch: Stretch,
    node: SpineNode | None,
    mailer: ContinuityMailer,
    *,
    frontend_url: str,
    now: datetime | None = None,
) -> tuple[Stretch, bool]:
    """Send one letter. A rejected send leaves the stretch unspent."""
    if now is not None and not is_due(stretch, now):
        raise ValueError("continuity stretch is not due")
    email = (stretch.email or "").strip()
    subject, text, _url = continuity_message(node, frontend_url=frontend_url)
    try:
        mailer.send_continuity(to_email=email, subject=subject, text=text)
    except Exception:
        logger.warning("continuity email rejected for %s", email, exc_info=True)
        return stretch, False
    return replace(stretch, accepted_presence_at=stretch.presence_at), True


def record_roadmap_presence(
    session: Session,
    external_id: str,
    *,
    now: datetime | None = None,
) -> None:
    """Mark the learner on an existing Roadmap. Does not send mail."""
    user = get_by_external_id(session, external_id)
    if user is None:
        return
    user.roadmap_presence_at = now or datetime.now(UTC)
    session.commit()


def sweep_continuity_emails(
    session: Session,
    *,
    now: datetime | None = None,
    mailer: ContinuityMailer,
    frontend_url: str | None = None,
) -> int:
    """Send every due letter. One failure does not spend that stretch or stop the rest."""
    moment = now or datetime.now(UTC)
    origin = frontend_url if frontend_url is not None else settings.frontend_url
    sent = 0
    for user in _due_users(session, moment):
        stretch = _stretch_for(session, user)
        if not is_due(stretch, moment):
            continue
        node = _next_node_for(session, user)
        updated, accepted = try_send(
            stretch,
            node,
            mailer,
            frontend_url=origin,
            now=moment,
        )
        if not accepted:
            session.rollback()
            continue
        user.continuity_accepted_presence_at = updated.accepted_presence_at
        session.commit()
        sent += 1
    return sent


def _due_users(session: Session, now: datetime) -> list[User]:
    cutoff = now - QUIET_STRETCH
    has_nodes = exists().where(UserSkillNode.user_id == User.id)
    has_artifact = exists().where(
        ForgeArtifact.user_id == User.id,
        ForgeArtifact.is_active.is_(True),
    )
    rows = session.scalars(
        select(User).where(
            User.roadmap_presence_at.is_not(None),
            User.roadmap_presence_at <= cutoff,
            User.email.is_not(None),
            or_(
                User.continuity_accepted_presence_at.is_(None),
                User.continuity_accepted_presence_at.is_distinct_from(
                    User.roadmap_presence_at
                ),
            ),
            or_(has_nodes, has_artifact),
        )
    )
    return list(rows)


def _stretch_for(session: Session, user: User) -> Stretch:
    return Stretch(
        presence_at=user.roadmap_presence_at,
        accepted_presence_at=user.continuity_accepted_presence_at,
        email=user.email,
        has_roadmap=user_has_roadmap(session, user),
    )


def user_has_roadmap(session: Session, user: User) -> bool:
    node = session.scalar(
        select(UserSkillNode.id).where(UserSkillNode.user_id == user.id).limit(1)
    )
    if node is not None:
        return True
    artifact = session.scalar(
        select(ForgeArtifact.id).where(
            ForgeArtifact.user_id == user.id,
            ForgeArtifact.is_active.is_(True),
        ).limit(1)
    )
    return artifact is not None


def _next_node_for(session: Session, user: User) -> SpineNode | None:
    if not user.external_id:
        return None
    from career_forge.services.roadmap import get_user_roadmap

    roadmap = get_user_roadmap(session, user.external_id)
    ordered = sorted(roadmap.nodes, key=lambda node: node.sort_order)
    return next_node(
        [
            SpineNode(node.node_id, node.title, node.status)
            for node in ordered
        ]
    )
