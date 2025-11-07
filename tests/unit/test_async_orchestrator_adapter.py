"""Unit tests for async MATRIZ orchestrator adapter seams."""

from __future__ import annotations

import pytest
from matriz.orchestration.service_async import (
    _reset_async_orchestrator_for_testing,
    get_async_orchestrator,
    run_async_matriz,
)


@pytest.fixture(autouse=True)
def reset_async_orchestrator():
    """Ensure each test gets a fresh orchestrator instance."""

    _reset_async_orchestrator_for_testing()
    yield
    _reset_async_orchestrator_for_testing()


def _extract_stage(result: dict, stage_value: str) -> dict:
    """Helper to fetch a stage dictionary by StageType value."""

    for stage in result.get("stages", []):
        stage_type = stage.get("stage_type")
        if stage_type == stage_value or getattr(stage_type, "value", None) == stage_value:
            return stage
    raise AssertionError(f"Stage '{stage_value}' not found in result")


@pytest.mark.asyncio
async def test_math_query_maps_to_expression() -> None:
    """Math input should populate expression payload before node processing."""

    orchestrator = get_async_orchestrator()
    assert orchestrator is not None

    result = await run_async_matriz("2 + 2")
    processing_stage = _extract_stage(result, "processing")
    additional = (
        processing_stage.get("data", {})
        .get("matriz_node", {})
        .get("additional_data", {})
    )

    assert additional.get("expression") == "2 + 2"
    assert "The result is" in result.get("answer", "")


@pytest.mark.asyncio
async def test_fact_query_maps_to_question() -> None:
    """Fact input should populate question payload before node processing."""

    result = await run_async_matriz("What is the capital of France?")
    processing_stage = _extract_stage(result, "processing")
    additional = (
        processing_stage.get("data", {})
        .get("matriz_node", {})
        .get("additional_data", {})
    )

    assert additional.get("question") == "What is the capital of France?"
    assert "Paris" in result.get("answer", "")
