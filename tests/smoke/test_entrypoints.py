"""
Entrypoints Smoke Test - Quick connector sanity checks
======================================================

Quick validation that canonical public APIs import correctly and have expected types.
Perfect for CI gates and connector health checks.
"""
import pytest


@pytest.mark.smoke
def test_core_api_imports():
    """Test that core LUKHAS APIs can be imported and have expected signatures."""
    try:
        from core import (
            TRINITY_SYMBOLS,
            CoreWrapper,
            GLYPHSymbol,
            GLYPHToken,
            create_glyph,
        )

        # Verify trinity symbols exist
        assert isinstance(TRINITY_SYMBOLS, dict)
        assert "identity" in TRINITY_SYMBOLS
        assert "consciousness" in TRINITY_SYMBOLS
        assert "guardian" in TRINITY_SYMBOLS

        # Verify GLYPH types exist
        assert GLYPHSymbol is not None
        assert GLYPHToken is not None
        assert callable(create_glyph)
        assert CoreWrapper is not None

    except ImportError as e:
        pytest.fail(f"Core API import failed: {e}")


@pytest.mark.smoke
def test_matriz_api_imports():
    """Test that MATRIZ trace analysis APIs are available."""
    # Test that we can import MATRIZ modules
    try:
        # Import matriz package (lowercase alias works in tests)
        import matriz  # type: ignore
        assert matriz is not None

        # Verify we can import the traces router (main API)
        from matriz.traces_router import router as traces_router
        assert traces_router is not None
        assert hasattr(traces_router, "routes")

    except ImportError as e:
        pytest.fail(f"MATRIZ API import failed: {e}")


@pytest.mark.smoke
def test_identity_api_imports():
    """Test that identity/auth APIs can be imported."""
    try:
        # Check if identity modules exist
        import importlib

        # Try lukhas identity first
        try:
            identity_spec = importlib.util.find_spec("lukhas.identity")
            if identity_spec is not None:
                from lukhas import identity
                assert identity is not None
        except ImportError:
            pass

        # Check candidate identity modules
        candidate_identity_spec = importlib.util.find_spec("candidate.governance.identity")
        if candidate_identity_spec is not None:
            # Just verify it can be imported
            import governance.identity

    except ImportError as e:
        pytest.fail(f"Identity API import failed: {e}")


@pytest.mark.smoke
def test_guardian_api_imports():
    """Test that Guardian/ethics APIs are available."""
    try:
        # Check for guardian systems
        import importlib

        # Look for candidate ethics modules
        ethics_spec = importlib.util.find_spec("candidate.core.ethics")
        if ethics_spec is not None:
            # Just verify it can be imported without error
            import core.ethics

        # Look for governance modules
        governance_spec = importlib.util.find_spec("candidate.core.governance")
        if governance_spec is not None:
            import core.governance

    except ImportError as e:
        pytest.fail(f"Guardian API import failed: {e}")


@pytest.mark.smoke
def test_memory_api_imports():
    """Test that memory system APIs are accessible."""
    try:
        import importlib

        # Check for memory modules
        memory_spec = importlib.util.find_spec("candidate.memory")
        if memory_spec is not None:
            # Verify basic import
            import memory

        # Check for lukhas memory if it exists
        lukhas_memory_spec = importlib.util.find_spec("lukhas.memory")
        if lukhas_memory_spec is not None:
            import memory

    except ImportError as e:
        pytest.fail(f"Memory API import failed: {e}")


@pytest.mark.smoke
def test_basic_types_and_constants():
    """Test basic types and constants are well-formed."""
    # Test that basic Python imports work
    import datetime
    import json
    import uuid

    # Verify we can create basic data structures
    test_data = {
        "timestamp": datetime.datetime.now().isoformat(),
        "id": str(uuid.uuid4()),
        "status": "healthy"
    }

    # Verify JSON serialization works
    serialized = json.dumps(test_data)
    deserialized = json.loads(serialized)

    assert deserialized["status"] == "healthy"
    assert "timestamp" in deserialized
    assert "id" in deserialized


@pytest.mark.smoke
def test_environment_health():
    """Test that test environment is properly configured."""
    import os
    import sys

    # Verify Python version is compatible
    assert sys.version_info >= (3, 9), f"Python {sys.version_info} < required 3.9+"

    # Verify PYTHONPATH includes repo root
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    assert repo_root in sys.path, "Repo root not in PYTHONPATH"

    # Verify test environment variables
    assert os.environ.get("PYTHONHASHSEED") == "0", "PYTHONHASHSEED not set for determinism"


if __name__ == "__main__":
    # Allow running this test file directly
    pytest.main([__file__, "-v"])
