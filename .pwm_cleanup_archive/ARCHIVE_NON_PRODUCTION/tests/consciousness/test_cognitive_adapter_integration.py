import pytest

from consciousness.cognitive.adapter import CognitiveAdapter
from consciousness.consciousness_hub import get_consciousness_hub


@pytest.mark.asyncio
async def test_cognitive_adapter_integration():
    """
    Tests that the CognitiveAdapter is correctly integrated into the ConsciousnessHub.
    """
    # Get the consciousness hub instance
    hub = get_consciousness_hub()
    await hub.initialize()

    # Check if the cognitive_adapter service is registered
    adapter_service = hub.get_service("cognitive_adapter")
    assert (
        adapter_service is not None
    ), "CognitiveAdapter service not found in ConsciousnessHub"

    # Check if the service is an instance of the correct class
    assert isinstance(
        adapter_service, CognitiveAdapter
    ), "Registered service is not an instance of CognitiveAdapter"

    # Check if it's also registered as a cognitive component
    assert (
        "cognitive_adapter" in hub.cognitive_components
    ), "CognitiveAdapter not in cognitive_components registry"
    assert (
        hub.cognitive_components["cognitive_adapter"] is adapter_service
    ), "Mismatch between service and cognitive component"

    print("\nCognitive Adapter integration test passed.")
