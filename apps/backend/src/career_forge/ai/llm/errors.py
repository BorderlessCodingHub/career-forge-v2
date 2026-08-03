"""Shared LLM error types for Career Forge."""

from __future__ import annotations

RETRY_MESSAGE = (
    "AI did not respond just now. Try again in a few seconds — your answers were saved."
)


class LlmError(Exception):
    """Base error for LLM invocation failures surfaced to clients."""

    def __init__(self, message: str = RETRY_MESSAGE) -> None:
        super().__init__(message)
        self.retry_message = message


class DiagnosisInterviewLlmError(LlmError):
    """Diagnosis interview graph could not complete an LLM step."""
