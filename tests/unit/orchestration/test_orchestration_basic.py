"""Test orchestration module basic functionality."""

from importlib.util import find_spec

import pytest

HAS_KERNEL_BUS = find_spec("orchestration.KernelBus") is not None
HAS_CONTEXT_BUS = find_spec("labs.orchestration.context_bus") is not None
HAS_ORCHESTRATION = find_spec("orchestration") is not None


@pytest.mark.skipif(not HAS_KERNEL_BUS, reason="Kernel bus not available")
def test_kernel_bus_import():
    """Test KernelBus imports and basic init."""
    from orchestration import KernelBus

    # Test creation
    bus = KernelBus()
    assert bus is not None
    assert hasattr(bus, "emit")
    assert hasattr(bus, "subscribe")


@pytest.mark.skipif(not HAS_CONTEXT_BUS, reason="Context bus not available")
def test_context_bus_import():
    """Test context bus imports."""
    from labs.orchestration.context_bus import ContextBus

    # Check class exists
    assert ContextBus is not None


@pytest.mark.skipif(not HAS_ORCHESTRATION, reason="Orchestration module not available")
def test_orchestration_exports():
    """Test orchestration module exports."""
    import orchestration as orchestration

    # Check key exports
    assert hasattr(orchestration, "KernelBus")
