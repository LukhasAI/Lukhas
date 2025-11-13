import sys
from unittest.mock import MagicMock, patch

import pytest

# Mock dependencies that are not available in the test environment
MOCK_MODULES = {
    "core.integration.dynamic_modality_broker": MagicMock(),
    "ethics.self_reflective_debugger": MagicMock(),
    "labs.consciousness.dream.core.dream_feedback_controller": MagicMock(),
    "ethics.meta_ethics_governor": MagicMock(),
    "memory.emotional": MagicMock(),
    "numpy": MagicMock(),
}

@patch.dict(sys.modules, MOCK_MODULES)
def test_hyperspace_dream_simulator_import():
    """
    Tests that the hyperspace_dream_simulator module can be imported without errors.
    """
    try:
        from matriz.memory.temporal import hyperspace_dream_simulator
    except Exception as e:
        pytest.fail(f"Failed to import hyperspace_dream_simulator: {e}")

    # Verify that the module has the expected classes and functions
    assert hasattr(hyperspace_dream_simulator, "HyperspaceDreamSimulator")
    assert hasattr(hyperspace_dream_simulator, "get_hds")
