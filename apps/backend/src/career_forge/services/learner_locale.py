"""Account locale for one learner-facing call (CAR-133).

The stored account is the source. The cookie and the client are not.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from career_forge.db.repositories.user import get_by_external_id
from career_forge.db.session import SessionLocal
from career_forge.services.forge_locale import forge_output_locale


def account_output_locale(user_id: str, session: Session | None = None) -> str:
    """Read the account locale at call time. Missing accounts stay English."""
    owns_session = session is None
    db = session or SessionLocal()
    try:
        user = get_by_external_id(db, user_id)
        stored = user.ui_locale if user is not None else None
        return forge_output_locale(stored)
    finally:
        if owns_session:
            db.close()
