"""Unit tests — CV ingest service (HAC-33)."""

from __future__ import annotations

import base64
from io import BytesIO
from unittest.mock import patch

import pytest
from pypdf import PdfWriter
from pypdf.generic import (
    ArrayObject,
    DictionaryObject,
    NameObject,
    NumberObject,
    StreamObject,
)

from career_forge.schemas.cv import CvAttachment, CvSignals
from career_forge.services.cv import (
    extract_cv_signals,
    extract_pdf_text,
    process_cv_attachment,
)


def _make_pdf_with_text(text: str) -> bytes:
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    content = StreamObject()
    content._data = f"BT /F1 12 Tf 72 720 Td ({text}) Tj ET".encode()
    page[NameObject("/Contents")] = content
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {
                    NameObject("/F1"): DictionaryObject(
                        {
                            NameObject("/Type"): NameObject("/Font"),
                            NameObject("/Subtype"): NameObject("/Type1"),
                            NameObject("/BaseFont"): NameObject("/Helvetica"),
                        },
                    ),
                },
            ),
        },
    )
    page[NameObject("/MediaBox")] = ArrayObject(
        [NumberObject(0), NumberObject(0), NumberObject(612), NumberObject(792)],
    )
    buffer = BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def _attachment_from_text(text: str, *, filename: str = "resume.pdf") -> CvAttachment:
    return CvAttachment(
        filename=filename,
        mime_type="application/pdf",
        content_base64=base64.b64encode(_make_pdf_with_text(text)).decode("ascii"),
    )


class TestExtractPdfText:
    def test_extracts_text_from_valid_pdf(self) -> None:
        pdf = _make_pdf_with_text("Python FastAPI Git")
        text = extract_pdf_text(pdf)
        assert text is not None
        assert "Python" in text

    def test_returns_none_for_invalid_bytes(self) -> None:
        assert extract_pdf_text(b"not-a-pdf") is None


class TestExtractCvSignals:
    def test_detects_skills_roles_and_years(self) -> None:
        body = (
            "Backend Developer with 3 years experience. "
            "Skills: Python, FastAPI, Git, PostgreSQL, REST APIs."
        )
        signals = extract_cv_signals(body)
        assert isinstance(signals, CvSignals)
        assert "Python" in signals.skills
        assert "FastAPI" in signals.skills
        assert "Git" in signals.skills
        assert signals.roles
        assert signals.years_hint == "3-5"

    def test_empty_text_yields_empty_signals(self) -> None:
        signals = extract_cv_signals("")
        assert signals.skills == []
        assert signals.roles == []
        assert signals.years_hint is None


class TestProcessCvAttachment:
    def test_none_attachment_fails_open(self) -> None:
        result = process_cv_attachment(None)
        assert result.parse_ok is False
        assert result.text is None
        assert result.signals is None

    def test_valid_pdf_returns_text_and_signals(self) -> None:
        attachment = _attachment_from_text(
            "Software Developer — 2 years. Python JavaScript React Git.",
        )
        result = process_cv_attachment(attachment)
        assert result.parse_ok is True
        assert result.text
        assert result.signals is not None
        assert "Python" in result.signals.skills

    def test_enrich_cv_attachment_sets_extracted_text(self) -> None:
        from career_forge.services.cv import enrich_cv_attachment

        attachment = _attachment_from_text("Python developer with Git experience.")
        enriched = enrich_cv_attachment(attachment)
        assert enriched.extracted_text is not None
        assert "Python" in enriched.extracted_text

    def test_invalid_base64_fails_open(self) -> None:
        attachment = CvAttachment(
            filename="bad.pdf",
            mime_type="application/pdf",
            content_base64="!!!not-base64!!!",
        )
        result = process_cv_attachment(attachment)
        assert result.parse_ok is False
        assert result.text is None

    def test_non_pdf_header_fails_open(self) -> None:
        payload = base64.b64encode(b"plain-text-not-pdf").decode("ascii")
        attachment = CvAttachment(
            filename="fake.pdf",
            mime_type="application/pdf",
            content_base64=payload,
        )
        result = process_cv_attachment(attachment)
        assert result.parse_ok is False

    def test_corrupt_pdf_fails_open(self) -> None:
        payload = base64.b64encode(b"%PDF-1.4 corrupt").decode("ascii")
        attachment = CvAttachment(
            filename="broken.pdf",
            mime_type="application/pdf",
            content_base64=payload,
        )
        with patch("career_forge.services.cv.extract_pdf_text", return_value=None):
            result = process_cv_attachment(attachment)
        assert result.parse_ok is False
