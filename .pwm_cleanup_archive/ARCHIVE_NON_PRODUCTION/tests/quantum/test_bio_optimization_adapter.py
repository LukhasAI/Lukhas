import pytest

from quantum.bio_optimization_adapter import (
    MockBioOrchestrator,
    QuantumBioOptimizationAdapter,
)


@pytest.mark.asyncio
async def test_basic_optimization_cycle():
    adapter = QuantumBioOptimizationAdapter(MockBioOrchestrator())
    result = await adapter.optimize_quantum_bio_system({"value": 1.0})
    assert isinstance(result, dict)
    status = adapter.get_optimization_status()
    assert status["total_optimization_cycles_completed"] >= 1
