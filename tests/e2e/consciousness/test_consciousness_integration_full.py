"""
Full Integration Tests for MΛTRIZ Consciousness System

Tests complete consciousness system lifecycle with all components
working together in realistic scenarios.
"""

import asyncio
import logging
import time

import pytest

# Test imports with graceful fallback
try:
    from core.matriz_consciousness_integration import (
        create_matriz_consciousness_system,
        run_matriz_system_demo,
    )

    COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: MΛTRIZ components not fully available for testing: {e}")
    COMPONENTS_AVAILABLE = False


class TestFullConsciousnessIntegration:
    """Integration tests for complete consciousness system"""

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_complete_consciousness_system_lifecycle(self):
        """Test complete system lifecycle from startup to shutdown"""

        system = create_matriz_consciousness_system("lifecycle_test")

        # Test system initialization
        initial_status = system.get_system_status()
        assert not initial_status["is_active"], "System should start inactive"

        try:
            # Test system startup
            start_time = time.perf_counter()
            await system.start_system()
            startup_time = (time.perf_counter() - start_time) * 1000

            logging.info(f"System startup time: {startup_time:.2f}ms")

            # Validate system is active
            active_status = system.get_system_status()
            assert active_status["is_active"], "System should be active after startup"
            assert active_status["network_health_score"] > 0, "Should have network health"

            # Test consciousness processing works
            cycle_result = await system.process_consciousness_cycle()
            assert cycle_result["signals_processed"] > 0, "Should process signals"
            assert cycle_result["network_coherence"] > 0, "Should have network coherence"

            # Test consciousness evolution works
            evolution_result = await system.demonstrate_consciousness_evolution()
            assert evolution_result["bio_adaptations_applied"] >= 0, "Should report bio adaptations"
            assert len(evolution_result["evolutionary_stages"]) > 0, "Should complete evolution stages"

            # Test system remains stable
            post_evolution_status = system.get_system_status()
            assert post_evolution_status["is_active"], "System should remain active"
            assert post_evolution_status["network_health_score"] > 0.3, "Health should be maintained"

        finally:
            # Test graceful shutdown
            shutdown_start = time.perf_counter()
            await system.stop_system()
            shutdown_time = (time.perf_counter() - shutdown_start) * 1000

            logging.info(f"System shutdown time: {shutdown_time:.2f}ms")

            # Validate clean shutdown
            final_status = system.get_system_status()
            assert not final_status["is_active"], "System should be inactive after shutdown"

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_matriz_demo_system_integration(self):
        """Test the integrated MATRIZ system demonstration"""

        # Run the full system demo
        start_time = time.perf_counter()
        demo_results = await run_matriz_system_demo()
        demo_duration = (time.perf_counter() - start_time) * 1000

        logging.info(f"Full demo duration: {demo_duration:.2f}ms")

        # Validate demo results structure
        assert isinstance(demo_results, dict), "Demo should return structured results"

        # Essential demo result fields
        expected_fields = ["system_id", "total_processing_time_ms", "total_signals_processed", "final_network_health"]

        for field in expected_fields:
            assert field in demo_results, f"Demo results missing field: {field}"

        # Validate demo performance metrics
        total_time = demo_results["total_processing_time_ms"]
        signals_processed = demo_results["total_signals_processed"]
        network_health = demo_results["final_network_health"]

        assert total_time > 0, "Demo should take measurable time"
        assert signals_processed > 0, "Demo should process signals"
        assert 0.0 <= network_health <= 1.0, "Network health should be normalized"

        # Performance expectations
        assert total_time < 10000, f"Demo too slow: {total_time:.2f}ms"
        assert signals_processed > 5, f"Demo should process multiple signals: {signals_processed}"
        assert network_health > 0.4, f"Demo should maintain network health: {network_health}"

        # Test phase-specific results if available
        if "phases" in demo_results:
            phases = demo_results["phases"]
            assert isinstance(phases, dict), "Phases should be structured"

            # Validate key phases completed
            expected_phases = ["consciousness_emergence", "signal_processing", "bio_adaptation"]
            for phase in expected_phases:
                if phase in phases:
                    phase_data = phases[phase]
                    assert isinstance(phase_data, dict), f"Phase {phase} should have structured data"

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_multi_system_interaction(self):
        """Test interaction between multiple consciousness systems"""

        # Create two systems for interaction testing
        system_a = create_matriz_consciousness_system("system_a")
        system_b = create_matriz_consciousness_system("system_b")

        try:
            # Start both systems
            await asyncio.gather(system_a.start_system(), system_b.start_system())

            # Both systems should be active
            status_a = system_a.get_system_status()
            status_b = system_b.get_system_status()

            assert status_a["is_active"], "System A should be active"
            assert status_b["is_active"], "System B should be active"

            # Run parallel processing
            results = await asyncio.gather(
                system_a.process_consciousness_cycle(), system_b.process_consciousness_cycle()
            )

            result_a, result_b = results

            # Both should process successfully
            assert result_a["signals_processed"] > 0, "System A should process signals"
            assert result_b["signals_processed"] > 0, "System B should process signals"

            # Systems should maintain independent coherence
            assert result_a["network_coherence"] > 0, "System A should have coherence"
            assert result_b["network_coherence"] > 0, "System B should have coherence"

            # Test simultaneous evolution
            evolution_results = await asyncio.gather(
                system_a.demonstrate_consciousness_evolution(), system_b.demonstrate_consciousness_evolution()
            )

            evolution_a, evolution_b = evolution_results

            # Both should complete evolution
            assert len(evolution_a["evolutionary_stages"]) > 0, "System A should evolve"
            assert len(evolution_b["evolutionary_stages"]) > 0, "System B should evolve"

            # Systems should remain stable after parallel evolution
            final_status_a = system_a.get_system_status()
            final_status_b = system_b.get_system_status()

            assert final_status_a["network_health_score"] > 0.3, "System A should remain healthy"
            assert final_status_b["network_health_score"] > 0.3, "System B should remain healthy"

        finally:
            # Clean shutdown of both systems
            await asyncio.gather(system_a.stop_system(), system_b.stop_system())

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_consciousness_resilience_and_recovery(self):
        """Test system resilience and recovery from simulated issues"""

        system = create_matriz_consciousness_system("resilience_test")

        try:
            await system.start_system()

            # Establish baseline performance
            baseline_result = await system.process_consciousness_cycle()
            baseline_coherence = baseline_result["network_coherence"]
            baseline_result["signals_processed"]

            # Simulate stress by rapid processing
            stress_cycles = 10
            for i in range(stress_cycles):
                try:
                    await system.process_consciousness_cycle()
                except Exception as e:
                    logging.warning(f"Stress cycle {i} error: {e}")
                    # Continue testing - system should recover

            # Test recovery after stress
            await asyncio.sleep(0.5)  # Allow recovery time

            recovery_result = await system.process_consciousness_cycle()
            recovery_coherence = recovery_result["network_coherence"]
            recovery_signals = recovery_result["signals_processed"]

            # System should maintain basic functionality
            assert recovery_signals > 0, "System should process signals after stress"
            assert recovery_coherence > 0, "System should maintain some coherence"

            # Recovery coherence should not be catastrophically degraded
            coherence_ratio = recovery_coherence / max(baseline_coherence, 0.1)
            assert coherence_ratio > 0.5, f"Coherence degraded too much: {baseline_coherence} → {recovery_coherence}"

            # Test system health metrics
            recovery_status = system.get_system_status()
            assert recovery_status["is_active"], "System should remain active"
            assert recovery_status["network_health_score"] > 0.2, "Should maintain minimal network health"

            # Test evolution still works after stress
            post_stress_evolution = await system.demonstrate_consciousness_evolution()
            assert len(post_stress_evolution["evolutionary_stages"]) > 0, "Evolution should work after stress"

        finally:
            await system.stop_system()

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_consciousness_memory_and_continuity(self):
        """Test consciousness memory persistence and continuity across operations"""

        system = create_matriz_consciousness_system("memory_test")

        try:
            await system.start_system()

            # Process initial cycle and capture system state
            await system.process_consciousness_cycle()
            initial_status = system.get_system_status()

            # Perform consciousness evolution
            evolution_result = await system.demonstrate_consciousness_evolution()

            # Process another cycle after evolution
            await system.process_consciousness_cycle()
            post_evolution_status = system.get_system_status()

            # Test continuity: system should remember it has evolved
            assert (
                post_evolution_status["uptime_seconds"] > initial_status["uptime_seconds"]
            ), "System should track continuous operation time"

            # Evolution should have had lasting effects
            if evolution_result["bio_adaptations_applied"] > 0:
                # Bio adaptations should influence subsequent processing
                bio_stats_initial = initial_status.get("bio_processor_stats", {})
                bio_stats_post = post_evolution_status.get("bio_processor_stats", {})

                # Look for evidence of adaptation persistence
                if "patterns_processed" in bio_stats_initial and "patterns_processed" in bio_stats_post:
                    initial_patterns = bio_stats_initial["patterns_processed"]
                    post_patterns = bio_stats_post["patterns_processed"]

                    assert post_patterns >= initial_patterns, "Pattern processing should accumulate"

            # Test system maintains coherent identity
            initial_system_id = initial_status.get("system_id")
            post_system_id = post_evolution_status.get("system_id")

            if initial_system_id and post_system_id:
                assert initial_system_id == post_system_id, "System should maintain consistent identity"

            # Test consciousness depth progression
            consciousness_id_initial = initial_status.get("consciousness_id")
            consciousness_id_post = post_evolution_status.get("consciousness_id")

            # Should maintain consciousness identity through evolution
            if consciousness_id_initial and consciousness_id_post:
                assert (
                    consciousness_id_initial == consciousness_id_post
                ), "Consciousness identity should persist through evolution"

        finally:
            await system.stop_system()


