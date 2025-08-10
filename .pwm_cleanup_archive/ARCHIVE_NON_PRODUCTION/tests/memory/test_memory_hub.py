import pytest

from memory.memory_hub import initialize_memory_system


@pytest.mark.asyncio
async def test_neurosymbolic_layer_integration():
    """
    Tests that the NeurosymbolicIntegrationLayer is correctly integrated into the MemoryHub.
    """
    memory_hub = await initialize_memory_system()
    neurosymbolic_layer = memory_hub.get_service("neurosymbolic_layer")
    assert (
        neurosymbolic_layer is not None
    ), "Neurosymbolic layer should be registered in the memory hub"
    assert hasattr(
        neurosymbolic_layer, "process_memory_batch"
    ), "Neurosymbolic layer should have a process_memory_batch method"
