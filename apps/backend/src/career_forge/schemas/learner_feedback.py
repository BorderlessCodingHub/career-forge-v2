"""Learner product note and the access-desk queue (LABS01-170)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LearnerFeedbackCreate(BaseModel):
    """The only accepted input is the message and an optional display path.

    A client-supplied email is ignored. The server copies the account email.
    """

    model_config = ConfigDict(extra="ignore")

    message: str = Field(max_length=4000)
    path: str | None = Field(default=None, max_length=2000)


class LearnerFeedbackAccepted(BaseModel):
    accepted: bool = True


class OperatorFeedbackNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    message: str
    email: str
    path: str | None
    created_at: datetime
    replied_at: datetime | None


class OperatorFeedbackNoteListResponse(BaseModel):
    notes: list[OperatorFeedbackNoteResponse]


class OperatorFeedbackReplyPatch(BaseModel):
    replied: bool
