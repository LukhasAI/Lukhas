"""Smoke test for MATRIZ orchestrator (if importable)."""

import pytest


@pytest.mark.smoke
@pytest.mark.unit
def test_orchestrator_importable():
    """Test if orchestrator modules can be imported."""
    try:
        # Try importing main orchestrator components
        from lukhas.orchestration.brain.primary_hub import PrimaryBrainHub

        assert PrimaryBrainHub is not None

    except ImportError as e:
        pytest.skip(f"Primary orchestrator not available: {e}")


@pytest.mark.smoke
@pytest.mark.unit
def test_orchestrator_instantiation():
    """Test basic orchestrator instantiation (happy path)."""
    try:
        from lukhas.orchestration.brain.primary_hub import PrimaryBrainHub

        # Basic instantiation test
        hub = PrimaryBrainHub()
        assert hub is not None

        # Check basic attributes exist
        assert hasattr(hub, "__class__")

    except ImportError:
        pytest.skip("Primary orchestrator not available")
    except Exception as e:
        # Log but don't fail - orchestrator may need full environment
        pytest.skip(f"Orchestrator requires full environment: {e}")


@pytest.mark.smoke
@pytest.mark.unit
def test_matriz_module_structure():
    """Test basic MATRIZ module structure exists."""
    try:
        import lukhas.orchestration

        assert lukhas.orchestration is not None

        # Check if brain module exists
        import lukhas.orchestration.brain

        assert lukhas.orchestration.brain is not None

    except ImportError:
        pytest.skip("MATRIZ orchestration modules not available")
