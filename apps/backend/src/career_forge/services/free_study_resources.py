"""Keep saved roadmap resources free and tied to this forge's search."""

from __future__ import annotations

import re
from collections.abc import Iterable
from urllib.parse import urlparse

from career_forge.schemas.study_plan import (
    StudyPlan,
    StudyPlanNode,
    StudyPlanTask,
    StudyResource,
)
from career_forge.services.forge_locale import forge_output_locale

PAID_HOSTS = frozenset(
    {
        "udemy.com",
        "coursera.org",
        "alura.com.br",
        "pluralsight.com",
        "frontendmasters.com",
        "educative.io",
        "oreilly.com",
        "packtpub.com",
        "udacity.com",
        "codecademy.com",
        "datacamp.com",
        "skillshare.com",
        "manning.com",
    },
)

PAID_PLATFORM_NAMES = (
    "Udemy",
    "Coursera",
    "Alura",
    "Pluralsight",
    "Frontend Masters",
    "Educative",
    "O'Reilly",
    "Packt",
    "LinkedIn Learning",
    "Udacity",
    "Codecademy",
    "DataCamp",
    "Skillshare",
    "Manning",
)

_LINKEDIN_HOST = "linkedin.com"
_LINKEDIN_LEARNING_PATH = "/learning"
_BRAND_ALIASES = ("Oreilly", "O’Reilly")
_BRAND = re.compile(
    r"\b(?:"
    + "|".join(
        sorted(
            (re.escape(name) for name in (*PAID_PLATFORM_NAMES, *_BRAND_ALIASES)),
            key=len,
            reverse=True,
        ),
    )
    + r")\b",
    re.IGNORECASE,
)
_FALLBACKS = {
    "pt-BR": {
        "why_now": "Segue a trilha.",
        "strategy": "Seguir com fontes gratuitas.",
        "title": "Próximo passo",
        "task_title": "Praticar",
        "outcome": "Aplicar o que estudou.",
        "evidence": "Mostrar o que fez.",
    },
    "en": {
        "why_now": "Continue the trail.",
        "strategy": "Follow the trail with free sources.",
        "title": "Next step",
        "task_title": "Practice",
        "outcome": "Apply what you studied.",
        "evidence": "Show what you did.",
    },
}


def free_search_rule() -> str:
    """Instruction for the three research searches. Does not add a search."""
    return (
        "Cite only free resources the learner can use without paying. "
        "Prefer a strong free resource in Portuguese when one exists; "
        "otherwise cite official documentation in English. "
        "If a result is paid, cite a free substitute instead. "
        f"Do not cite these paid platforms: {_platform_list()}."
    )


def free_plan_rule() -> str:
    """Instruction for the planner that writes node resources."""
    return (
        "Attach a resource only when its URL appears in research_state and "
        "you are sure the learner can use it without paying. "
        "Prefer a strong free resource in Portuguese when one exists; "
        "otherwise official documentation in English. "
        "Never name a paid platform in titles, tasks, strategy, or why_now. "
        f"Paid platforms: {_platform_list()}. "
        "If no free researched source fits, leave resources empty."
    )


def evaluator_system(research_urls: list[str] | None = None) -> str:
    """Evaluator prompt: revise paid, invented, or unnamed-free sources."""
    listed = "\n".join(f"- {url}" for url in research_urls or []) or "- (none)"
    return (
        "You are the Career Forge quality evaluator. "
        "Critique study plans for tech career transitions. "
        "Mark revise if sequence, practice, evidence, sources, or context fit is missing. "
        "Also mark revise when a resource URL is not in the researched URL list, "
        "when a resource host is a paid platform, or when the plan names a paid platform. "
        "A paid host includes its subdomains. linkedin.com counts only when the path "
        "is /learning. "
        f"Paid platforms: {_platform_list()}. "
        f"Researched URLs:\n{listed}"
    )


def research_urls_from_events(events: Iterable[dict]) -> list[str]:
    """Citation URLs already shown on the forge timeline."""
    urls: list[str] = []
    for event in events:
        for source in event.get("sources") or []:
            url = source.get("url")
            if url:
                urls.append(str(url))
    return urls


