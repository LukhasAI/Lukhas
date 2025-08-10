#!/usr/bin/env python3
"""
Run Identity System Integration Tests

This script runs all integration tests and generates a comprehensive report.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Import test module
from identity.tests.test_identity_integration import TestIdentityIntegration


async def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("LUKHAS IDENTITY SYSTEM INTEGRATION TESTS")
    print("=" * 60)
    print(f"Start Time: {datetime.utcnow().isoformat()}")
    print("=" * 60 + "\n")

    # Create test instance
    test_suite = TestIdentityIntegration()

    # Setup components
    print("Setting up test components...")
    components = None

    try:
        # Manual setup since we're not using pytest fixtures
        from identity.core.colonies import (
            BiometricVerificationColony,
            ConsciousnessVerificationColony,
            DreamVerificationColony,
        )
        from identity.core.events import get_identity_event_publisher
        from identity.core.glyph import DistributedGLYPHColony
        from identity.core.health import IdentityHealthMonitor
        from identity.core.swarm import TierAwareSwarmHub
        from identity.core.tagging import IdentityTagResolver

        # Initialize components
        event_publisher = await get_identity_event_publisher()

        biometric_colony = BiometricVerificationColony("test_biometric_colony")
        await biometric_colony.initialize()

        consciousness_colony = ConsciousnessVerificationColony(
            "test_consciousness_colony"
        )
        await consciousness_colony.initialize()

        dream_colony = DreamVerificationColony("test_dream_colony")
        await dream_colony.initialize()

        swarm_hub = TierAwareSwarmHub("test_swarm_hub")
        await swarm_hub.initialize()

        tag_resolver = IdentityTagResolver("test_tag_resolver")
        await tag_resolver.initialize()

        health_monitor = IdentityHealthMonitor("test_health_monitor")
        await health_monitor.initialize()

        glyph_colony = DistributedGLYPHColony("test_glyph_colony")
        await glyph_colony.initialize()

        # Register components with health monitor
        await health_monitor.register_component(
            "test_biometric_colony", ComponentType.COLONY, tier_level=0
        )

        components = {
            "event_publisher": event_publisher,
            "biometric_colony": biometric_colony,
            "consciousness_colony": consciousness_colony,
            "dream_colony": dream_colony,
            "swarm_hub": swarm_hub,
            "tag_resolver": tag_resolver,
            "health_monitor": health_monitor,
            "glyph_colony": glyph_colony,
        }

        print("✓ Components initialized successfully\n")

        # Run tests
        test_results = {}

        tests = [
            ("Biometric Verification", test_suite.test_biometric_verification_real),
            (
                "Consciousness Verification",
                test_suite.test_consciousness_verification_real,
            ),
            ("Dream Verification", test_suite.test_dream_verification_tier5),
            ("Swarm Hub Orchestration", test_suite.test_swarm_hub_orchestration),
            ("Trust Network & Tagging", test_suite.test_trust_network_and_tagging),
            ("Health Monitoring", test_suite.test_health_monitoring_and_healing),
            ("GLYPH Generation", test_suite.test_distributed_glyph_generation),
            ("Colony Connectivity", test_suite.test_colony_connectivity_and_state),
        ]

        for test_name, test_func in tests:
            print(f"\n{'='*40}")
            print(f"Running: {test_name}")
            print("=" * 40)

            try:
                # Create a mock fixture that returns components
                class MockFixture:
                    async def __aenter__(self):
                        return components

                    async def __aexit__(self, *args):
                        pass

                # Run test
                await test_func(MockFixture())
                test_results[test_name] = "PASSED"
                print(f"✓ {test_name} - PASSED")

            except Exception as e:
                test_results[test_name] = f"FAILED: {str(e)}"
                print(f"✗ {test_name} - FAILED: {e}")
                import traceback

                traceback.print_exc()

        # Generate summary report
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        passed = sum(1 for r in test_results.values() if r == "PASSED")
        failed = len(test_results) - passed

        print(f"Total Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")

        print("\nDetailed Results:")
        for test, result in test_results.items():
            status = "✓" if result == "PASSED" else "✗"
            print(f"  {status} {test}: {result}")

        # Save summary
        summary = {
            "test_run": datetime.utcnow().isoformat(),
            "total_tests": len(test_results),
            "passed": passed,
            "failed": failed,
            "success_rate": passed / len(test_results),
            "results": test_results,
        }

        os.makedirs("identity/tests/results", exist_ok=True)
        with open("identity/tests/results/test_summary_latest.json", "w") as f:
            json.dump(summary, f, indent=2)

        print("\nTest results saved to: identity/tests/results/")

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"End Time: {datetime.utcnow().isoformat()}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Import ComponentType for health monitor
    from identity.core.health import ComponentType

    # Run tests
    asyncio.run(run_all_tests())
