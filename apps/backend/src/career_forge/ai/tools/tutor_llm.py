"""LLM chapter tutor + deterministic fallback (HAC-71).

Grounds answers in the chapter's key_concepts + references and the learner's open
gaps. Falls back to a deterministic, still-grounded reply when no API key is set.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from career_forge.ai.llm.client import StructuredToolClient
from career_forge.schemas.tutor import TutorContext, TutorMessage


class TutorReplyDraft(BaseModel):
    reply: str = Field(min_length=1)
    used_concepts: list[str] = Field(default_factory=list)


def _format_context(context: TutorContext) -> str:
    lines = [f"Capítulo: {context.node_title or context.node_id or 'trilha'}"]
    if context.key_concepts:
        lines.append("Conceitos-chave do capítulo: " + "; ".join(context.key_concepts))
    if context.references:
        lines.append("Referências oficiais:")
        for ref in context.references:
            lines.append(f"- {ref.title}" + (f" ({ref.url})" if ref.url else ""))
    if context.open_gaps:
        lines.append("Lacunas abertas do aluno (aborde proativamente): " + "; ".join(context.open_gaps))
    return "\n".join(lines)


def _format_history(history: list[TutorMessage]) -> str:
    if not history:
        return ""
    turns = [f"{m.role}: {m.content}" for m in history[-6:]]
    return "\n\n## Conversa anterior\n" + "\n".join(turns)


def _fallback_reply(message: str, context: TutorContext) -> TutorReplyDraft:
    title = context.node_title or "este capítulo"
    parts = [f"Sobre {title}: vamos destrinchar sua dúvida."]
    if context.key_concepts:
        parts.append(
            "Os conceitos centrais aqui são "
            + ", ".join(context.key_concepts[:4])
            + ". Comece relacionando sua pergunta a eles."
        )
    if context.open_gaps:
        parts.append(f"Atenção à sua lacuna aberta: {context.open_gaps[0]}.")
    if context.references:
        parts.append(f"Referência para aprofundar: {context.references[0].title}.")
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
    ) -> TutorReplyDraft:
        system = (
            "Você é um tutor técnico do Career Forge, focado em UM capítulo de estudo. "
            "Responda à dúvida do aluno de forma didática e concisa (máx ~6 frases), em "
            "português (BR). Ancore a explicação nos conceitos-chave e nas referências "
            "oficiais fornecidas, citando-as pelo título quando relevante. Se o aluno tem "
            "lacunas abertas, aborde-as proativamente. Não invente referências. Liste em "
            "`used_concepts` os conceitos-chave que você efetivamente usou."
        )
        user = (
            f"{_format_context(context)}{_format_history(history)}\n\n"
            f"## Pergunta do aluno\n{message}\n\nResponda agora."
        )
        return self._client.invoke(system=system, user=user, schema=TutorReplyDraft)


def generate_tutor_reply(
    *,
    message: str,
    history: list[TutorMessage],
    context: TutorContext,
) -> TutorReplyDraft:
    """Synchronous tutor reply — LLM when configured, else deterministic fallback."""
    try:
        tutor = OpenAiTutor()
    except RuntimeError:
        return _fallback_reply(message, context)
    try:
        return tutor._invoke(message=message, history=history, context=context)
    except Exception:
        return _fallback_reply(message, context)
