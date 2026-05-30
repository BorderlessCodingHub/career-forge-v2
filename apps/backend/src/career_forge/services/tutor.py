"""Chapter Q&A tutor service — HAC-71.

Reuses the mock-interview chapter context (key_concepts + references + open gaps)
as the tutor's grounding, then produces a grounded reply.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from career_forge.ai.tools.tutor_llm import generate_tutor_reply
from career_forge.schemas.tutor import (
    TutorContext,
    TutorReference,
    TutorRequest,
    TutorResponse,
)
from career_forge.services.mock_interview_context import build_mock_interview_context


def load_tutor_context(
    session: Session,
    user_id: str,
    node_id: str | None,
    node_title: str | None = None,
) -> TutorContext:
    """Build chapter grounding from key_concepts, references, and open gaps."""
    if not node_id:
        return TutorContext(node_id=None, node_title=node_title)

    try:
        study_block, _ = build_mock_interview_context(session, user_id=user_id, node_id=node_id)
    except Exception:
        return TutorContext(node_id=node_id, node_title=node_title)

    references = [
        TutorReference(title=str(ref.get("title") or "Referência"), url=ref.get("url"))
        for ref in study_block.get("references") or []
    ]
    return TutorContext(
        node_id=node_id,
        node_title=node_title or study_block.get("title"),
        key_concepts=list(study_block.get("key_concepts") or []),
        references=references,
        open_gaps=list(study_block.get("open_gaps") or []),
    )


def build_tutor_response(payload: TutorRequest, context: TutorContext) -> TutorResponse:
    """Grounded chapter reply (LLM when configured, deterministic fallback otherwise)."""
    draft = generate_tutor_reply(
        message=payload.message,
        history=payload.history,
        context=context,
    )
    references = [ref.title for ref in context.references][:3]
    return TutorResponse(
        reply=draft.reply.strip(),
        references=references,
        used_concepts=draft.used_concepts or context.key_concepts[:4],
        context=context,
    )
