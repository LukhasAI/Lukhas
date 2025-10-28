import pytest

from core.orchestration.brain.lukhas_agi_orchestrator import (
    LukhasAGIOrchestrator,
    get_agi_status,
    initialize_agi_system,
    lukhas_agi_orchestrator,
)


@pytest.mark.asyncio
async def test_initialize_and_process_updates_metrics():
    orchestrator = LukhasAGIOrchestrator()
    await orchestrator.initialize_agi_system(start_background=False)

    result = await orchestrator.process_agi_request("hello world", {"history": [1, 2, 3]})

    assert result["status"] == "ok"
    status = orchestrator.get_agi_status()
    assert status["requests_processed"] == 1
    assert status["drift_score"] > 0.0
    assert status["affect_delta"] > 0.0


@pytest.mark.asyncio
async def test_module_level_helpers_share_state():
    await initialize_agi_system(start_monitoring=False)

    module_status = get_agi_status()
    assert module_status["initialised"] is True

    await lukhas_agi_orchestrator.process_agi_request("ping", {})
    shared_status = get_agi_status()
    assert shared_status["requests_processed"] >= 1

    await lukhas_agi_orchestrator.stop_agi_orchestration()
