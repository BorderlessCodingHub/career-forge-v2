"""Shared LLM error types for Career Forge."""

from __future__ import annotations

import re

RETRY_MESSAGE = (
    "AI did not respond just now. Try again in a few seconds — your answers were saved."
)

PUBLIC_STREAM_ERROR = (
    "We couldn't finish your trail just now. Try again in a few minutes."
)

_OPENROUTER_KEY_URL = re.compile(
    r"https?://openrouter\.ai/\S*?/keys/[A-Za-z0-9]+",
    re.IGNORECASE,
)
_LONG_HEX = re.compile(r"\b[0-9a-fA-F]{32,}\b")
_UNSAFE_STREAM_TEXT = re.compile(
    r"https?://|[{}]|error code|user_id|traceback|openrouter|api[_ ]key|\bsk-|exception",
    re.IGNORECASE,
)


def redact_provider_secrets(text: str) -> str:
    """Drop key URLs and long hex tokens. Keep the rest for the audit row."""
    redacted = _OPENROUTER_KEY_URL.sub("[redacted-key-url]", text)
    return _LONG_HEX.sub("[redacted]", redacted)


def public_stream_error(raw: str) -> str:
    """Learner-facing stream text. Short plain sentences pass through."""
    text = raw.strip()
    if (
        text
        and len(text) <= 200
        and _UNSAFE_STREAM_TEXT.search(text) is None
        and _LONG_HEX.search(text) is None
    ):
        return text
    return PUBLIC_STREAM_ERROR


class LlmError(Exception):
    """Base error for LLM invocation failures surfaced to clients."""

    def __init__(self, message: str = RETRY_MESSAGE) -> None:
        super().__init__(message)
        self.retry_message = message


class DiagnosisInterviewLlmError(LlmError):
    """Diagnosis interview graph could not complete an LLM step."""
