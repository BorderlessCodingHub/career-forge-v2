"""Shared demo user Ana state — seed, roadmap fallback, demo API."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEMO_ANA_EXTERNAL_ID = "demo-ana"

DEMO_ANA_PROFILE = {
    "track_id": "rag-engineer-beginner",
    "goal": "rag-engineer",
    "motivation": "I want to ship grounded RAG systems for production knowledge bases.",
}

# Pitch-ready graph on rag-engineer-beginner spine.
DEMO_ANA_SKILL_STATE: dict[str, dict[str, Any]] = {
    "rag-embeddings": {
        "status": "aprovado",
        "mastery_score": 65,
        "priority": "low",
        "evidence": {
            "strengths": ["Solid grasp of embedding fundamentals"],
            "gaps": [],
            "next_action": "Advance to chunking and retrieval.",
        },
    },
    "rag-chunking": {
        "status": "aprovado",
        "mastery_score": 78,
        "priority": "low",
        "evidence": {
            "strengths": ["Chooses chunk size and overlap thoughtfully"],
            "gaps": [],
            "next_action": "Apply chunking in a retrieval pipeline.",
        },
    },
    "rag-retrieval": {
        "status": "em_estudo",
        "mastery_score": 42,
        "priority": "high",
        "rationale": "Primary gap — focus of onboarding",
    },
    "rag-rerank": {
        "status": "recomendado",
        "mastery_score": 35,
        "priority": "high",
    },
    "rag-grounding": {
        "status": "validar",
        "mastery_score": 0,
        "priority": "high",
        "rationale": "Next step — live validation",
    },
    "rag-eval": {"status": "bloqueado", "mastery_score": 0, "priority": None},
    "rag-production": {"status": "bloqueado", "mastery_score": 0, "priority": None},
}

DEMO_ANA_VALIDATIONS: list[dict[str, Any]] = [
    {
        "skill_node_id": "rag-embeddings",
        "score": 65,
        "passed": True,
        "feedback": "Solid embeddings fundamentals — ready for chunking.",
        "questions": [
            {
                "id": "rag-emb-q1",
                "index": 1,
                "label": "conceito",
                "prompt": "In your own words, what does an embedding capture about text?",
                "rubric_criterion": "Describe embedding as dense semantic vector",
            },
            {
                "id": "rag-emb-q2",
                "index": 2,
                "label": "aplicação",
                "prompt": "How would you pick an embedding model for a product corpus?",
                "rubric_criterion": "Name size vs quality trade-off",
            },
            {
                "id": "rag-emb-q3",
                "index": 3,
                "label": "aprofundamento",
                "prompt": "Explain cosine similarity to a junior teammate.",
                "rubric_criterion": "Interpret similarity on a small example",
            },
        ],
        "answers": [
            {
                "question_id": "rag-emb-q1",
                "answer": "An embedding is a dense vector that places similar meaning nearby in space.",
            },
            {
                "question_id": "rag-emb-q2",
                "answer": "I balance latency and quality — start with a strong open model and measure recall.",
            },
            {
                "question_id": "rag-emb-q3",
                "answer": "Cosine similarity measures angle between vectors; closer to 1 means more similar.",
            },
        ],
    },
    {
        "skill_node_id": "rag-chunking",
        "score": 78,
        "passed": True,
        "feedback": "Good chunking judgment — size, overlap, and metadata.",
        "questions": [
            {
                "id": "rag-chunk-q1",
                "index": 1,
                "label": "conceito",
                "prompt": "When would you prefer semantic chunking over fixed windows?",
                "rubric_criterion": "Explain fixed vs semantic chunking",
            },
            {
                "id": "rag-chunk-q2",
                "index": 2,
                "label": "aplicação",
                "prompt": "How do you choose chunk size for a docs corpus?",
                "rubric_criterion": "Justify chunk size for a sample corpus",
            },
            {
                "id": "rag-chunk-q3",
                "index": 3,
                "label": "aprofundamento",
                "prompt": "Why does chunk metadata matter at retrieval time?",
                "rubric_criterion": "Show how metadata survives into retrieval",
            },
        ],
        "answers": [
            {
                "question_id": "rag-chunk-q1",
                "answer": "Semantic chunking when section boundaries matter more than token windows.",
            },
            {
                "question_id": "rag-chunk-q2",
                "answer": "I start around 400–800 tokens with overlap and tune on retrieval evals.",
            },
            {
                "question_id": "rag-chunk-q3",
                "answer": "Source and section metadata let the answer cite and filter chunks correctly.",
            },
        ],
    },
]


def load_demo_diagnosis(path: Path | None = None) -> dict[str, Any]:
    if path is not None:
        fixture = path
    else:
        fixture = Path(__file__).resolve().parents[1] / "fixtures" / "diagnosis_response.json"
    with fixture.open(encoding="utf-8") as handle:
        return json.load(handle)
