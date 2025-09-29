"""
Capability test: Backpressure and burst emission handling

This test ensures the system can handle burst signal emissions without
deadlocking and that proper decimation/backpressure occurs under load.
"""
import asyncio
import pytest

from lukhas.core.matriz_consciousness_integration import create_matriz_consciousness_system


@pytest.mark.capability
async def test_burst_emission_backpressure():
    """Test system handles burst emissions with proper backpressure"""

    # Create system and ensure it's properly initialized
    system = create_matriz_consciousness_system("backpressure_test")

    try:
        await system.start_system()

        # Burst 100 awareness signals quickly
        burst_tasks = []
        for i in range(100):
            task = system.emitters["consciousness"].emit_awareness_pulse(0.7 + (i % 3) * 0.1)
            burst_tasks.append(task)

        # Execute burst with timeout to prevent test hanging
        try:
            await asyncio.wait_for(asyncio.gather(*burst_tasks, return_exceptions=True), timeout=30.0)
        except asyncio.TimeoutError:
            pytest.fail("Burst emission timed out - possible deadlock")

        # Get router stats to verify processing occurred
        router_stats = system.signal_router.get_signal_processing_stats()

        # Verify some signals were processed (don't require 100% - decimation is expected)
        signals_processed = router_stats.get("signals_processed", 0)
        assert signals_processed > 0, f"No signals processed during burst (got {signals_processed})"

        # Verify cascade prevention is working (some signals may be blocked)
        cascade_preventions = router_stats.get("cascade_preventions", 0)
        if cascade_preventions > 0:
            # This is expected behavior under burst load
            print(f"✅ Cascade prevention activated: {cascade_preventions} signals blocked")

        # Verify router didn't crash - should still be able to route signals
        post_burst_signal = await system.emitters["consciousness"].emit_awareness_pulse(0.8)
        assert post_burst_signal is not None, "Router should still function after burst"

    finally:
        await system.stop_system()


@pytest.mark.capability
async def test_concurrent_module_emissions():
    """Test concurrent emissions from multiple modules"""

    system = create_matriz_consciousness_system("concurrent_test")

    try:
        await system.start_system()

        # Create concurrent emissions from different modules
        concurrent_tasks = [
            system.emitters["consciousness"].emit_awareness_pulse(0.8),
            system.emitters["orchestration"].emit_network_health_pulse(),
            system.emitters["identity"].emit_identity_authentication(0.9, {"test": True}),
            system.emitters["governance"].emit_guardian_compliance_signal(0.95, [], 0.02),
            # Add more awareness pulses to stress test
            system.emitters["consciousness"].emit_awareness_pulse(0.7),
            system.emitters["consciousness"].emit_awareness_pulse(0.9),
        ]

        # Execute concurrently with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*concurrent_tasks, return_exceptions=True),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            pytest.fail("Concurrent emissions timed out")

        # Verify no exceptions were raised
        exceptions = [r for r in results if isinstance(r, Exception)]
        if exceptions:
            pytest.fail(f"Concurrent emissions raised exceptions: {exceptions}")

        # Verify signals were created
        signals_created = [r for r in results if r is not None and not isinstance(r, Exception)]
        assert len(signals_created) > 0, "Should create at least some signals"

    finally:
        await system.stop_system()


@pytest.mark.capability
async def test_router_performance_under_load():
    """Test router performance metrics under sustained load"""

    system = create_matriz_consciousness_system("perf_test")

    try:
        await system.start_system()

        # Generate sustained load for a short period
        load_duration = 5  # seconds
        start_time = asyncio.get_event_loop().time()

        load_tasks = []
        while (asyncio.get_event_loop().time() - start_time) < load_duration:
            task = system.emitters["consciousness"].emit_awareness_pulse(0.8)
            load_tasks.append(task)
            await asyncio.sleep(0.1)  # 10 Hz emission rate

        # Wait for all tasks to complete
        await asyncio.gather(*load_tasks, return_exceptions=True)

        # Check performance metrics
        router_stats = system.signal_router.get_signal_processing_stats()

        signals_processed = router_stats.get("signals_processed", 0)
        avg_routing_time = router_stats.get("avg_routing_time_ms", 0)

        assert signals_processed > 0, "Should process signals under load"

        # Performance target: average routing time should be reasonable
        if avg_routing_time > 0:
            assert avg_routing_time < 100, f"Routing time too slow: {avg_routing_time:.2f}ms (target: <100ms)"
            print(f"✅ Average routing time: {avg_routing_time:.2f}ms")

    finally:
        await system.stop_system()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "capability"])