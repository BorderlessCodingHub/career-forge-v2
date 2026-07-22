"""Domain errors — transport-agnostic, mapped to HTTP at the API boundary (HAC-76).

Services raise these instead of FastAPI HTTPException so they stay free of the
transport layer. `main.py` registers a handler that maps `status_code` 1:1, so
observable HTTP responses are unchanged.
"""

from __future__ import annotations

from typing import Literal

QuotaExhaustedCode = Literal["global_pool", "per_user_cap"]

QUOTA_EXHAUSTED_MESSAGE = (
    "experimental quota exhausted — come back on day 1 of next month"
)


class DomainError(Exception):
    """Base domain error. `status_code` maps to the HTTP status at the boundary."""

    status_code: int = 400


class NotFoundError(DomainError):
    status_code = 404


class NodeNotFoundError(NotFoundError):
    """Roadmap node not found for the user."""


class ChecklistItemNotFoundError(DomainError):
    """Unknown checklist item id for a node (bad request)."""

    status_code = 400


class MockInterviewSessionNotFoundError(NotFoundError):
    """MCQ mock interview session id not found or expired."""


class ProfileNotFoundError(NotFoundError):
    """No confirmed diagnosis/profile for the user."""


class QuotaExhaustedError(DomainError):
    """Global pool or per-user forge cap exhausted (CAR-6 kill-switch)."""

    status_code = 429

    def __init__(self, code: QuotaExhaustedCode) -> None:
        self.code = code
        super().__init__(QUOTA_EXHAUSTED_MESSAGE)
