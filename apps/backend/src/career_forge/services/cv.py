"""CV ingest — PDF text extract + heuristic signals (HAC-33)."""

from __future__ import annotations

import base64
import binascii
import logging
import re
from typing import Literal

from pypdf import PdfReader

from career_forge.schemas.cv import CvAttachment, CvParseResult, CvSignals

logger = logging.getLogger(__name__)

MAX_CV_BYTES = 5 * 1024 * 1024

SKILL_KEYWORDS: dict[str, str] = {
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "java": "Java",
    "react": "React",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "sql": "SQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "git": "Git",
    "github": "GitHub",
    "html": "HTML",
    "css": "CSS",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "api": "APIs",
    "rest": "REST",
    "graphql": "GraphQL",
}

ROLE_KEYWORDS: dict[str, str] = {
    "software engineer": "Software Engineer",
    "software developer": "Software Developer",
    "backend developer": "Backend Developer",
    "frontend developer": "Frontend Developer",
    "full stack": "Full Stack Developer",
    "fullstack": "Full Stack Developer",
    "data analyst": "Data Analyst",
    "devops": "DevOps Engineer",
    "intern": "Intern",
    "estagiário": "Estagiário",
    "estagiaria": "Estagiária",
    "desenvolvedor": "Desenvolvedor",
    "desenvolvedora": "Desenvolvedora",
    "engenheiro de software": "Engenheiro de Software",
    "engenheira de software": "Engenheira de Software",
}

YEARS_PATTERNS: list[tuple[re.Pattern[str], Literal["0-1", "1-3", "3-5", "5+"]]] = [
    (re.compile(r"\b(\d{2,}|\d{1,2}\+)\s*(?:\+?\s*)?(?:years?|yrs?|anos?)\b", re.I), "5+"),
    (re.compile(r"\b([6-9]|10|\d{2,})\s*(?:\+?\s*)?(?:years?|yrs?|anos?)\b", re.I), "5+"),
    (re.compile(r"\b([3-5])\s*(?:\+?\s*)?(?:years?|yrs?|anos?)\b", re.I), "3-5"),
    (re.compile(r"\b([1-2])\s*(?:\+?\s*)?(?:years?|yrs?|anos?)\b", re.I), "1-3"),
    (re.compile(r"\b(?:less than|under|menos de)\s*(?:a|1|one|um)\s*(?:year|ano)\b", re.I), "0-1"),
]


def _decode_pdf_bytes(attachment: CvAttachment) -> bytes | None:
    if attachment.mime_type != "application/pdf":
        return None
    try:
        raw = base64.b64decode(attachment.content_base64, validate=True)
    except (binascii.Error, ValueError):
        logger.warning("CV base64 decode failed for %s", attachment.filename)
        return None
    if not raw or len(raw) > MAX_CV_BYTES:
        logger.warning("CV payload empty or too large for %s", attachment.filename)
        return None
    if not raw.startswith(b"%PDF"):
        logger.warning("CV payload is not a PDF for %s", attachment.filename)
        return None
    return raw


def extract_pdf_text(content: bytes) -> str | None:
    """Extract plain text from PDF bytes. Returns None on any failure."""
    from io import BytesIO

    try:
        reader = PdfReader(BytesIO(content))
    except Exception:
        logger.exception("PDF reader init failed")
        return None

    try:
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception:
        logger.exception("PDF text extraction failed")
        return None

    text = "\n".join(part.strip() for part in pages if part and part.strip()).strip()
    return text or None


def extract_cv_signals(text: str) -> CvSignals:
    """Heuristic keyword pass — MVP without LLM."""
    normalized = text.lower()

    skills: list[str] = []
    seen_skills: set[str] = set()
    for keyword, label in SKILL_KEYWORDS.items():
        if keyword in normalized and label not in seen_skills:
            seen_skills.add(label)
            skills.append(label)

    roles: list[str] = []
    seen_roles: set[str] = set()
    for keyword, label in ROLE_KEYWORDS.items():
        if keyword in normalized and label not in seen_roles:
            seen_roles.add(label)
            roles.append(label)

    years_hint: Literal["0-1", "1-3", "3-5", "5+"] | None = None
    for pattern, bucket in YEARS_PATTERNS:
        match = pattern.search(text)
        if match:
            if bucket == "5+" and match.lastindex:
                raw_years = match.group(1)
                if raw_years.isdigit() and int(raw_years) <= 5:
                    continue
            years_hint = bucket
            break

    return CvSignals(skills=skills, roles=roles, years_hint=years_hint)


def parse_cv_attachment(attachment: CvAttachment | None) -> CvParseResult:
    """Parse optional CV attachment. Always fail open."""
    if attachment is None:
        return CvParseResult()

    raw = _decode_pdf_bytes(attachment)
    if raw is None:
        return CvParseResult()

    text = extract_pdf_text(raw)
    if text is None:
        return CvParseResult()

    signals = extract_cv_signals(text)
    return CvParseResult(text=text, signals=signals, parse_ok=True)


def attach_extracted_text(attachment: CvAttachment) -> CvAttachment:
    """Return attachment with extracted_text populated when parse succeeds."""
    result = parse_cv_attachment(attachment)
    if not result.parse_ok or result.text is None:
        return attachment
    return attachment.model_copy(update={"extracted_text": result.text})