def restrict_plan_to_free_sources(
    plan: StudyPlan,
    research_urls: Iterable[str],
    *,
    locale: str | None = None,
) -> StudyPlan:
    """Drop paid or invented resources and paid-platform sentences."""
    allowed = {_source_key(url) for url in research_urls}
    fallbacks = _FALLBACKS[forge_output_locale(locale)]
    return plan.model_copy(
        update={
            "strategy": _clean_prose(plan.strategy, fallbacks["strategy"]),
            "nodes": [_clean_node(node, allowed, fallbacks) for node in plan.nodes],
        },
    )


def _platform_list() -> str:
    return ", ".join(PAID_PLATFORM_NAMES)


def _clean_node(
    node: StudyPlanNode,
    allowed: set[str],
    fallbacks: dict[str, str],
) -> StudyPlanNode:
    return node.model_copy(
        update={
            "title": _clean_prose(node.title, fallbacks["title"]),
            "why_now": _clean_prose(node.why_now, fallbacks["why_now"]),
            "key_concepts": _clean_concepts(node.key_concepts),
            "tasks": [_clean_task(task, fallbacks) for task in node.tasks],
            "resources": [
                resource
                for resource in node.resources
                if _keep_resource(resource, allowed)
            ],
        },
    )


def _clean_task(task: StudyPlanTask, fallbacks: dict[str, str]) -> StudyPlanTask:
    return task.model_copy(
        update={
            "title": _clean_prose(task.title, fallbacks["task_title"]),
            "outcome": _clean_prose(task.outcome, fallbacks["outcome"]),
            "evidence_prompt": _clean_prose(task.evidence_prompt, fallbacks["evidence"]),
        },
    )


def _keep_resource(resource: StudyResource, allowed: set[str]) -> bool:
    if _is_paid_url(resource.url):
        return False
    if _source_key(resource.url) not in allowed:
        return False
    if _BRAND.search(resource.title) or _BRAND.search(resource.snippet):
        return False
    return True


def _clean_concepts(concepts: list[str]) -> list[str]:
    cleaned: list[str] = []
    for concept in concepts:
        if not _BRAND.search(concept):
            cleaned.append(concept)
            continue
        stripped = _tidy(_BRAND.sub("", concept)).strip(" .")
        if stripped:
            cleaned.append(stripped)
    return cleaned


def _clean_prose(text: str, fallback: str) -> str:
    sentences = _sentences(text)
    if len(sentences) > 1:
        kept = [sentence for sentence in sentences if not _BRAND.search(sentence)]
        joined = _tidy(" ".join(kept))
        if _has_words(joined):
            return joined
        return fallback
    stripped = _tidy(_BRAND.sub("", text))
    if _has_words(stripped):
        return stripped
    return fallback


def _sentences(text: str) -> list[str]:
    """Split on sentence ends. A dot inside Node.js or 3.11 stays in the sentence."""
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", text)
    return [part.strip() for part in parts if part.strip()]


def _has_words(text: str) -> bool:
    return bool(text.strip(" .!?"))


def _tidy(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    collapsed = re.sub(r"\s+([.!?])", r"\1", collapsed)
    return re.sub(r"([.!?]){2,}", r"\1", collapsed).strip()


def _is_paid_url(url: str) -> bool:
    host = _hostname(url)
    if host == _LINKEDIN_HOST or host.endswith(f".{_LINKEDIN_HOST}"):
        path = urlparse(url).path or "/"
        return path == _LINKEDIN_LEARNING_PATH or path.startswith(
            f"{_LINKEDIN_LEARNING_PATH}/",
        )
    return any(host == paid or host.endswith(f".{paid}") for paid in PAID_HOSTS)


def _hostname(url: str) -> str:
    host = (urlparse(url).hostname or "").lower()
    if host.startswith("www."):
        return host[4:]
    return host


def _source_key(url: str) -> str:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    path = (parsed.path or "").rstrip("/")
    query = f"?{parsed.query}" if parsed.query else ""
    scheme = (parsed.scheme or "https").lower()
    return f"{scheme}://{host}{path}{query}"
