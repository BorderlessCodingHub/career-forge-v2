"""Sentry init for the API. No-op when SENTRY_DSN is empty."""

from __future__ import annotations

from typing import Any

import sentry_sdk

from career_forge.config import settings


def _scrub_email(event: dict[str, Any], _hint: dict[str, Any]) -> dict[str, Any]:
    event.pop("user", None)
    return event


def init_sentry() -> None:
    dsn = settings.sentry_dsn.strip()
    if not dsn:
        return
    environment = settings.sentry_environment.strip() or settings.env
    release = settings.sentry_release.strip() or None
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        release=release,
        send_default_pii=False,
        traces_sample_rate=1.0 if settings.env.lower() != "production" else 0.1,
        before_send=_scrub_email,
    )
