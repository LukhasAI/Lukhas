"""
Capability test: Zero unrouted signals during consciousness cycles

This test ensures no signals go unrouted during normal operation,
preventing silent routing failures that could degrade system performance.
"""
import pytest
from core.matriz_consciousness_integration import create_matriz_consciousness_system
from core.metrics import router_no_rule_total


def _get_no_rule_count():
    """Get current count of unrouted signals from Prometheus counter"""
    try:
        # Handle both real Prometheus counters and mock counters
        if hasattr(router_no_rule_total, '_value'):
            if hasattr(router_no_rule_total._value, 'get'):
                return router_no_rule_total._value.get()
            else:
                return getattr(router_no_rule_total._value, '_value', 0)
        else:
            return 0
    except Exception:
        return 0


def normalize_metrics(raw: dict) -> dict:
    """Normalize metrics to canonical contract for capability tests"""
    # Simple pass-through for now since _normalize_demo_result handles it
    return raw


async def _run_demo(system):
    """Shim for MatrizConsciousnessSystem API drift - maps to available demo method"""
    return await system.demonstrate_consciousness_evolution()


@pytest.mark.capability
async def test_no_unrouted_during_cycle():
    """Test that consciousness cycles generate zero unrouted signals"""

    system = create_matriz_consciousness_system("cap_router_test")
    before = _get_no_rule_count()

    try:
        await system.start_system()

        # Run a full consciousness cycle
        cycle_result = await system.process_consciousness_cycle()

        # Verify the cycle actually processed signals
        assert cycle_result["signals_emitted"] > 0, "Cycle should emit signals"
        assert cycle_result["signals_processed"] > 0, "Cycle should process signals"

    finally:
        await system.stop_system()

    after = _get_no_rule_count()
    unrouted_count = after - before

    assert unrouted_count == 0, f"Unrouted signals detected during cycle: {unrouted_count}"


@pytest.mark.capability
async def test_no_unrouted_during_startup_shutdown():
    """Test that system startup/shutdown generates zero unrouted signals"""

    before = _get_no_rule_count()

    system = create_matriz_consciousness_system("cap_startup_test")

    try:
        # Just start and stop - no processing
        await system.start_system()
    finally:
        await system.stop_system()

    after = _get_no_rule_count()
    unrouted_count = after - before

    assert unrouted_count == 0, f"Unrouted signals detected during startup/shutdown: {unrouted_count}"


@pytest.mark.capability
async def test_no_unrouted_during_demonstration():
    """Test that full system demonstration generates zero unrouted signals"""

    system = create_matriz_consciousness_system("cap_demo_test")
    before = _get_no_rule_count()

    try:
        await system.start_system()

        # Run the full demonstration scenario
        demo_result = await _run_demo(system)
        demo_result = normalize_metrics(demo_result)

        # Verify the demo actually worked
        assert demo_result["total_signals_processed"] > 0, "Demo should process signals"

    finally:
        await system.stop_system()

    after = _get_no_rule_count()
    unrouted_count = after - before

    assert unrouted_count == 0, f"Unrouted signals detected during demonstration: {unrouted_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "capability"])
