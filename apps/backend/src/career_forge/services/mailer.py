"""Outbound mail adapters — log (dev) · Resend · SES (CAR-44 / CAR-47)."""

from __future__ import annotations

import json
import logging
from typing import Protocol, runtime_checkable
from urllib import error, request

from career_forge.config import settings
from career_forge.services.learner_mail import (
    operator_otp_letter,
    otp_letter,
    resume_letter,
)

logger = logging.getLogger(__name__)

# Cloudflare in front of api.resend.com returns 1010 for Python-urllib's default UA (CAR-84).
RESEND_USER_AGENT = "CareerForge/1.0 (+https://labs.borderlesscoding.com/career-forge)"
_MAX_ERROR_BODY = 300


def _otp_minutes() -> int:
    return max(1, settings.otp_ttl_seconds // 60)


def _http_error_detail(exc: error.HTTPError) -> str:
    raw = exc.read()[:_MAX_ERROR_BODY].decode("utf-8", errors="replace").strip()
    if not raw:
        return str(exc.code)
    return f"{exc.code}: {raw}"


@runtime_checkable
class Mailer(Protocol):
    def send_otp(self, *, to_email: str, code: str, locale: str | None = None) -> None: ...

    def send_operator_otp(self, *, to_email: str, code: str) -> None: ...

    def send_resume_link(
        self, *, to_email: str, resume_url: str, locale: str | None = None
    ) -> None: ...

    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None: ...

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None: ...


class LogMailer:
    """Dev/test mailer — prints payloads so local stacks need no SMTP."""

    def send_otp(self, *, to_email: str, code: str, locale: str | None = None) -> None:
        subject, text = otp_letter(
            code=code,
            minutes=_otp_minutes(),
            locale=locale,
        )
        logger.info(
            "OTP for %s: %s — mailer_backend=log\n%s\n%s",
            to_email,
            code,
            subject,
            text,
        )

    def send_operator_otp(self, *, to_email: str, code: str) -> None:
        subject, text = operator_otp_letter(code=code, minutes=_otp_minutes())
        logger.info(
            "Operator console OTP for %s: %s — not learner Email identity\n%s\n%s",
            to_email,
            code,
            subject,
            text,
        )

    def send_resume_link(
        self, *, to_email: str, resume_url: str, locale: str | None = None
    ) -> None:
        subject, text = resume_letter(
            url=resume_url,
            days=settings.jwt_resume_ttl_days,
            locale=locale,
        )
        logger.info(
            "Resume link for %s — mailer_backend=log\n%s\n%s",
            to_email,
            subject,
            text,
        )

    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None:
        logger.info(
            "Continuity email for %s: %s — mailer_backend=log\n%s",
            to_email,
            subject,
            text,
        )

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
        logger.info(
            "Billing email for %s: %s — mailer_backend=log\n%s",
            to_email,
            subject,
            text,
        )


class ResendMailer:
    """Prod mailer via Resend HTTP API when ``RESEND_API_KEY`` is set."""

    def send_otp(self, *, to_email: str, code: str, locale: str | None = None) -> None:
        subject, text = otp_letter(code=code, minutes=_otp_minutes(), locale=locale)
        self._send(to_email=to_email, subject=subject, text=text)

    def send_operator_otp(self, *, to_email: str, code: str) -> None:
        subject, text = operator_otp_letter(code=code, minutes=_otp_minutes())
        self._send(to_email=to_email, subject=subject, text=text)

    def send_resume_link(
        self, *, to_email: str, resume_url: str, locale: str | None = None
    ) -> None:
        subject, text = resume_letter(
            url=resume_url,
            days=settings.jwt_resume_ttl_days,
            locale=locale,
        )
        self._send(to_email=to_email, subject=subject, text=text)

    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None:
        self._send(to_email=to_email, subject=subject, text=text)

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
        self._send(to_email=to_email, subject=subject, text=text)

    def _send(self, *, to_email: str, subject: str, text: str) -> None:
        api_key = settings.resend_api_key.strip()
        if not api_key:
            raise RuntimeError("RESEND_API_KEY is required when mailer_backend=resend")
        payload = json.dumps(
            {
                "from": settings.mail_from,
                "to": [to_email],
                "subject": subject,
                "text": text,
            }
        ).encode("utf-8")
        req = request.Request(
            "https://api.resend.com/emails",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": RESEND_USER_AGENT,
            },
        )
        try:
            with request.urlopen(req, timeout=15) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"Resend HTTP {resp.status}")
        except error.HTTPError as exc:
            raise RuntimeError(f"Resend HTTP {_http_error_detail(exc)}") from exc


class SesMailer:
    """Prod mailer via AWS SES (boto3) when region is configured."""

    def send_otp(self, *, to_email: str, code: str, locale: str | None = None) -> None:
        subject, text = otp_letter(code=code, minutes=_otp_minutes(), locale=locale)
        self._send(to_email=to_email, subject=subject, text=text)

    def send_operator_otp(self, *, to_email: str, code: str) -> None:
        subject, text = operator_otp_letter(code=code, minutes=_otp_minutes())
        self._send(to_email=to_email, subject=subject, text=text)

    def send_resume_link(
        self, *, to_email: str, resume_url: str, locale: str | None = None
    ) -> None:
        subject, text = resume_letter(
            url=resume_url,
            days=settings.jwt_resume_ttl_days,
            locale=locale,
        )
        self._send(to_email=to_email, subject=subject, text=text)

    def send_continuity(self, *, to_email: str, subject: str, text: str) -> None:
        self._send(to_email=to_email, subject=subject, text=text)

    def send_billing(self, *, to_email: str, subject: str, text: str) -> None:
        self._send(to_email=to_email, subject=subject, text=text)

    def _send(self, *, to_email: str, subject: str, text: str) -> None:
        region = settings.aws_ses_region.strip()
        if not region:
            raise RuntimeError("AWS_SES_REGION is required when mailer_backend=ses")
        try:
            import boto3  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("boto3 is required for mailer_backend=ses") from exc

        client = boto3.client("ses", region_name=region)
        client.send_email(
            Source=settings.mail_from,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Text": {"Data": text}},
            },
        )


def get_mailer() -> Mailer:
    backend = settings.mailer_backend.strip().lower()
    if backend == "resend":
        return ResendMailer()
    if backend == "ses":
        return SesMailer()
    return LogMailer()
