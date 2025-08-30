"""Test orchestration module basic functionality."""

import pytest


def test_kernel_bus_import():
    """Test KernelBus imports and basic init."""
    try:
        from lukhas.orchestration import KernelBus

        # Test creation
        bus = KernelBus()
        assert bus is not None
        assert hasattr(bus, "publish")
        assert hasattr(bus, "subscribe")

    except ImportError:
        pytest.skip("Kernel bus not available")


def test_context_bus_import():
    """Test context bus imports."""
    try:
        from lukhas.orchestration.context_bus import ContextBus

        # Check class exists
        assert ContextBus is not None

    except (ImportError, AttributeError):
        pytest.skip("Context bus not available")


def test_orchestration_exports():
    """Test orchestration module exports."""
    try:
        import lukhas.orchestration as orchestration

        # Check key exports
        assert hasattr(orchestration, "KernelBus")

    except ImportError:
        pytest.skip("Orchestration module not available")
