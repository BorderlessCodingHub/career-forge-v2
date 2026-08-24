"""Resend HTTP client — User-Agent required to pass Cloudflare (CAR-84)."""

from __future__ import annotations

from io import BytesIO
from urllib import error

import pytest

from career_forge.config import settings
from career_forge.services.mailer import ResendMailer


def test_resend_send_sets_user_agent(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.resend_api_key = "re_test_key"
    captured: dict[str, str] = {}

    class _Resp:
        status = 200

        def __enter__(self) -> "_Resp":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def read(self) -> bytes:
            return b'{"id":"ok"}'

    def _urlopen(req: object, timeout: int = 0) -> _Resp:
        del timeout
        headers = getattr(req, "headers", {})
        captured.update({str(k).lower(): str(v) for k, v in headers.items()})
        return _Resp()

    monkeypatch.setattr("career_forge.services.mailer.request.urlopen", _urlopen)

    ResendMailer()._send(to_email="pilot@example.com", subject="code", text="123456")

    assert "user-agent" in captured
    assert "CareerForge" in captured["user-agent"]
    assert captured.get("accept") == "application/json"


def test_resend_http_error_includes_body(monkeypatch: pytest.MonkeyPatch) -> None:
    settings.resend_api_key = "re_test_key"

    def _urlopen(req: object, timeout: int = 0) -> object:
        del req, timeout
        raise error.HTTPError(
            url="https://api.resend.com/emails",
            code=403,
            msg="Forbidden",
            hdrs=None,  # type: ignore[arg-type]
            fp=BytesIO(b"error code: 1010\n"),
        )

    monkeypatch.setattr("career_forge.services.mailer.request.urlopen", _urlopen)

    with pytest.raises(RuntimeError, match="1010"):
        ResendMailer()._send(to_email="pilot@example.com", subject="code", text="123456")
