"""Generate the 16 CAR-18 golden case fixtures (hand-seeds + provisional snapshots).

Run from apps/backend::

    PYTHONPATH=src python -m scripts.generate_golden_cases
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

_BACKEND_ROOT = Path(__file__).resolve().parents[1]
_SRC = _BACKEND_ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from career_forge.paths import GOAL_TO_CATALOG_TRACK, golden_cases_dir  # noqa: E402
from career_forge.services.lean_forge import load_must_have_ids  # noqa: E402
from career_forge.services.must_have_coverage import (  # noqa: E402
    coverage_for_goal,
)

GOALS = ("rag-engineer", "agent-engineer", "llm-evals", "fine-tuning")
PERSONAS = ("early", "mid", "staff", "soft-gated-weak")

# Hand-seed bands (grill lock). Midpoint weak↔early → 0.50 cutoff.
PROFILE_SCORE: dict[str, float] = {
    "soft-gated-weak": 0.42,
    "early": 0.58,
    "mid": 0.75,
    "staff": 0.90,
}

GOAL_COPY: dict[str, dict[str, Any]] = {
    "rag-engineer": {
        "label_prefix": "RAG",
        "strengths": {
            "soft-gated-weak": ["Curious about LLMs", "Can read Python"],
            "early": ["Knows embeddings exist", "Built one toy chatbot"],
            "mid": ["Shipped retrieval in a side project", "Understands chunking tradeoffs"],
            "staff": ["Owned production RAG evals", "Debugged retrieval regressions"],
        },
        "gaps": {
            "soft-gated-weak": ["No retrieval practice", "Unclear grounding"],
            "early": ["Hybrid search", "Reranking"],
            "mid": ["Latency/cost tuning", "Orchestration patterns"],
            "staff": ["Multi-index routing", "Online eval loops"],
        },
        "validation_preview": {
            "soft-gated-weak": "In one paragraph, what does retrieval do in a RAG system?",
            "early": "How would you choose a chunk size for a FAQ knowledge base?",
            "mid": "Explain when hybrid search beats dense-only retrieval.",
            "staff": "How do you detect and roll back a retrieval quality regression?",
        },
    },
    "agent-engineer": {
        "label_prefix": "Agent",
        "strengths": {
            "soft-gated-weak": ["Writes scripts", "Heard of tools"],
            "early": ["Called one tool API", "Understands prompts"],
            "mid": ["Built a tool-using agent", "Logs tool failures"],
            "staff": ["Shipped multi-step agents", "Owns guardrails"],
        },
        "gaps": {
            "soft-gated-weak": ["No tool orchestration", "No failure handling"],
            "early": ["Planning loops", "Memory"],
            "mid": ["Multi-agent boundaries", "Observability"],
            "staff": ["MCP fleets", "Policy enforcement"],
        },
        "validation_preview": {
            "soft-gated-weak": "What is a tool call in an agent workflow?",
            "early": "How would you retry a failed tool call safely?",
            "mid": "When should an agent plan versus act immediately?",
            "staff": "How do you isolate blast radius when one tool misbehaves?",
        },
    },
    "llm-evals": {
        "label_prefix": "Evals",
        "strengths": {
            "soft-gated-weak": ["Cares about quality", "Used ChatGPT"],
            "early": ["Wrote a checklist", "Ran manual spot-checks"],
            "mid": ["Built offline eval sets", "Tracked regressions"],
            "staff": ["Owns LLM-as-judge + online monitors", "Cost/latency budgets"],
        },
        "gaps": {
            "soft-gated-weak": ["No metrics vocabulary", "No datasets"],
            "early": ["LLM-as-judge bias", "Tracing"],
            "mid": ["Online evals", "Prompt versioning"],
            "staff": ["Guardrail eval suites", "LLMOps handoff"],
        },
        "validation_preview": {
            "soft-gated-weak": "Name one metric you could use to score model answers.",
            "early": "How would you build a small golden set for a FAQ bot?",
            "mid": "When is LLM-as-judge risky, and how do you calibrate it?",
            "staff": "Design an online eval that catches silent quality drops.",
        },
    },
    "fine-tuning": {
        "label_prefix": "Fine-tuning",
        "strengths": {
            "soft-gated-weak": ["Trained a classic ML model", "Comfortable with data"],
            "early": ["Tried one LoRA notebook", "Knows SFT exists"],
            "mid": ["Prepared SFT datasets", "Compared LoRA vs full FT"],
            "staff": ["Shipped aligned models", "Owns eval + serve path"],
        },
        "gaps": {
            "soft-gated-weak": ["When-to-tune judgment", "No LoRA practice"],
            "early": ["DPO/alignment", "Quantization"],
            "mid": ["Distributed training", "Serving"],
            "staff": ["Multi-tenant serve SLOs", "Data governance"],
        },
        "validation_preview": {
            "soft-gated-weak": "When would fine-tuning be the wrong tool versus prompting?",
            "early": "What does LoRA change compared to full fine-tuning?",
            "mid": "How do you decide between SFT and preference optimization?",
            "staff": "How do you evaluate a tuned model before production serve?",
        },
    },
}


def _belief_notes(persona: str, score: float) -> dict[str, Any]:
    # Spread confidences around profile_score for rubric context only.
    deltas = {
        "motivation_goal": 0.05,
        "background_transfer": -0.02,
        "learning_velocity": 0.0,
        "hands_on_proof": -0.05 if persona != "staff" else 0.03,
        "constraints": 0.02,
    }
    notes = {
        "soft-gated-weak": "thin evidence — soft gate expected",
        "early": "early BASE/PSP transfer signals",
        "mid": "solid mid-spectrum application evidence",
        "staff": "staff-level ownership evidence",
    }
    out: dict[str, Any] = {}
    for key, delta in deltas.items():
        conf = max(0.05, min(0.98, round(score + delta, 2)))
        out[key] = {"confidence": conf, "note": notes[persona]}
    return out


def _forged_ids(goal_id: str, persona: str) -> list[str]:
    must = load_must_have_ids(goal_id)
    if persona == "soft-gated-weak":
        # Lean smoke: first 4 must-haves (subset of allowlist).
        return must[:4]
    if persona == "early":
        return must[:7]  # 70%
    if persona == "mid":
        return must[:8] + ["noise-extra"]
    # staff — strong coverage
    return list(must)


def _build_case(goal_id: str, persona: str) -> dict[str, Any]:
    copy = GOAL_COPY[goal_id]
    score = PROFILE_SCORE[persona]
    track = GOAL_TO_CATALOG_TRACK[goal_id]
    forged = _forged_ids(goal_id, persona)
    coverage = coverage_for_goal(goal_id, forged)
    soft = persona == "soft-gated-weak"
    primary = load_must_have_ids(goal_id)[0]

    labels = {
        "soft-gated-weak": f"{copy['label_prefix']} explorer (low confidence)",
        "early": f"Early {copy['label_prefix']} learner",
        "mid": f"Mid {copy['label_prefix']} practitioner",
        "staff": f"Staff {copy['label_prefix']} engineer",
    }

    return {
        "case_id": f"{goal_id}__{persona}",
        "goal_id": goal_id,
        "persona": persona,
        "blurb": (
            f"Synthetic BASE/PSP {persona} persona for {goal_id}. "
            f"Hand-seeded profile_score={score}."
        ),
        "transcript_context": [
            {
                "role": "interviewer",
                "text": f"What have you built related to {goal_id}?",
            },
            {
                "role": "learner",
                "text": copy["strengths"][persona][0],
            },
        ],
        "belief_notes": _belief_notes(persona, score),
        "diagnosis": {
            "profile": {
                "label": labels[persona],
                "track_id": track,
                "persona_slug": f"{goal_id}_{persona}",
            },
            "strengths": copy["strengths"][persona],
            "gaps": copy["gaps"][persona],
            "starting_priorities": load_must_have_ids(goal_id)[:3],
            "estimated_mastery": {
                node_id: max(5, int(score * 100) - i * 5)
                for i, node_id in enumerate(load_must_have_ids(goal_id)[:5])
            },
            "profile_score": score,
        },
        "expectations": {
            "soft_gated": soft,
            "min_pre_inject_coverage": None if soft else 0.7,
        },
        "snapshot": {
            "source": "provisional-harness",
            "forged_node_ids": forged,
            "pre_inject_coverage": round(coverage.coverage, 4),
            "validation_sample": {
                "node_id": primary,
                "question_preview": copy["validation_preview"][persona],
            },
            "scored_at": None,
            "scorecard": None,
        },
    }


def main() -> int:
    root = golden_cases_dir()
    root.mkdir(parents=True, exist_ok=True)
    for goal in GOALS:
        for persona in PERSONAS:
            payload = _build_case(goal, persona)
            path = root / f"{payload['case_id']}.json"
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"wrote {path.relative_to(root.parent.parent)}")
    print("OK — 16 golden cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
