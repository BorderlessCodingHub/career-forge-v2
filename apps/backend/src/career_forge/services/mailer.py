"""Outbound mail adapters — log (dev) · Resend · SES (CAR-44 / CAR-47)."""

from __future__ import annotations

import json
import logging
from typing import Protocol, runtime_checkable
from urllib import error, request

from career_forge.config import settings

logger = logging.getLogger(__name__)


@runtime_checkable
class Mailer(Protocol):
    def send_otp(self, *, to_email: str, code: str) -> None: ...

    def send_resume_link(self, *, to_email: str, resume_url: str) -> None: ...


class LogMailer:
    """Dev/test mailer — prints payloads so local stacks need no SMTP."""

    def send_otp(self, *, to_email: str, code: str) -> None:
        logger.info(
            "OTP for %s: %s (valid ~%ss) — mailer_backend=log",
            to_email,
            code,
            settings.otp_ttl_seconds,
        )

    def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
        logger.info(
            "Resume link for %s: %s — mailer_backend=log",
            to_email,
            resume_url,
        )


class ResendMailer:
    """Prod mailer via Resend HTTP API when ``RESEND_API_KEY`` is set."""

    def send_otp(self, *, to_email: str, code: str) -> None:
        minutes = max(1, settings.otp_ttl_seconds // 60)
        self._send(
            to_email=to_email,
            subject="Your Career Forge code",
            text=(
                f"Your verification code is {code}. "
                f"It expires in {minutes} minutes."
            ),
        )

    def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
        self._send(
            to_email=to_email,
            subject="Your Career Forge resume link",
            text=(
                "Use this single-use link to resume your Career Forge roadmap "
                f"(expires in about {settings.jwt_resume_ttl_days} days):\n\n"
                f"{resume_url}\n"
            ),
        )

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
            },
        )
        try:
            with request.urlopen(req, timeout=15) as resp:
                if resp.status >= 400:
                    raise RuntimeError(f"Resend HTTP {resp.status}")
        except error.HTTPError as exc:
            raise RuntimeError(f"Resend HTTP {exc.code}") from exc


class SesMailer:
    """Prod mailer via AWS SES (boto3) when region is configured."""

    def send_otp(self, *, to_email: str, code: str) -> None:
        minutes = max(1, settings.otp_ttl_seconds // 60)
        self._send(
            to_email=to_email,
            subject="Your Career Forge code",
            text=(
                f"Your verification code is {code}. "
                f"It expires in {minutes} minutes."
            ),
        )

    def send_resume_link(self, *, to_email: str, resume_url: str) -> None:
        self._send(
            to_email=to_email,
            subject="Your Career Forge resume link",
            text=(
                "Use this single-use link to resume your Career Forge roadmap "
                f"(expires in about {settings.jwt_resume_ttl_days} days):\n\n"
                f"{resume_url}\n"
            ),
        )

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
