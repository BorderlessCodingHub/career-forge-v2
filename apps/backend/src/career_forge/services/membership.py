"""Borderless membership lookup — stub allowlist + HTTP client (CAR-45).

Soft label only: ``base | psp | external``. Does not enforce a paywall.
Swap stub → HTTP when ``MEMBERSHIP_BACKEND=http`` and Yuri's staging URL/token
are set. Fail-open: lookup errors and unknown emails resolve to ``external``.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Protocol, cast, runtime_checkable
from urllib import error, parse, request

from career_forge.config import settings
from career_forge.db.models.user import User

logger = logging.getLogger(__name__)

MembershipProgram = Literal["base", "psp"]
MembershipLabel = Literal["base", "psp", "external"]
_PROGRAMS: frozenset[str] = frozenset({"base", "psp"})


@dataclass(frozen=True)
class MembershipRecord:
    """Wire shape from ``GET …/members?email=`` plus derived soft label."""

    active: bool
    program: MembershipProgram | None

    @property
    def label(self) -> MembershipLabel:
        if self.active and self.program in _PROGRAMS:
            return self.program
        return "external"

    @property
    def entitled(self) -> bool:
        return self.label != "external"


def _unknown() -> MembershipRecord:
    return MembershipRecord(active=False, program=None)


def parse_stub_allowlist(raw: str) -> dict[str, MembershipProgram]:
    """Parse ``email:program`` comma pairs. Invalid entries are skipped."""
    mapping: dict[str, MembershipProgram] = {}
    for chunk in raw.split(","):
        piece = chunk.strip()
        if not piece or ":" not in piece:
            continue
        email, program = piece.rsplit(":", 1)
        email_key = email.strip().lower()
        program_key = program.strip().lower()
        if not email_key or program_key not in _PROGRAMS:
            continue
        mapping[email_key] = cast(MembershipProgram, program_key)
    return mapping


@runtime_checkable
class MembershipClient(Protocol):
    def lookup(self, email: str) -> MembershipRecord: ...


class StubMembershipClient:
    """Env allowlist so eng is not blocked waiting on Borderless staging."""

    def __init__(self, allowlist: dict[str, MembershipProgram] | None = None) -> None:
        self._allowlist = {
            email.strip().lower(): program for email, program in (allowlist or {}).items()
        }

    def lookup(self, email: str) -> MembershipRecord:
        program = self._allowlist.get(email.strip().lower())
        if program in _PROGRAMS:
            return MembershipRecord(active=True, program=program)
        return _unknown()


def _default_http_get(url: str, token: str, timeout: float) -> str:
    req = request.Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        },
    )
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            if resp.status >= 400:
                raise OSError(f"membership HTTP {resp.status}")
            return resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raise OSError(f"membership HTTP {exc.code}") from exc


class BorderlessMembershipClient:
    """Live ``GET {url}?email=`` → ``{ active, program }`` (CAR-45)."""

    def __init__(
        self,
        *,
        url: str,
        token: str,
        timeout: float = 5.0,
        fetch: Callable[[str, str, float], str] | None = None,
    ) -> None:
        self._url = url.rstrip("?")
        self._token = token
        self._timeout = timeout
        self._fetch = fetch or _default_http_get

    def lookup(self, email: str) -> MembershipRecord:
        query = parse.urlencode({"email": email.strip().lower()})
        url = f"{self._url}?{query}"
        try:
            raw = self._fetch(url, self._token, self._timeout)
            payload = json.loads(raw)
        except Exception:
            logger.warning("membership HTTP lookup failed; defaulting to external")
            return _unknown()
        if not isinstance(payload, dict):
            return _unknown()
        active = bool(payload.get("active") is True)
        program_raw = payload.get("program")
        program: MembershipProgram | None = None
        if isinstance(program_raw, str) and program_raw.strip().lower() in _PROGRAMS:
            program = cast(MembershipProgram, program_raw.strip().lower())
        return MembershipRecord(active=active, program=program)


def get_membership_client() -> MembershipClient:
    backend = settings.membership_backend.strip().lower()
    if backend == "http":
        url = settings.borderless_members_url.strip()
        token = settings.borderless_members_token.strip()
        if not url or not token:
            raise RuntimeError(
                "BORDERLESS_MEMBERS_URL and BORDERLESS_MEMBERS_TOKEN are required "
                "when MEMBERSHIP_BACKEND=http"
            )
        return BorderlessMembershipClient(url=url, token=token)
    return StubMembershipClient(
        allowlist=parse_stub_allowlist(settings.membership_stub_allowlist),
    )


def apply_membership_label(
    user: User,
    email: str,
    client: MembershipClient | None = None,
) -> MembershipRecord:
    """Persist soft label + entitled flag. Fail-open to ``external``."""
    resolver: MembershipClient
    try:
        resolver = client or get_membership_client()
        record = resolver.lookup(email)
    except Exception:
        logger.exception("membership lookup raised; defaulting to external")
        record = _unknown()
    user.membership_label = record.label
    user.membership_entitled = record.entitled
    return record
