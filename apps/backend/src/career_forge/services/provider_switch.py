"""Provider switch — one stored Run provider for the product (CAR-135)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from career_forge.ai.run import GraphRun
from career_forge.auth.operator_session import OperatorPrincipal
from career_forge.db.models.operator import Operator
from career_forge.db.models.provider_switch import (
    DIRECT_PROVIDER,
    GATEWAY_PROVIDER,
    SINGLETON_ID,
    ProviderSwitch,
    RunProvider,
)
from career_forge.errors import ConflictError
from career_forge.services.operator_access import require_access_role

_ARM_REFUSED = (
    "The Model gateway is not configured. "
    "Set OPENROUTER_API_KEY before turning the Provider switch on."
)
_DISARM_REFUSED = (
    "The Direct provider is not configured. "
    "Set OPENAI_API_KEY before turning the Provider switch off."
)


@dataclass(frozen=True)
class ProviderSwitchView:
    on: bool
    run_provider: RunProvider
    operator_email: str | None
    written_at: datetime | None


def _key_configured(name: str) -> bool:
    return bool(os.getenv(name, "").strip())


def read_provider_switch(session: Session) -> ProviderSwitchView:
    row = session.get(ProviderSwitch, SINGLETON_ID)
    if row is None:
        return ProviderSwitchView(
            on=False,
            run_provider=DIRECT_PROVIDER,
            operator_email=None,
            written_at=None,
        )
    operator = session.get(Operator, row.operator_id)
    return ProviderSwitchView(
        on=row.run_provider == GATEWAY_PROVIDER,
        run_provider=row.run_provider,
        operator_email=operator.email if operator is not None else None,
        written_at=row.written_at,
    )


_MODEL_CHAT_GRAPHS = frozenset({"roadmap_forge", "tutor", "mock_interview"})


def stamp_run_provider(run: GraphRun, session: Session) -> GraphRun:
    """Capture the Provider switch onto a forge, tutor, or mock interview run.

    Diagnosis interview, mentor, rubric validation, and the rule-based diagnosis
    graph stay on the Direct provider. A later flip does not rewrite ``run``.
    """
    if run.graph_name not in _MODEL_CHAT_GRAPHS:
        return run.model_copy(update={"run_provider": DIRECT_PROVIDER})
    return run.model_copy(
        update={"run_provider": read_provider_switch(session).run_provider},
    )


def write_provider_switch(
    session: Session,
    *,
    principal: OperatorPrincipal,
    on: bool,
) -> ProviderSwitchView:
    require_access_role(principal)
    if on and not _key_configured("OPENROUTER_API_KEY"):
        raise ConflictError(_ARM_REFUSED)
    if not on and not _key_configured("OPENAI_API_KEY"):
        raise ConflictError(_DISARM_REFUSED)
    run_provider: RunProvider = GATEWAY_PROVIDER if on else DIRECT_PROVIDER
    row = session.get(ProviderSwitch, SINGLETON_ID, with_for_update=True)
    written_at = datetime.now(UTC)
    if row is None:
        row = ProviderSwitch(
            id=SINGLETON_ID,
            run_provider=run_provider,
            operator_id=principal.operator_id,
            written_at=written_at,
        )
        session.add(row)
    else:
        row.run_provider = run_provider
        row.operator_id = principal.operator_id
        row.written_at = written_at
    session.flush()
    return read_provider_switch(session)