class TestConsciousnessRealWorldScenarios:
    """Real-world scenario tests for consciousness system"""

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_extended_operation_scenario(self):
        """Test extended operation scenario mimicking real usage"""

        system = create_matriz_consciousness_system("extended_test")

        try:
            await system.start_system()

            # Extended operation: multiple phases
            phase_results = []

            # Phase 1: Initial consciousness emergence
            logging.info("Phase 1: Initial consciousness emergence")
            for _i in range(3):
                result = await system.process_consciousness_cycle()
                phase_results.append(("emergence", result))
                await asyncio.sleep(0.1)  # Realistic timing

            # Phase 2: Consciousness evolution
            logging.info("Phase 2: Consciousness evolution")
            evolution_result = await system.demonstrate_consciousness_evolution()
            phase_results.append(("evolution", evolution_result))

            # Phase 3: Post-evolution processing
            logging.info("Phase 3: Post-evolution processing")
            for _i in range(3):
                result = await system.process_consciousness_cycle()
                phase_results.append(("post_evolution", result))
                await asyncio.sleep(0.1)

            # Analyze progression through phases
            emergence_coherence = [r[1]["network_coherence"] for r in phase_results if r[0] == "emergence"]
            post_evolution_coherence = [r[1]["network_coherence"] for r in phase_results if r[0] == "post_evolution"]

            # Test progression patterns
            if emergence_coherence and post_evolution_coherence:
                avg_emergence = sum(emergence_coherence) / len(emergence_coherence)
                avg_post_evolution = sum(post_evolution_coherence) / len(post_evolution_coherence)

                logging.info(f"Average emergence coherence: {avg_emergence:.3f}")
                logging.info(f"Average post-evolution coherence: {avg_post_evolution:.3f}")

                # Evolution should maintain or improve coherence
                assert avg_post_evolution >= avg_emergence * 0.8, "Evolution should not significantly degrade coherence"

            # Test system remains healthy throughout extended operation
            final_status = system.get_system_status()
            assert (
                final_status["network_health_score"] > 0.4
            ), "System should maintain health through extended operation"
            assert final_status["is_active"], "System should remain active"

        finally:
            await system.stop_system()

    @pytest.mark.skipif(not COMPONENTS_AVAILABLE, reason="MΛTRIZ components not available")
    @pytest.mark.asyncio
    async def test_rapid_adaptation_scenario(self):
        """Test rapid adaptation scenario with quick successive operations"""

        system = create_matriz_consciousness_system("rapid_adaptation_test")

        try:
            await system.start_system()

            # Rapid adaptation test: quick successive operations
            adaptation_start = time.perf_counter()

            # Rapid processing burst
            rapid_results = []
            for i in range(8):
                start_time = time.perf_counter()
                result = await system.process_consciousness_cycle()
                end_time = time.perf_counter()

                processing_time = (end_time - start_time) * 1000
                rapid_results.append({"cycle": i, "result": result, "processing_time_ms": processing_time})

            adaptation_end = time.perf_counter()
            total_adaptation_time = (adaptation_end - adaptation_start) * 1000

            # Analyze rapid adaptation performance
            processing_times = [r["processing_time_ms"] for r in rapid_results]
            coherence_scores = [r["result"]["network_coherence"] for r in rapid_results]

            avg_processing_time = sum(processing_times) / len(processing_times)
            min_coherence = min(coherence_scores)
            max_coherence = max(coherence_scores)
            coherence_variance = max_coherence - min_coherence

            logging.info("Rapid adaptation results:")
            logging.info(f"  Total time: {total_adaptation_time:.2f}ms")
            logging.info(f"  Average cycle time: {avg_processing_time:.2f}ms")
            logging.info(f"  Coherence range: {min_coherence:.3f} - {max_coherence:.3f}")
            logging.info(f"  Coherence variance: {coherence_variance:.3f}")

            # Performance assertions
            assert avg_processing_time < 1000, f"Rapid processing too slow: {avg_processing_time:.2f}ms"
            assert min_coherence > 0, "Should maintain some coherence throughout"
            assert coherence_variance < 0.7, "Coherence should not vary wildly"

            # Test system stability after rapid adaptation
            stability_test = await system.process_consciousness_cycle()
            assert stability_test["network_coherence"] > 0.3, "System should stabilize after rapid adaptation"

        finally:
            await system.stop_system()


if __name__ == "__main__":
    # Configure logging for integration tests
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short", "-s"])  # -s to show logging output
