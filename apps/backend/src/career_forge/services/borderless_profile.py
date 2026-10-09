"""Borderless profile membership read (CAR-128).

Password-mode inclusion comes from ``GET /api/users/profile`` field
``membership``. The learner's Borderless access token stays on the server,
encrypted, and is never returned to the browser.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Literal, Protocol, runtime_checkable
from urllib import error, request
from urllib.parse import urlsplit, urlunsplit

from cryptography.fernet import Fernet, InvalidToken

from career_forge.config import settings
from career_forge.db.models.user import User

logger = logging.getLogger(__name__)

PROFILE_READ_TIMEOUT_SECONDS = 5.0
MEMBERSHIP_RETRY_AFTER = timedelta(minutes=5)
_INCLUDED = frozenset({"base", "psp"})

ProfileFetch = Callable[[str, str, float], tuple[int, str]]
ProfileKind = Literal["label", "failed", "unrenewable"]


@dataclass(frozen=True)
class ProfileRead:
    kind: ProfileKind
    label: str | None = None


@runtime_checkable
class ProfileClient(Protocol):
    def read(self, access_token: str) -> ProfileRead: ...


def borderless_profile_url(signin_url: str) -> str:
    """Profile lives on the same origin as Borderless sign-in."""
    parts = urlsplit(signin_url.strip())
    if not parts.scheme or not parts.netloc:
        raise RuntimeError(
            "BORDERLESS_SIGNIN_URL must be absolute to read the Borderless profile"
        )
    return urlunsplit((parts.scheme, parts.netloc, "/api/users/profile", "", ""))


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _encryption_key() -> str:
    return settings.borderless_token_encryption_key.strip()


def seal_access_token(access_token: str) -> str:
    """Encrypt a Borderless access token for storage. Plaintext is not logged."""
    key = _encryption_key()
    if not key:
        raise RuntimeError(
            "BORDERLESS_TOKEN_ENCRYPTION_KEY is required to store Borderless access"
        )
    try:
        fernet = Fernet(key.encode())
    except (ValueError, TypeError) as exc:
        raise RuntimeError(
            "BORDERLESS_TOKEN_ENCRYPTION_KEY must be a Fernet key"
        ) from exc
    return fernet.encrypt(access_token.encode()).decode()


def open_access_token(ciphertext: str | None) -> str | None:
    if not ciphertext:
        return None
    key = _encryption_key()
    if not key:
        return None
    try:
        return Fernet(key.encode()).decrypt(ciphertext.encode()).decode()
    except (InvalidToken, ValueError, TypeError):
        logger.warning("borderless access token could not be opened")
        return None


def membership_label_from_payload(payload: dict) -> str:
    """BASE and PSP include. FREE, anything else, and a missing field are external."""
    raw = _first_membership_string(payload)
    if raw is None:
        return "external"
    key = raw.strip().lower()
    if key in _INCLUDED:
        return key
    return "external"


def _first_membership_string(payload: dict) -> str | None:
    candidates: list[object] = []
    data = payload.get("data")
    if isinstance(data, dict):
        user = data.get("user")
        if isinstance(user, dict):
            candidates.append(user.get("membership"))
        candidates.append(data.get("membership"))
    candidates.append(payload.get("membership"))
    for value in candidates:
        if isinstance(value, str):
            return value
    return None


def parse_profile_body(raw: str) -> ProfileRead:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return ProfileRead(kind="failed")
    if not isinstance(payload, dict):
        return ProfileRead(kind="failed")
    return ProfileRead(kind="label", label=membership_label_from_payload(payload))


def _default_profile_fetch(url: str, access_token: str, timeout: float) -> tuple[int, str]:
    req = request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as response:
            return response.status, response.read().decode("utf-8")
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return exc.code, body


class BorderlessProfileClient:
    """``GET {origin}/api/users/profile`` with the learner's Borderless access token."""

    def __init__(
        self,
        *,
        url: str,
        timeout: float = PROFILE_READ_TIMEOUT_SECONDS,
        fetch: ProfileFetch | None = None,
    ) -> None:
        self._url = url
        self._timeout = timeout
        self._fetch = fetch or _default_profile_fetch

    def read(self, access_token: str) -> ProfileRead:
        try:
            status, body = self._fetch(self._url, access_token, self._timeout)
        except Exception:
            logger.warning("borderless profile read failed")
            return ProfileRead(kind="failed")
        if status in {401, 403}:
            return ProfileRead(kind="unrenewable")
        if status != 200:
            logger.warning("borderless profile read failed status=%s", status)
            return ProfileRead(kind="failed")
        parsed = parse_profile_body(body)
        if parsed.kind != "label":
            logger.warning("borderless profile read returned an unreadable body")
        return parsed


_profile_client: ProfileClient | None = None


def get_borderless_profile_client() -> ProfileClient:
    global _profile_client
    if _profile_client is None:
        _profile_client = BorderlessProfileClient(
            url=borderless_profile_url(settings.borderless_signin_url),
        )
    return _profile_client


def set_borderless_profile_client(client: ProfileClient | None) -> None:
    global _profile_client
    _profile_client = client


def _aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _retry_waiting(user: User, now: datetime) -> bool:
    failed_at = user.membership_read_failed_at
    if failed_at is None:
        return False
    return now - _aware(failed_at) < MEMBERSHIP_RETRY_AFTER


def sync_borderless_membership(user: User, *, force: bool = False) -> None:
    """Read the profile when a stored token can still be used.

    A failed read keeps the last label. 401/403 latches until the next
    password sign-in stores a new token and reads with ``force``.
    """
    if not user.borderless_access_token:
        return
    now = _now()
    if not force:
        if user.borderless_access_unrenewable:
            return
        if _retry_waiting(user, now):
            return

    access_token = open_access_token(user.borderless_access_token)
    if access_token is None:
        user.borderless_access_unrenewable = True
        user.membership_read_failed_at = None
        return

    outcome = get_borderless_profile_client().read(access_token)
    if outcome.kind == "label" and outcome.label is not None:
        user.membership_label = outcome.label
        user.membership_entitled = outcome.label in _INCLUDED
        user.membership_read_failed_at = None
        user.borderless_access_unrenewable = False
        return
    if outcome.kind == "unrenewable":
        user.borderless_access_unrenewable = True
        user.membership_read_failed_at = None
        return
    user.borderless_access_unrenewable = False
    user.membership_read_failed_at = now
