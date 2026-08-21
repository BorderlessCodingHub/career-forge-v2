"""Outbound mail adapters — log (dev) · Resend · SES (CAR-44)."""

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


class LogMailer:
    """Dev/test mailer — prints the OTP so local stacks need no SMTP."""

    def send_otp(self, *, to_email: str, code: str) -> None:
        logger.info(
            "OTP for %s: %s (valid ~%ss) — mailer_backend=log",
            to_email,
            code,
            settings.otp_ttl_seconds,
        )


class ResendMailer:
    """Prod mailer via Resend HTTP API when ``RESEND_API_KEY`` is set."""

    def send_otp(self, *, to_email: str, code: str) -> None:
        api_key = settings.resend_api_key.strip()
        if not api_key:
            raise RuntimeError("RESEND_API_KEY is required when mailer_backend=resend")
        minutes = max(1, settings.otp_ttl_seconds // 60)
        payload = json.dumps(
            {
                "from": settings.mail_from,
                "to": [to_email],
                "subject": "Your Career Forge code",
                "text": (
                    f"Your verification code is {code}. "
                    f"It expires in {minutes} minutes."
                ),
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
        region = settings.aws_ses_region.strip()
        if not region:
            raise RuntimeError("AWS_SES_REGION is required when mailer_backend=ses")
        try:
            import boto3  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("boto3 is required for mailer_backend=ses") from exc

        minutes = max(1, settings.otp_ttl_seconds // 60)
        client = boto3.client("ses", region_name=region)
        client.send_email(
            Source=settings.mail_from,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": "Your Career Forge code"},
                "Body": {
                    "Text": {
                        "Data": (
                            f"Your verification code is {code}. "
                            f"It expires in {minutes} minutes."
                        )
                    }
                },
            },
        )


def get_mailer() -> Mailer:
    backend = settings.mailer_backend.strip().lower()
    if backend == "resend":
        return ResendMailer()
    if backend == "ses":
        return SesMailer()
    return LogMailer()
