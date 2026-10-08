"""Continuity email — quiet stretch, next Node, one accepted send (CAR-123)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from dataclasses import replace

from career_forge.services.continuity import (
    QUIET_STRETCH,
    SpineNode,
    Stretch,
    continuity_message,
    is_due,
    next_node,
    try_send,
)

PRESENCE = datetime(2026, 10, 1, 12, 0, tzinfo=UTC)


def _stretch(**overrides: object) -> Stretch:
    base = Stretch(
        presence_at=PRESENCE,
        accepted_presence_at=None,
        email="ana@example.com",
        has_roadmap=True,
    )
    return replace(base, **overrides)  # type: ignore[arg-type]


def test_next_node_is_the_first_spine_node_that_is_neither_approved_nor_locked() -> None:
    nodes = [
        SpineNode("a", "Locked first", "bloqueado"),
        SpineNode("b", "Already passed", "aprovado"),
        SpineNode("c", "Retrieval", "em_estudo"),
        SpineNode("d", "Later", "recomendado"),
    ]

    found = next_node(nodes)

    assert found is not None
    assert found.node_id == "c"
    assert found.title == "Retrieval"


def test_next_node_is_absent_when_every_spine_node_is_approved_or_locked() -> None:
    nodes = [
        SpineNode("a", "Locked", "bloqueado"),
        SpineNode("b", "Passed", "aprovado"),
    ]

    assert next_node(nodes) is None


def test_quiet_stretch_is_168_hours_and_not_due_before_that() -> None:
    assert QUIET_STRETCH == timedelta(hours=168)
    assert is_due(_stretch(), PRESENCE + timedelta(hours=168) - timedelta(seconds=1)) is False
    assert is_due(_stretch(), PRESENCE + timedelta(hours=168)) is True


def test_one_accepted_send_covers_that_presence_until_a_new_one() -> None:
    accepted = _stretch(accepted_presence_at=PRESENCE)
    later = PRESENCE + timedelta(hours=200)

    assert is_due(accepted, later) is False

    fresh = _stretch(
        presence_at=later,
        accepted_presence_at=PRESENCE,
    )
    assert is_due(fresh, later + timedelta(hours=168)) is True


def test_missing_email_or_roadmap_is_not_due() -> None:
    due_at = PRESENCE + timedelta(hours=168)
    assert is_due(_stretch(email=None), due_at) is False
    assert is_due(_stretch(email="  "), due_at) is False
    assert is_due(_stretch(has_roadmap=False), due_at) is False
    assert is_due(_stretch(presence_at=None), due_at) is False


def test_letter_names_the_next_node_and_does_not_say_the_learner_is_behind() -> None:
    node = SpineNode("retrieval", "Retrieval", "em_estudo")
    subject, text, url = continuity_message(
        node,
        frontend_url="http://localhost:3300/career-forge",
    )

    assert "Retrieval" in subject
    assert "Retrieval" in text
    assert url == "http://localhost:3300/career-forge/roadmap?from=continuity&node=retrieval"
    assert "behind" not in f"{subject}\n{text}".lower()


def test_letter_without_a_next_node_opens_the_roadmap() -> None:
    subject, text, url = continuity_message(
        None,
        frontend_url="http://localhost:3300/career-forge/",
    )

    assert url == "http://localhost:3300/career-forge/roadmap?from=continuity"
    assert "node=" not in url
    assert "behind" not in f"{subject}\n{text}".lower()
    assert text.endswith(url + "\n") or url in text


class _Mailer:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent: list[tuple[str, str, str]] = []

    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None:
        if self.fail:
            raise RuntimeError("rejected")
        self.sent.append((to_email, subject, text))


def test_rejected_send_does_not_spend_the_stretch() -> None:
    stretch = _stretch()
    mailer = _Mailer(fail=True)

    updated, accepted = try_send(
        stretch,
        SpineNode("c", "Retrieval", "em_estudo"),
        mailer,
        frontend_url="http://localhost:3300/career-forge",
    )

    assert accepted is False
    assert updated.accepted_presence_at is None
    assert mailer.sent == []


def test_accepted_send_records_the_presence_it_covered() -> None:
    stretch = _stretch()
    mailer = _Mailer()

    updated, accepted = try_send(
        stretch,
        None,
        mailer,
        frontend_url="http://localhost:3300/career-forge",
    )

    assert accepted is True
    assert updated.accepted_presence_at == PRESENCE
    assert len(mailer.sent) == 1
    to_email, _subject, text = mailer.sent[0]
    assert to_email == "ana@example.com"
    assert "from=continuity" in text
    assert "behind" not in text.lower()


def test_try_send_refuses_a_stretch_that_is_not_due() -> None:
    stretch = _stretch(accepted_presence_at=PRESENCE)
    mailer = _Mailer()

    with pytest.raises(ValueError):
        try_send(
            stretch,
            None,
            mailer,
            frontend_url="http://localhost:3300/career-forge",
            now=PRESENCE + timedelta(hours=200),
        )

    assert mailer.sent == []
