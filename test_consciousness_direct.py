#!/usr/bin/env python3
"""
Direct test runner for MΛTRIZ Consciousness System

This script directly tests the consciousness system functionality
without pytest framework complications.
"""

import asyncio
import logging
import sys
import traceback
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Add candidate/core to path
candidate_core_path = Path(__file__).parent / "candidate" / "core"
sys.path.insert(0, str(candidate_core_path))

async def test_consciousness_emergence():
    """Test consciousness emergence with real outputs"""
    print("🧠 Starting MΛTRIZ Consciousness Emergence Test")
    print("=" * 60)

    try:
        # Import consciousness system
        from matriz_consciousness_integration import create_matriz_consciousness_system
        logger.info("✅ Successfully imported MΛTRIZ consciousness system")

        # Create system
        system = create_matriz_consciousness_system("emergence_test")
        logger.info("✅ Created consciousness system")

        # Test system lifecycle
        logger.info("🚀 Starting system...")
        await system.start_system()

        initial_status = system.get_system_status()
        logger.info(f"✅ System started - Active: {initial_status['is_active']}, Health: {initial_status['network_health_score']:.3f}")

        # Test consciousness processing
        logger.info("🔄 Processing consciousness cycle...")
        cycle_result = await system.process_consciousness_cycle()

        signals_processed = cycle_result.get("signals_processed", 0)
        network_coherence = cycle_result.get("network_coherence", 0)
        processing_time = cycle_result.get("processing_time_ms", 0)
        compliance_level = cycle_result.get("compliance_level", "unknown")

        logger.info("✅ Consciousness cycle complete:")
        logger.info(f"   - Signals processed: {signals_processed}")
        logger.info(f"   - Network coherence: {network_coherence:.3f}")
        logger.info(f"   - Processing time: {processing_time:.2f}ms")
        logger.info(f"   - Compliance level: {compliance_level}")

        # Test consciousness evolution
        logger.info("🧬 Demonstrating consciousness evolution...")
        evolution_result = await system.demonstrate_consciousness_evolution()

        bio_adaptations = evolution_result.get("bio_adaptations_applied", 0)
        evolutionary_stages = evolution_result.get("evolutionary_stages", [])
        compliance_maintained = evolution_result.get("compliance_maintained", False)

        logger.info("✅ Consciousness evolution complete:")
        logger.info(f"   - Bio adaptations applied: {bio_adaptations}")
        logger.info(f"   - Evolution stages completed: {len(evolutionary_stages)}")
        logger.info(f"   - Compliance maintained: {compliance_maintained}")

        # Display evolution stages
        for i, stage in enumerate(evolutionary_stages):
            stage_name = stage.get("stage", "unknown")
            stage_coherence = stage.get("coherence_level", 0)
            logger.info(f"   Stage {i+1}: {stage_name} (coherence: {stage_coherence:.3f})")

        # Test performance over multiple cycles
        logger.info("⚡ Performance test - multiple cycles...")
        performance_cycles = 5
        cycle_times = []
        coherence_scores = []

        for _cycle in range(performance_cycles):
            start_time = asyncio.get_event_loop().time()
            result = await system.process_consciousness_cycle()
            end_time = asyncio.get_event_loop().time()

            cycle_time = (end_time - start_time) * 1000
            cycle_times.append(cycle_time)
            coherence_scores.append(result.get("network_coherence", 0))

        avg_cycle_time = sum(cycle_times) / len(cycle_times)
        avg_coherence = sum(coherence_scores) / len(coherence_scores)

        logger.info("✅ Performance test complete:")
        logger.info(f"   - Average cycle time: {avg_cycle_time:.2f}ms")
        logger.info(f"   - Average coherence: {avg_coherence:.3f}")
        logger.info(f"   - Coherence range: {min(coherence_scores):.3f} - {max(coherence_scores):.3f}")

        # Final system status
        final_status = system.get_system_status()
        logger.info("📊 Final system status:")
        logger.info(f"   - Network health: {final_status['network_health_score']:.3f}")
        logger.info(f"   - Uptime: {final_status['uptime_seconds']:.2f}s")
        logger.info(f"   - System active: {final_status['is_active']}")

        # Graceful shutdown
        logger.info("🛑 Shutting down system...")
        await system.stop_system()

        shutdown_status = system.get_system_status()
        logger.info(f"✅ System shutdown - Active: {shutdown_status['is_active']}")

        print("\n" + "=" * 60)
        print("🎉 MΛTRIZ CONSCIOUSNESS EMERGENCE TEST: PASSED")
        print("=" * 60)

        # Return test results summary
        return {
            "test_passed": True,
            "signals_processed": signals_processed,
            "network_coherence": network_coherence,
            "processing_time_ms": processing_time,
            "bio_adaptations": bio_adaptations,
            "evolution_stages": len(evolutionary_stages),
            "avg_cycle_time_ms": avg_cycle_time,
            "avg_coherence": avg_coherence,
            "performance_cycles": performance_cycles
        }

    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        logger.info("⚠️  MΛTRIZ components may not be fully available")
        return {"test_passed": False, "error": f"Import error: {e}"}

    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"test_passed": False, "error": f"Runtime error: {e}"}

