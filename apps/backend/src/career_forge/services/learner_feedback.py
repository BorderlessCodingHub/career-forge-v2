"""Store a learner product note, then optionally notify the access desk."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.config import Settings, settings
from career_forge.db.models.learner_feedback import LearnerFeedbackNote
from career_forge.db.models.user import User
from career_forge.db.repositories.user import get_by_external_id
from career_forge.errors import BadRequestError, NotFoundError, RateLimitedError
from career_forge.services.mailer import get_mailer
from career_forge.services.operator_access import require_access_role

logger = logging.getLogger(__name__)

_MESSAGE_MAX = 2000
_PATH_MAX = 200
_NOTE_LIMIT = 5
_LIST_CAP = 100
_WINDOW = timedelta(hours=24)
_LOCALES = frozenset({"en", "pt-BR"})

FEEDBACK_LIMIT_MESSAGE = (
    "Five notes are already stored for this account in the last 24 hours"
)


def locale_from_cookie(header: str | None) -> str | None:
    if not header:
        return None
    for part in header.split(";"):
        name, separator, value = part.strip().partition("=")
        if separator != "=" or name != "cf_locale":
            continue
        cleaned = value.strip()
        if cleaned in _LOCALES:
            return cleaned
        return None
    return None


def display_path(raw: str | None) -> str | None:
    if raw is None:
        return None
    text = raw.strip()
    if not text.startswith("/") or "://" in text or any(char.isspace() for char in text):
        return None
    return text[:_PATH_MAX]


def submit_learner_feedback(
    session: Session,
    *,
    external_id: str,
    message: str,
    path: str | None,
    cookie_header: str | None,
    cfg: Settings | None = None,
) -> None:
    """Insert the note and commit it before any notice. A failed notice stays success."""
    resolved = cfg or settings
    user = get_by_external_id(session, external_id)
    email = (user.email or "").strip() if user is not None else ""
    if user is None or not email:
        raise BadRequestError("An account email is required")
    cleaned = message.strip()
    if not cleaned:
        raise BadRequestError("A message is required")
    if len(cleaned) > _MESSAGE_MAX:
        raise BadRequestError("A message is at most 2000 characters")

    session.execute(select(User.id).where(User.id == user.id).with_for_update())
    cutoff = datetime.now(timezone.utc) - _WINDOW
    recent = session.scalar(
        select(func.count())
        .select_from(LearnerFeedbackNote)
        .where(
            LearnerFeedbackNote.user_id == user.id,
            LearnerFeedbackNote.created_at >= cutoff,
        )
    )
    if int(recent or 0) >= _NOTE_LIMIT:
        raise RateLimitedError(FEEDBACK_LIMIT_MESSAGE)

    session.add(
        LearnerFeedbackNote(
            user_id=user.id,
            email=email,
            message=cleaned,
            path=display_path(path),
            locale=locale_from_cookie(cookie_header),
        )
    )
    session.commit()
    _notify(resolved)


def list_feedback_notes(
    session: Session,
    *,
    principal: OperatorPrincipal,
) -> list[LearnerFeedbackNote]:
    require_access_role(principal)
    rows = session.scalars(
        select(LearnerFeedbackNote)
        .order_by(LearnerFeedbackNote.created_at.desc(), LearnerFeedbackNote.id.desc())
        .limit(_LIST_CAP)
    )
    return list(rows)


def set_feedback_replied(
    session: Session,
    *,
    principal: OperatorPrincipal,
    note_id: uuid.UUID,
    replied: bool,
) -> LearnerFeedbackNote:
    require_access_role(principal)
    row = session.get(LearnerFeedbackNote, note_id)
    if row is None:
        raise NotFoundError("product note not found")
    row.replied_at = datetime.now(timezone.utc) if replied else None
    return row


def _notify(cfg: Settings) -> None:
    target = cfg.feedback_notify_email.strip()
    if not target:
        return
    try:
        get_mailer().send_feedback_notice(to_email=target)
    except Exception:
        logger.warning("feedback notice was not sent")
