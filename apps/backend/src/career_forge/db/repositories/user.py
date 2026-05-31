"""User repository — single entry for lookup/creation by external id (HAC-74).

Replaces the `_resolve_user` helper duplicated across services and the inline
demo-user upsert that was repeated in roadmap/validation/mock-interview.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from career_forge.db.models.user import User


def get_by_external_id(session: Session, external_id: str) -> User | None:
    """Return the user for an external (session) id, or None."""
    return session.scalar(select(User).where(User.external_id == external_id))


def ensure_user(
    session: Session,
    external_id: str,
    *,
    display_name: str | None = None,
) -> User:
    """Get the user by external id, creating a demo-shaped record if missing."""
    user = get_by_external_id(session, external_id)
    if user is not None:
        return user
    user = User(
        external_id=external_id,
        display_name=display_name or external_id.replace("-", " ").title(),
        email=f"{external_id}@demo.careerforge.local",
    )
    session.add(user)
    session.flush()
    return user
