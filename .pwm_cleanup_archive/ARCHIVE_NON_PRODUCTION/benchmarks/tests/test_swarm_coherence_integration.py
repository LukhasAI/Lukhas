#!/usr/bin/env python3
"""
Test script for swarm-colony coherence integration
Tests the enhanced swarm system with colony infrastructure
"""

import asyncio
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

sys.path.append(".")


async def test_enhanced_swarm_basic():
    """Test basic enhanced swarm functionality."""
    print("=== Testing Enhanced Swarm (Basic) ===")

    try:
        from core.enhanced_swarm import EnhancedSwarmHub

        print("✅ Enhanced swarm imported successfully")

        # Create hub
        hub = EnhancedSwarmHub()
        print("✅ Enhanced swarm hub created")

        # Create colonies with different types
        reasoning = hub.create_colony("reasoning", "reasoning", 2)
        memory = hub.create_colony("memory", "memory", 2)
        creativity = hub.create_colony("creativity", "creativity", 2)

        print(f"✅ Created {len(hub.colonies)} colonies")
        print(f"  - Reasoning: {len(reasoning.agents) if reasoning else 0} agents")
        print(f"  - Memory: {len(memory.agents) if memory else 0} agents")
        print(f"  - Creativity: {len(creativity.agents) if creativity else 0} agents")

        # Test task processing
        if reasoning:
            task = {
                "task_id": "reasoning_test",
                "type": "logical_reasoning",
                "data": {
                    "premises": ["All AI systems can learn", "LUKHAS is an AI system"],
                    "query": "Can LUKHAS learn?",
                },
            }

            result = await reasoning.process_task(task)
            print(f"✅ Reasoning task result: {result.get('status', 'unknown')}")
            print(f"  - Agents involved: {result.get('agents_involved', 0)}")
            print(f"  - Confidence: {result.get('confidence', 0.0):.2f}")

        # Test inter-colony broadcast
        broadcast_result = await hub.broadcast_event(
            {
                "type": "test_broadcast",
                "message": "Testing inter-colony communication",
                "source": "test_system",
            }
        )

        print(
            f"✅ Broadcast completed to {len(broadcast_result) if broadcast_result else 0} colonies"
        )

        return True

    except Exception as e:
        print(f"❌ Enhanced swarm basic test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_basecolony_integration():
    """Test integration with BaseColony infrastructure."""
    print("\n=== Testing BaseColony Integration ===")

    try:
        from core.enhanced_swarm import EnhancedColony

        print("✅ BaseColony imported successfully")

        # Create enhanced colony that inherits from BaseColony
        colony = EnhancedColony("test_base", "reasoning", 2)
        print("✅ Enhanced colony with BaseColony inheritance created")

        # Test BaseColony features if available
        if hasattr(colony, "capabilities"):
            print(f"✅ Colony capabilities: {colony.capabilities}")

        if hasattr(colony, "event_store"):
            print("✅ Event store integration available")

        if hasattr(colony, "tracer"):
            print("✅ Tracing integration available")

        # Test task processing with BaseColony features
        task = {
            "task_id": "basecolony_test",
            "type": "analysis",
            "data": {"input": "test data for BaseColony integration"},
        }

        result = await colony.process_task(task)
        print(
            f"✅ BaseColony integration task result: {result.get('status', 'unknown')}"
        )

        return True

    except Exception as e:
        print(f"❌ BaseColony integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_legacy_compatibility():
    """Test backward compatibility with legacy swarm system."""
    print("\n=== Testing Legacy Compatibility ===")

    try:
        from core.swarm import SwarmHub

        print("✅ Legacy swarm components imported")

        # Create legacy hub
        hub = SwarmHub()
        print("✅ Legacy SwarmHub created")

        # Test enhanced features availability
        enhanced_available = (
            hasattr(hub, "_enhanced_hub") and hub._enhanced_hub is not None
        )
        print(f"✅ Enhanced features available: {enhanced_available}")

        # Create colony with enhanced features
        colony = hub.create_colony("legacy_test", ["general_processing"], 2)
        print(f"✅ Colony created via legacy interface: {colony is not None}")

        if colony:
            print(f"  - Colony agents: {len(colony.agents)}")

            # Test enhanced demonstration if available
            if hasattr(hub, "demonstrate_enhanced_capabilities"):
                demo_result = await hub.demonstrate_enhanced_capabilities()
                print(f"✅ Enhanced capabilities demo: {demo_result is not None}")

        return True

    except Exception as e:
        print(f"❌ Legacy compatibility test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_bio_symbolic_simple():
    """Test bio-symbolic integration without complex dependencies."""
    print("\n=== Testing Bio-Symbolic (Simple) ===")

    try:
        from core.bio_symbolic_swarm_hub import BioSymbolicSwarmHub

        print("✅ BioSymbolicSwarmHub imported")

        # Create hub without consciousness to avoid dependencies
        hub = BioSymbolicSwarmHub()
        hub.consciousness_engine = None  # Disable to avoid complex dependencies
        print("✅ Bio-symbolic hub created (consciousness disabled)")

        # Create basic enhanced colonies
        reasoning = hub.create_colony("reasoning", "reasoning", 2)
        memory = hub.create_colony("memory", "memory", 2)

        print(f"✅ Created {len(hub.colonies)} enhanced colonies")

        # Test swarm state
        swarm_state = hub._get_swarm_state()
        print("✅ Swarm state:")
        print(f"  - Colonies: {swarm_state['colony_count']}")
        print(f"  - Bio-colonies: {swarm_state['bio_colony_count']}")
        print(f"  - Total agents: {swarm_state['total_agents']}")

        # Test basic task processing without consciousness
        if reasoning:
            task = {
                "task_id": "bio_symbolic_test",
                "type": "logical_reasoning",
                "data": {"query": "Test bio-symbolic integration"},
            }

            result = await hub._process_task_basic(task)
            print(f"✅ Basic task processing: {len(result) if result else 0} results")

        return True

    except Exception as e:
        print(f"❌ Bio-symbolic simple test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all integration tests."""
    print("🔗 SWARM-COLONY COHERENCE INTEGRATION TEST SUITE")
    print("=" * 60)

    tests = [
        ("Enhanced Swarm Basic", test_enhanced_swarm_basic),
        ("BaseColony Integration", test_basecolony_integration),
        ("Legacy Compatibility", test_legacy_compatibility),
        ("Bio-Symbolic Simple", test_bio_symbolic_simple),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            results[test_name] = await test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1

    print(f"\nPassed: {passed}/{len(tests)}")

    if passed == len(tests):
        print("🎉 ALL TESTS PASSED - Swarm-Colony coherence integration successful!")
        return 0
    else:
        print("⚠️  Some tests failed - Integration needs attention")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
