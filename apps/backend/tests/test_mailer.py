"""Mail transports — Resend HTTP (CAR-84) and Gmail SMTP (CAR-141)."""

from __future__ import annotations

import smtplib
from email.message import EmailMessage
from io import BytesIO
from urllib import error

import pytest

from career_forge.config import settings
from career_forge.services.mailer import ResendMailer, get_mailer


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


_LABS_FROM = "Career Forge <careerforgelabs@gmail.com>"
_SMTP_USER = "careerforgelabs@gmail.com"
_SMTP_PASSWORD = "app-password"


class _FakeSMTP:
    """Stand-in for smtplib.SMTP. Records the Gmail session; can refuse a send."""

    sessions: list["_FakeSMTP"] = []
    refuse: BaseException | None = None

    def __init__(self, host: str, port: int, timeout: float = 0) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.started_tls = False
        self.login_args: tuple[str, str] | None = None
        self.message: EmailMessage | None = None
        _FakeSMTP.sessions.append(self)

    def __enter__(self) -> "_FakeSMTP":
        return self

    def __exit__(self, *_args: object) -> None:
        return None

    def starttls(self) -> None:
        self.started_tls = True

    def login(self, user: str, password: str) -> None:
        self.login_args = (user, password)

    def send_message(self, message: EmailMessage) -> None:
        if _FakeSMTP.refuse is not None:
            raise _FakeSMTP.refuse
        self.message = message


def _arm_smtp(monkeypatch: pytest.MonkeyPatch, *, password: str) -> None:
    _FakeSMTP.sessions = []
    _FakeSMTP.refuse = None
    monkeypatch.setattr(settings, "mailer_backend", "smtp")
    monkeypatch.setattr(settings, "mail_from", _LABS_FROM)
    monkeypatch.setattr(settings, "smtp_password", password)
    monkeypatch.setattr("career_forge.services.mailer.smtplib.SMTP", _FakeSMTP)


def test_smtp_sends_every_letter_through_gmail(monkeypatch: pytest.MonkeyPatch) -> None:
    _arm_smtp(monkeypatch, password=_SMTP_PASSWORD)
    mailer = get_mailer()

    mailer.send_otp(to_email="learner@example.com", code="123456")
    mailer.send_operator_otp(to_email="operator@example.com", code="654321")
    mailer.send_resume_link(
        to_email="learner@example.com",
        resume_url="https://labs.example/resume/abc",
    )
    mailer.send_continuity(
        to_email="learner@example.com",
        subject="Continue with Retrieval",
        text="Retrieval is the next node on your roadmap.",
    )
    mailer.send_billing(
        to_email="learner@example.com",
        subject="A charge for Career Forge failed",
        text="This link updates your card:\n\nhttps://labs.example/billing/card\n",
    )
    mailer.send_account_link(
        to_email="learner@example.com",
        url="https://labs.example/account/confirm?token=abc",
        kind="confirm",
        hours=24,
    )

    assert len(_FakeSMTP.sessions) == 6
    subjects = []
    bodies = []
    for session in _FakeSMTP.sessions:
        assert session.host == "smtp.gmail.com"
        assert session.port == 587
        assert session.started_tls is True
        assert session.login_args == (_SMTP_USER, _SMTP_PASSWORD)
        assert session.message is not None
        assert session.message["From"] == _LABS_FROM
        subjects.append(session.message["Subject"])
        bodies.append(session.message.get_content())

    assert subjects == [
        "Your Career Forge code",
        "Your Operator console code",
        "Your Career Forge resume link",
        "Continue with Retrieval",
        "A charge for Career Forge failed",
        "Confirm your Career Forge email",
    ]
    assert _FakeSMTP.sessions[0].message is not None
    assert _FakeSMTP.sessions[0].message["To"] == "learner@example.com"
    assert "123456" in bodies[0]
    assert "654321" in bodies[1]
    assert "https://labs.example/resume/abc" in bodies[2]
    assert "Retrieval is the next node" in bodies[3]
    assert "https://labs.example/billing/card" in bodies[4]
    assert "https://labs.example/account/confirm?token=abc" in bodies[5]


def test_smtp_missing_password_fails_without_connecting(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _arm_smtp(monkeypatch, password="   ")

    with pytest.raises(RuntimeError, match="SMTP_PASSWORD"):
        get_mailer().send_otp(to_email="learner@example.com", code="123456")

    assert _FakeSMTP.sessions == []


@pytest.mark.parametrize(
    "refusal",
    [
        smtplib.SMTPRecipientsRefused(
            {"learner@example.com": (550, b"Daily user sending quota exceeded")}
        ),
        OSError("timed out"),
    ],
)
def test_smtp_refusal_or_network_failure_fails_the_call(
    monkeypatch: pytest.MonkeyPatch,
    refusal: BaseException,
) -> None:
    _arm_smtp(monkeypatch, password=_SMTP_PASSWORD)
    _FakeSMTP.refuse = refusal

    with pytest.raises(RuntimeError, match="SMTP send failed"):
        get_mailer().send_otp(to_email="learner@example.com", code="123456")
