"""Domain errors — transport-agnostic, mapped to HTTP at the API boundary (HAC-76).

Services raise these instead of FastAPI HTTPException so they stay free of the
transport layer. `main.py` registers a handler that maps `status_code` 1:1, so
observable HTTP responses are unchanged.
"""

from __future__ import annotations


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