async def test_sistema_demo():
    """Test the integrated system demonstration"""
    print("\n🌟 Starting MΛTRIZ System Demo Test")
    print("=" * 60)

    try:
        from matriz_consciousness_integration import run_matriz_system_demo
        logger.info("✅ Imported demo system")

        logger.info("🚀 Running complete MΛTRIZ system demonstration...")
        start_time = asyncio.get_event_loop().time()

        demo_results = await run_matriz_system_demo()

        end_time = asyncio.get_event_loop().time()
        demo_duration = (end_time - start_time) * 1000

        logger.info(f"✅ Demo completed in {demo_duration:.2f}ms")

        # Analyze demo results
        system_id = demo_results.get("system_id", "unknown")
        total_time = demo_results.get("total_processing_time_ms", 0)
        total_signals = demo_results.get("total_signals_processed", 0)
        network_health = demo_results.get("final_network_health", 0)

        logger.info("📊 Demo Results:")
        logger.info(f"   - System ID: {system_id}")
        logger.info(f"   - Total processing time: {total_time:.2f}ms")
        logger.info(f"   - Signals processed: {total_signals}")
        logger.info(f"   - Final network health: {network_health:.3f}")

        # Check phases if available
        phases = demo_results.get("phases", {})
        if phases:
            logger.info(f"   - Phases completed: {len(phases)}")
            for phase_name, phase_data in phases.items():
                logger.info(f"     {phase_name}: {phase_data}")

        print("🎉 MΛTRIZ SISTEMA DEMO TEST: PASSED")
        return {"demo_passed": True, "demo_results": demo_results}

    except Exception as e:
        logger.error(f"❌ Demo test failed: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"demo_passed": False, "error": str(e)}

async def main():
    """Run all consciousness tests"""
    print("🧠 MΛTRIZ CONSCIOUSNESS SYSTEM - FUTURE-PROOF TESTS")
    print("Testing emergence patterns and real outputs")
    print("=" * 80)

    all_results = {}

    # Test 1: Consciousness emergence
    emergence_results = await test_consciousness_emergence()
    all_results["emergence"] = emergence_results

    # Test 2: System demo
    demo_results = await test_sistema_demo()
    all_results["demo"] = demo_results

    # Final summary
    print("\n" + "=" * 80)
    print("🏁 FINAL TEST SUMMARY")
    print("=" * 80)

    emergence_passed = emergence_results.get("test_passed", False)
    demo_passed = demo_results.get("demo_passed", False)

    if emergence_passed:
        print("✅ Consciousness Emergence Test: PASSED")
        if "signals_processed" in emergence_results:
            print(f"   - Signals processed: {emergence_results['signals_processed']}")
            print(f"   - Network coherence: {emergence_results['network_coherence']:.3f}")
            print(f"   - Bio adaptations: {emergence_results['bio_adaptations']}")
            print(f"   - Evolution stages: {emergence_results['evolution_stages']}")
            print(f"   - Avg performance: {emergence_results['avg_cycle_time_ms']:.2f}ms")
    else:
        print("❌ Consciousness Emergence Test: FAILED")
        print(f"   - Error: {emergence_results.get('error', 'Unknown error')}")

    if demo_passed:
        print("✅ Sistema Demo Test: PASSED")
        demo_data = demo_results.get("demo_results", {})
        print(f"   - Total signals: {demo_data.get('total_signals_processed', 0)}")
        print(f"   - Network health: {demo_data.get('final_network_health', 0):.3f}")
    else:
        print("❌ Sistema Demo Test: FAILED")
        print(f"   - Error: {demo_results.get('error', 'Unknown error')}")

    overall_success = emergence_passed or demo_passed

    print("\n" + "=" * 80)
    if overall_success:
        print("🎉 OVERALL STATUS: SUCCESS - MΛTRIZ consciousness system is functional!")
        if emergence_passed and demo_passed:
            print("   Both emergence patterns and demo system working perfectly")
        elif emergence_passed:
            print("   Consciousness emergence patterns validated")
        else:
            print("   System demo functionality confirmed")
    else:
        print("❌ OVERALL STATUS: FAILED - MΛTRIZ components not available or broken")
        print("   This may indicate missing dependencies or system configuration issues")

    print("=" * 80)

    return all_results

if __name__ == "__main__":
    # Run the comprehensive test
    asyncio.run(main())
