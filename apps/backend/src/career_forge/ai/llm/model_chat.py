"""Run provider bound for one model chat life (CAR-136, CAR-137).

Forge, tutor, and mock interview read the provider captured when that life
starts. A diagnosis interview reads the provider copied from its session onto
that turn's GraphRun. The binding does not follow a later flip of the
Provider switch.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token

from career_forge.db.models.provider_switch import (
    DIRECT_PROVIDER,
    GATEWAY_PROVIDER,
    RunProvider,
)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_GATEWAY_KEY_MISSING = "The Model gateway key is missing. This run cannot continue."

_current: ContextVar[RunProvider] = ContextVar(
    "career_forge_run_provider",
    default=DIRECT_PROVIDER,
)


class ModelGatewayKeyMissing(Exception):
    """Captured Model gateway has no key. The run fails; it does not use OpenAI."""

    def __init__(self, message: str = _GATEWAY_KEY_MISSING) -> None:
        super().__init__(message)


def current_run_provider() -> RunProvider:
    return _current.get()


@contextmanager
def bound_run_provider(provider: RunProvider) -> Iterator[None]:
    token: Token[RunProvider] = _current.set(provider)
    try:
        yield
    finally:
        _current.reset(token)


def configured_model_name(model: str) -> str:
    """Bare configured id. A wire prefix is not part of the name."""
    name = model.strip()
    if name.lower().startswith("openai/"):
        return name.split("/", 1)[1]
    return name


def wire_model_name(model: str, run_provider: RunProvider) -> str:
    """Model id on the wire. The gateway prefixes ``openai/``; Direct does not."""
    bare = configured_model_name(model)
    if run_provider == GATEWAY_PROVIDER:
        return f"openai/{bare}"
    return bare
