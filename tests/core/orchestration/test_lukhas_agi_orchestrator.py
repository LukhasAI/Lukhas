"""Tests for the symbolic Lukhas AGI orchestrator stub."""

import asyncio

import pytest

from core.orchestration.brain.lukhas_agi_orchestrator import (
    LukhasAGIOrchestrator,
    lukhas_agi_orchestrator,
)


@pytest.mark.asyncio
async def test_initialize_and_process_request() -> None:
    orchestrator = LukhasAGIOrchestrator()

    initialised = await orchestrator.initialize_agi_system()
    assert initialised is True

    result = await orchestrator.process_agi_request("hello", {"signals": ["s1"]})

    assert result["processing_results"]["cognitive"]["echo"] == "hello"
    assert result["processing_results"]["cognitive_capabilities"]
    assert result["system_state"]["consciousness_level"] == "stable"


@pytest.mark.asyncio
async def test_background_orchestration_lifecycle() -> None:
    await lukhas_agi_orchestrator.initialize_agi_system()
    await lukhas_agi_orchestrator.start_agi_orchestration()

    await asyncio.sleep(0)

    status = lukhas_agi_orchestrator.get_agi_status()
    assert status["active"] is True

    await lukhas_agi_orchestrator.stop_agi_orchestration()
    assert lukhas_agi_orchestrator.get_agi_status()["active"] is False
