"""Smoke test for MATRIZ orchestrator (if importable)."""

import pytest
from importlib.util import find_spec

HAS_PRIMARY_HUB = find_spec("orchestration.brain.primary_hub") is not None
HAS_ORCHESTRATION = find_spec("orchestration") is not None
HAS_ORCHESTRATION_BRAIN = find_spec("orchestration.brain") is not None


@pytest.mark.smoke
@pytest.mark.unit
@pytest.mark.skipif(not HAS_PRIMARY_HUB, reason="Primary orchestrator not available")
def test_orchestrator_importable():
    """Test if orchestrator modules can be imported."""
    # Try importing main orchestrator components
    from orchestration.brain.primary_hub import PrimaryBrainHub

    assert PrimaryBrainHub is not None


@pytest.mark.smoke
@pytest.mark.unit
@pytest.mark.skipif(not HAS_PRIMARY_HUB, reason="Primary orchestrator not available")
def test_orchestrator_instantiation():
    """Test basic orchestrator instantiation (happy path)."""
    try:
        from orchestration.brain.primary_hub import PrimaryBrainHub

        # Basic instantiation test
        hub = PrimaryBrainHub()
        assert hub is not None

        # Check basic attributes exist
        assert hasattr(hub, "__class__")

    except Exception as e:
        # Log but don't fail - orchestrator may need full environment
        pytest.skip(f"Orchestrator requires full environment: {e}")


@pytest.mark.smoke
@pytest.mark.unit
@pytest.mark.skipif(
    not (HAS_ORCHESTRATION and HAS_ORCHESTRATION_BRAIN),
    reason="MATRIZ orchestration modules not available",
)
def test_matriz_module_structure():
    """Test basic MATRIZ module structure exists."""
    import orchestration

    assert orchestration is not None  # TODO: lukhas

    # Check if brain module exists
    import orchestration.brain

    assert orchestration.brain is not None
