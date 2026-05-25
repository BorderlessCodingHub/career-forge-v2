"""Tests for LLM output normalization and structured client wiring."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from career_forge.ai.llm.client import StructuredLlmClient
from career_forge.ai.llm.errors import LlmError
from career_forge.schemas.diagnosis_interview import (
    PROFILE_DIMENSION_LABELS,
    SATURATION_CONFIDENCE_THRESHOLD,
    RubricDimension,
    RubricDimensionKey,
)
from career_forge.schemas.llm_outputs import (
    JudgeBeliefOutput,
    infer_dimension_status,
    normalize_rubric_dimension,
)


def _sample_dimension(key: RubricDimensionKey, *, confidence: float, status: str) -> RubricDimension:
    return RubricDimension(
        key=key,
        label=PROFILE_DIMENSION_LABELS[key],
        confidence=confidence,
        evidence=["evidência"],
        status=status,  # type: ignore[arg-type]
        note="",
    )


def test_infer_dimension_status_maps_low_confidence_mapped_to_needs_clarification() -> None:
    assert infer_dimension_status(0.6, "mapped") == "needs_clarification"
    assert infer_dimension_status(SATURATION_CONFIDENCE_THRESHOLD, "mapped") == "mapped"


def test_judge_belief_output_to_belief_state_aligns_keys() -> None:
    output = JudgeBeliefOutput(
        motivation_goal=_sample_dimension("motivation_goal", confidence=0.8, status="mapped"),
        background_transfer=_sample_dimension("background_transfer", confidence=0.4, status="pending"),
        learning_velocity=_sample_dimension("learning_velocity", confidence=0.5, status="needs_clarification"),
        hands_on_proof=_sample_dimension("hands_on_proof", confidence=0.68, status="mapped"),
        constraints=_sample_dimension("constraints", confidence=0.77, status="mapped"),
    )
    belief = output.to_belief_state()
    assert belief.dimensions["motivation_goal"].status == "mapped"
    assert belief.dimensions["hands_on_proof"].key == "hands_on_proof"


def test_normalize_rubric_dimension_fills_note_from_evidence() -> None:
    dim = RubricDimension(
        key="constraints",
        label="Contexto real",
        confidence=0.8,
        evidence=["2 horas por dia"],
        status="mapped",
        note="",
    )
    normalized = normalize_rubric_dimension("constraints", dim)
    assert normalized.note == "2 horas por dia"


@pytest.mark.asyncio
async def test_structured_llm_client_validates_model_output() -> None:
    mock_result = JudgeBeliefOutput(
        motivation_goal=_sample_dimension("motivation_goal", confidence=0.8, status="mapped"),
        background_transfer=_sample_dimension("background_transfer", confidence=0.4, status="pending"),
        learning_velocity=_sample_dimension("learning_velocity", confidence=0.5, status="needs_clarification"),
        hands_on_proof=_sample_dimension("hands_on_proof", confidence=0.68, status="mapped"),
        constraints=_sample_dimension("constraints", confidence=0.77, status="mapped"),
    )
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(return_value=mock_result)

    with patch("career_forge.ai.llm.client.ChatOpenAI"):
        client = StructuredLlmClient("gpt-4.1-nano")
        with patch.object(client, "_structured_runnable", return_value=mock_runnable):
            result = await client.invoke(
                system="system",
                user="user",
                schema=JudgeBeliefOutput,
            )

    assert result.motivation_goal.confidence == 0.8


@pytest.mark.asyncio
async def test_structured_llm_client_wraps_validation_errors() -> None:
    mock_runnable = MagicMock()
    mock_runnable.ainvoke = AsyncMock(return_value={"motivation_goal": "invalid"})

    with patch("career_forge.ai.llm.client.ChatOpenAI"):
        client = StructuredLlmClient("gpt-4.1-nano")
        with patch.object(client, "_structured_runnable", return_value=mock_runnable):
            with pytest.raises(LlmError):
                await client.invoke(system="system", user="user", schema=JudgeBeliefOutput)
