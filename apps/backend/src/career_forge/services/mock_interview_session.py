"""In-memory mock interview MCQ sessions — gabarito stays server-side (HAC-65)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from career_forge.errors import MockInterviewSessionNotFoundError


@dataclass
class MockInterviewSessionRecord:
    session_id: str
    user_id: str
    node_id: str
    node_title: str
    rubric: list[str]
    answer_key: dict[str, str]
    questions_public: list[dict[str, Any]] = field(default_factory=list)


_sessions: dict[str, MockInterviewSessionRecord] = {}


def reset_mock_interview_sessions() -> None:
    """Test helper — clear all MCQ sessions."""
    _sessions.clear()


def save_mock_interview_session(record: MockInterviewSessionRecord) -> MockInterviewSessionRecord:
    _sessions[record.session_id] = record
    return record


def create_session_id() -> str:
    return str(uuid.uuid4())


def get_mock_interview_session(session_id: str) -> MockInterviewSessionRecord:
    record = _sessions.get(session_id)
    if record is None:
        raise MockInterviewSessionNotFoundError(f"Mock interview session {session_id} not found")
    return record


def consume_mock_interview_session(session_id: str) -> MockInterviewSessionRecord:
    record = get_mock_interview_session(session_id)
    _sessions.pop(session_id, None)
    return record
