"""LLM chapter tutor + deterministic fallback (HAC-71).

Grounds answers in the chapter's key_concepts + references and the learner's open
gaps. Falls back to a deterministic, still-grounded reply when no API key is set.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.ai.tracing import LlmTraceContext
from career_forge.schemas.tutor import TutorContext, TutorMessage


class TutorReplyDraft(BaseModel):
    reply: str = Field(min_length=1)
    used_concepts: list[str] = Field(default_factory=list)


def _format_context(context: TutorContext) -> str:
    lines = [f"Chapter: {context.node_title or context.node_id or 'trail'}"]
    if context.key_concepts:
        lines.append("Chapter key concepts: " + "; ".join(context.key_concepts))
    if context.references:
        lines.append("Official references:")
        for ref in context.references:
            lines.append(f"- {ref.title}" + (f" ({ref.url})" if ref.url else ""))
    if context.open_gaps:
        lines.append("Learner open gaps (address proactively): " + "; ".join(context.open_gaps))
    return "\n".join(lines)


def _format_history(history: list[TutorMessage]) -> str:
    if not history:
        return ""
    turns = [f"{m.role}: {m.content}" for m in history[-6:]]
    return "\n\n## Prior conversation\n" + "\n".join(turns)


def _fallback_reply(message: str, context: TutorContext) -> TutorReplyDraft:
    title = context.node_title or "this chapter"
    parts = [f"About {title}: let's break down your question."]
    if context.key_concepts:
        parts.append(
            "The core concepts here are "
            + ", ".join(context.key_concepts[:4])
            + ". Start by relating your question to them."
        )
    if context.open_gaps:
        parts.append(f"Watch your open gap: {context.open_gaps[0]}.")
    if context.references:
        parts.append(f"Reference to go deeper: {context.references[0].title}.")
    return TutorReplyDraft(reply=" ".join(parts), used_concepts=context.key_concepts[:4])


class OpenAiTutor:
    def __init__(self, *, model: str | None = None, api_key: str | None = None) -> None:
        self._client = StructuredToolClient(
            model_env="TUTOR_MODEL",
            default_model="gpt-5.4-mini",
            temperature=0.3,
            model=model,
            api_key=api_key,
        )

    def _invoke(
        self,
        *,
        message: str,
        history: list[TutorMessage],
        context: TutorContext,
        trace: LlmTraceContext | None = None,
    ) -> TutorReplyDraft:
        system = (
            "You are a Career Forge technical tutor focused on ONE study chapter. "
            "Answer the learner's question in a clear, concise way (max ~6 sentences), in "
            "English. Ground the explanation in the key concepts and official references "
            "provided, citing them by title when relevant. If the learner has open gaps, "
            "address them proactively. Do not invent references. List in "
            "`used_concepts` the key concepts you actually used."
        )
        user = (
            f"{_format_context(context)}{_format_history(history)}\n\n"
            f"## Learner question\n{message}\n\nAnswer now."
        )
        return self._client.invoke(
            system=system,
            user=user,
            schema=TutorReplyDraft,
            trace=trace,
        )


def generate_tutor_reply(
    *,
    message: str,
    history: list[TutorMessage],
    context: TutorContext,
    trace: LlmTraceContext | None = None,
) -> TutorReplyDraft:
    """Synchronous tutor reply — LLM when configured, else deterministic fallback."""
    try:
        tutor = OpenAiTutor()
    except RuntimeError:
        return _fallback_reply(message, context)
    try:
        return tutor._invoke(
            message=message,
            history=history,
            context=context,
            trace=trace,
        )
    except Exception:
        return _fallback_reply(message, context)
