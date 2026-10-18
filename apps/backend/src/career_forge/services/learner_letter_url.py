"""Join the public base to a learner letter path.

A legal base has scheme http or https, a host, an optional port, and path
``/career-forge``. smtp, resend, and ses require https. Any other mailer
accepts http or https.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from career_forge.errors import MailDeliveryError

_HTTPS_MAILERS = frozenset({"smtp", "resend", "ses"})
_APP_PATH = "/career-forge"


def learner_letter_url(path: str, *, base: str, mailer_backend: str) -> str:
    """Absolute letter URL, or ``MailDeliveryError`` before a body is rendered."""
    trimmed = base.strip()
    if trimmed.endswith("/"):
        trimmed = trimmed[:-1]
    parts = urlsplit(trimmed)
    backend = mailer_backend.strip().lower()
    scheme_ok = parts.scheme == "https" or (
        parts.scheme == "http" and backend not in _HTTPS_MAILERS
    )
    if (
        not scheme_ok
        or not parts.hostname
        or "@" in parts.netloc
        or "?" in trimmed
        or "#" in trimmed
        or parts.path != _APP_PATH
        or not path.startswith("/")
    ):
        raise MailDeliveryError()
    return f"{trimmed}{path}"
