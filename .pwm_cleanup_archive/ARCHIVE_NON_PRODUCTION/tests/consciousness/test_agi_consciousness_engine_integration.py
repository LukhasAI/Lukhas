import pytest

from consciousness.consciousness_hub import get_consciousness_hub
from consciousness.systems.engine_complete import AGIConsciousnessEngine


@pytest.mark.asyncio
async def test_agi_consciousness_engine_integration():
    """
    Tests that the AGIConsciousnessEngine is correctly integrated into the ConsciousnessHub.
    """
    # Get the consciousness hub instance
    hub = get_consciousness_hub()
    await hub.initialize()

    # Check if the agi_consciousness_engine service is registered
    engine_service = hub.get_service("agi_consciousness_engine")
    assert (
        engine_service is not None
    ), "AGIConsciousnessEngine service not found in ConsciousnessHub"

    # Check if the service is an instance of the correct class
    assert isinstance(
        engine_service, AGIConsciousnessEngine
    ), "Registered service is not an instance of AGIConsciousnessEngine"

    print("\nAGI Consciousness Engine integration test passed.")
