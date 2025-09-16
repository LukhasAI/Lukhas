import pytest

from candidate.qi.bio.bio_coordinator import QIBioCoordinator

pytestmark = pytest.mark.asyncio


async def test_qi_bio_coordinator_smoke_runs_with_fallbacks():
    coord = QIBioCoordinator()
    # Provide minimal input compatible with _prepare_quantum_signal
    input_data = {"signal": [0.1, 0.2, 0.3]}
    result = await coord.process_bio_quantum(input_data, context={})
    assert isinstance(result, dict)
    assert "result" in result and "metadata" in result
