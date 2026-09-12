"""CAR-103 — users.borderless_user_id nullable unique (partial)."""

from __future__ import annotations

import pytest
from sqlalchemy.exc import IntegrityError

from career_forge.db.repositories.user import ensure_user
from career_forge.db.session import SessionLocal


def test_existing_user_has_null_borderless_user_id() -> None:
    with SessionLocal() as session:
        user = ensure_user(session, "car103-null")
        session.commit()
        session.refresh(user)
        assert user.borderless_user_id is None


def test_two_users_may_both_have_null_borderless_user_id() -> None:
    with SessionLocal() as session:
        a = ensure_user(session, "car103-null-a")
        b = ensure_user(session, "car103-null-b")
        session.commit()
        assert a.borderless_user_id is None
        assert b.borderless_user_id is None


def test_non_null_borderless_user_id_is_unique() -> None:
    with SessionLocal() as session:
        first = ensure_user(session, "car103-unique-a")
        first.borderless_user_id = "bl-user-1"
        session.commit()

    with SessionLocal() as session:
        second = ensure_user(session, "car103-unique-b")
        second.borderless_user_id = "bl-user-1"
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
