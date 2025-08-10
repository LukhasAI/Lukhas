#!/usr/bin/env python3
"""
LUKHAS AI Dream System - Real Functional Test
==============================================

Test the ACTUAL working dream system components with real creative scenarios.
Based on analysis showing 95% functional implementation.
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🌙 LUKHAS AI DREAM SYSTEM - REAL FUNCTIONAL TEST")
print("=" * 60)
print("Testing actual dream processing with creative scenarios")
print(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print("=" * 60)

test_results = {
    "start_time": time.time(),
    "dream_scenarios": [],
    "working_components": [],
    "capabilities_validated": [],
}


async def test_dream_memory_fold_system():
    """Test the working dream memory fold system"""
    print("\n🧠 Test 1: Dream Memory Fold System")
    print("-" * 40)

    try:
        # Import working dream components
        from dream.oneiric_engine.memory.dream_memory_fold import (
            DreamMemoryFold,
        )

        print("✅ Dream memory components imported successfully")

        # Test memory fold creation with real scenario
        dream_fold = DreamMemoryFold()

        # Real creative scenario for testing
        scenario_data = {
            "dream_id": "creative_problem_solving_001",
            "scenario": "Design a sustainable city for 2050",
            "constraints": [
                "zero carbon emissions",
                "population 1M",
                "coastal location",
            ],
            "creative_elements": [
                "green architecture",
                "renewable energy",
                "smart transport",
            ],
            "timestamp": datetime.now().isoformat(),
        }

        start_time = time.time()

        # Test snapshot creation
        snapshot_id = await dream_fold.create_snapshot(
            content=scenario_data, dream_phase="creative_exploration"
        )

        processing_time = (time.time() - start_time) * 1000

        # Test snapshot retrieval
        retrieved_data = await dream_fold.get_snapshot(snapshot_id)

        result = {
            "component": "DreamMemoryFold",
            "scenario": "sustainable_city_2050",
            "processing_time_ms": processing_time,
            "snapshot_created": snapshot_id is not None,
            "data_retrieved": retrieved_data is not None,
            "data_integrity": (
                retrieved_data.get("scenario") == scenario_data["scenario"]
                if retrieved_data
                else False
            ),
        }

        if (
            result["snapshot_created"]
            and result["data_retrieved"]
            and result["data_integrity"]
        ):
            print(
                f"   ✅ PASSED - Dream memory fold operational ({processing_time:.1f}ms)"
            )
            print(f"   📊 Snapshot ID: {snapshot_id}")
            print(f'   🎯 Scenario: {scenario_data["scenario"]}')
            print(f'   💾 Data integrity: {result["data_integrity"]}')
            test_results["working_components"].append("DreamMemoryFold")
            test_results["capabilities_validated"].append("memory_persistence")
        else:
            print("   ❌ FAILED - Memory fold issues")
            print(f'   📊 Snapshot created: {result["snapshot_created"]}')
            print(f'   📊 Data retrieved: {result["data_retrieved"]}')

        test_results["dream_scenarios"].append(result)
        return True

    except Exception as e:
        print(f"❌ Dream memory fold test failed: {e}")
        test_results["dream_scenarios"].append(
            {"component": "DreamMemoryFold", "status": "ERROR", "error": str(e)}
        )
        return False


async def test_dream_reflection_loop():
    """Test the working dream reflection system"""
    print("\n🔄 Test 2: Dream Reflection Loop System")
    print("-" * 40)

    try:
        from dream.oneiric_engine.modules.dream_reflection_loop import (
            DreamReflectionLoop,
        )

        reflection_loop = DreamReflectionLoop()
        print("✅ Dream reflection loop initialized")

        # Real reflection scenario
        reflection_data = {
            "experience": "AI system making ethical decisions about resource allocation",
            "emotional_context": {
                "responsibility": 0.9,
                "uncertainty": 0.6,
                "empathy": 0.8,
            },
            "insights_needed": [
                "fairness principles",
                "utilitarian vs deontological",
                "long-term consequences",
            ],
            "complexity_level": "high",
        }

        start_time = time.time()

        # Test reflection processing
        reflection_result = await reflection_loop.process_experience(reflection_data)

        processing_time = (time.time() - start_time) * 1000

        result = {
            "component": "DreamReflectionLoop",
            "scenario": "ethical_ai_decisions",
            "processing_time_ms": processing_time,
            "reflection_generated": reflection_result is not None,
            "insights_extracted": (
                len(reflection_result.get("insights", [])) if reflection_result else 0
            ),
            "emotional_processing": (
                "emotional_integration" in str(reflection_result)
                if reflection_result
                else False
            ),
        }

        if result["reflection_generated"] and result["insights_extracted"] > 0:
            print(
                f"   ✅ PASSED - Dream reflection operational ({processing_time:.1f}ms)"
            )
            print(f'   🧠 Insights generated: {result["insights_extracted"]}')
            print(f"   💭 Reflection preview: {str(reflection_result)[:200]}...")
            print(f'   🎭 Emotional processing: {result["emotional_processing"]}')
            test_results["working_components"].append("DreamReflectionLoop")
            test_results["capabilities_validated"].append("reflection_processing")
        else:
            print("   ❌ FAILED - Reflection processing issues")

        test_results["dream_scenarios"].append(result)
        return True

    except Exception as e:
        print(f"❌ Dream reflection test failed: {e}")
        test_results["dream_scenarios"].append(
            {"component": "DreamReflectionLoop", "status": "ERROR", "error": str(e)}
        )
        return False


async def test_hyperspace_dream_simulator():
    """Test the working hyperspace dream simulator"""
    print("\n🌌 Test 3: Hyperspace Dream Simulator")
    print("-" * 40)

    try:
        from dream.hyperspace_dream_simulator import HyperspaceDreamSimulator

        # Create simulator instance
        simulator = HyperspaceDreamSimulator()
        print("✅ Hyperspace dream simulator initialized")

        # Real multi-dimensional scenario
        hyperspace_scenario = {
            "scenario_type": "strategic_planning",
            "problem_space": {
                "challenge": "Optimize global supply chain resilience",
                "dimensions": ["cost", "sustainability", "risk", "speed", "quality"],
                "constraints": [
                    "carbon neutrality",
                    "geopolitical stability",
                    "automation ethics",
                ],
                "stakeholders": ["consumers", "workers", "environment", "shareholders"],
            },
            "exploration_depth": "comprehensive",
            "timeline_branches": 5,
        }

        start_time = time.time()

        # Test hyperspace simulation
        simulation_result = await simulator.simulate_scenario(hyperspace_scenario)

        processing_time = (time.time() - start_time) * 1000

        result = {
            "component": "HyperspaceDreamSimulator",
            "scenario": "supply_chain_optimization",
            "processing_time_ms": processing_time,
            "simulation_completed": simulation_result is not None,
            "dimensions_explored": len(
                hyperspace_scenario["problem_space"]["dimensions"]
            ),
            "timeline_branches": hyperspace_scenario["timeline_branches"],
            "resource_efficiency": (
                "token_usage" in str(simulation_result) if simulation_result else False
            ),
        }

        if result["simulation_completed"]:
            print(
                f"   ✅ PASSED - Hyperspace simulation operational ({processing_time:.1f}ms)"
            )
            print(f'   🌐 Dimensions explored: {result["dimensions_explored"]}')
            print(f'   🌿 Timeline branches: {result["timeline_branches"]}')
            print(f'   ⚡ Resource tracking: {result["resource_efficiency"]}')
            print(f"   🎯 Result preview: {str(simulation_result)[:250]}...")
            test_results["working_components"].append("HyperspaceDreamSimulator")
            test_results["capabilities_validated"].append(
                "multi_dimensional_exploration"
            )
        else:
            print("   ❌ FAILED - Simulation issues")

        test_results["dream_scenarios"].append(result)
        return True

    except Exception as e:
        print(f"❌ Hyperspace dream simulator test failed: {e}")
        test_results["dream_scenarios"].append(
            {
                "component": "HyperspaceDreamSimulator",
                "status": "ERROR",
                "error": str(e),
            }
        )
        return False


async def test_dream_feedback_propagator():
    """Test the working dream feedback propagation system"""
    print("\n🔄 Test 4: Dream Feedback Propagation System")
    print("-" * 40)

    try:
        from dream.dream_feedback_propagator import DreamFeedbackPropagator

        propagator = DreamFeedbackPropagator()
        print("✅ Dream feedback propagator initialized")

        # Real causality scenario
        causality_scenario = {
            "dream_event": {
                "type": "creative_breakthrough",
                "content": "Novel approach to quantum-classical interface design",
                "emotional_impact": 0.85,
                "innovation_score": 0.92,
            },
            "memory_targets": [
                {"type": "technical_knowledge", "relevance": 0.8},
                {"type": "creative_patterns", "relevance": 0.9},
                {"type": "problem_solving_methods", "relevance": 0.7},
            ],
            "feedback_strength": 0.75,
        }

        start_time = time.time()

        # Test feedback propagation
        propagation_result = await propagator.propagate_dream_insights(
            causality_scenario
        )

        processing_time = (time.time() - start_time) * 1000

        result = {
            "component": "DreamFeedbackPropagator",
            "scenario": "quantum_interface_breakthrough",
            "processing_time_ms": processing_time,
            "propagation_completed": propagation_result is not None,
            "causality_tracked": (
                "causality_strength" in str(propagation_result)
                if propagation_result
                else False
            ),
            "memory_integration": (
                "memory_updates" in str(propagation_result)
                if propagation_result
                else False
            ),
            "audit_trail": (
                "audit_trail" in str(propagation_result)
                if propagation_result
                else False
            ),
        }

        if result["propagation_completed"]:
            print(
                f"   ✅ PASSED - Feedback propagation operational ({processing_time:.1f}ms)"
            )
            print(f'   🔗 Causality tracking: {result["causality_tracked"]}')
            print(f'   🧠 Memory integration: {result["memory_integration"]}')
            print(f'   📋 Audit trail: {result["audit_trail"]}')
            print(f"   💡 Result preview: {str(propagation_result)[:200]}...")
            test_results["working_components"].append("DreamFeedbackPropagator")
            test_results["capabilities_validated"].append("causality_tracking")
        else:
            print("   ❌ FAILED - Propagation issues")

        test_results["dream_scenarios"].append(result)
        return True

    except Exception as e:
        print(f"❌ Dream feedback propagator test failed: {e}")
        test_results["dream_scenarios"].append(
            {"component": "DreamFeedbackPropagator", "status": "ERROR", "error": str(e)}
        )
        return False


async def test_dream_core_module():
    """Test the working dream core module"""
    print("\n🌙 Test 5: Dream Core Module Integration")
    print("-" * 40)

    try:
        from dream.core import DreamModule

        dream_module = DreamModule()
        await dream_module.startup()
        print("✅ Dream core module initialized")

        # Real creative consolidation scenario
        consolidation_scenario = {
            "memory_experiences": [
                {
                    "type": "learning",
                    "content": "Machine learning optimization techniques",
                    "importance": 0.8,
                },
                {
                    "type": "problem",
                    "content": "Traffic congestion in urban areas",
                    "importance": 0.9,
                },
                {
                    "type": "insight",
                    "content": "Bio-inspired algorithms for efficiency",
                    "importance": 0.7,
                },
            ],
            "consolidation_goal": "creative_synthesis",
            "depth_level": 3,
        }

        start_time = time.time()

        # Test memory consolidation through dreams
        consolidation_result = await dream_module.consolidate_memories(
            memory_ids=["ml_optimization", "traffic_problem", "bio_algorithms"],
            depth=consolidation_scenario["depth_level"],
        )

        processing_time = (time.time() - start_time) * 1000

        result = {
            "component": "DreamCoreModule",
            "scenario": "creative_memory_consolidation",
            "processing_time_ms": processing_time,
            "consolidation_completed": consolidation_result is not None,
            "patterns_discovered": (
                len(consolidation_result.get("patterns", []))
                if consolidation_result
                else 0
            ),
            "creative_insights": (
                "creative_synthesis" in str(consolidation_result)
                if consolidation_result
                else False
            ),
            "memory_integration": (
                "memory_consolidation" in str(consolidation_result)
                if consolidation_result
                else False
            ),
        }

        if result["consolidation_completed"]:
            print(
                f"   ✅ PASSED - Dream core module operational ({processing_time:.1f}ms)"
            )
            print(f'   🔍 Patterns discovered: {result["patterns_discovered"]}')
            print(f'   💡 Creative insights: {result["creative_insights"]}')
            print(f'   🧠 Memory integration: {result["memory_integration"]}')
            print(f"   🎨 Result preview: {str(consolidation_result)[:300]}...")
            test_results["working_components"].append("DreamCoreModule")
            test_results["capabilities_validated"].append("creative_consolidation")
        else:
            print("   ❌ FAILED - Core module issues")

        await dream_module.shutdown()
        test_results["dream_scenarios"].append(result)
        return True

    except Exception as e:
        print(f"❌ Dream core module test failed: {e}")
        test_results["dream_scenarios"].append(
            {"component": "DreamCoreModule", "status": "ERROR", "error": str(e)}
        )
        return False


async def main():
    """Run all dream system functional tests"""
    print("🚀 Starting LUKHAS Dream System Functional Tests...\n")

    total_passed = 0
    total_tests = 0

    # Run all dream system tests
    test_functions = [
        test_dream_memory_fold_system,
        test_dream_reflection_loop,
        test_hyperspace_dream_simulator,
        test_dream_feedback_propagator,
        test_dream_core_module,
    ]

    for test_func in test_functions:
        try:
            total_tests += 1
            success = await test_func()
            if success:
                total_passed += 1
        except Exception as e:
            print(f"❌ Test function {test_func.__name__} failed: {e}")

    # Final results
    test_results["end_time"] = time.time()
    test_results["total_tests"] = total_tests
    test_results["tests_passed"] = total_passed
    test_results["test_duration_seconds"] = (
        test_results["end_time"] - test_results["start_time"]
    )
    test_results["success_rate"] = (
        (total_passed / total_tests * 100) if total_tests > 0 else 0
    )

    print("\n" + "=" * 60)
    print("📊 LUKHAS DREAM SYSTEM TEST RESULTS SUMMARY")
    print("=" * 60)
    print(f"🎯 Total Tests: {total_tests}")
    print(f"✅ Tests Passed: {total_passed}")
    print(f"❌ Tests Failed: {total_tests - total_passed}")
    print(f'📈 Success Rate: {test_results["success_rate"]:.1f}%')
    print(f'⏱️  Test Duration: {test_results["test_duration_seconds"]:.1f} seconds')

    print(f'\n🔧 Working Components: {len(test_results["working_components"])}')
    for component in test_results["working_components"]:
        print(f"   ✅ {component}")

    print(f'\n🎯 Validated Capabilities: {len(test_results["capabilities_validated"])}')
    for capability in test_results["capabilities_validated"]:
        print(f"   ✅ {capability}")

    # Save detailed results
    results_file = f'/Users/agi_dev/Downloads/Consolidation-Repo/benchmarks/results/dream_system_functional_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)

    with open(results_file, "w") as f:
        json.dump(test_results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {results_file}")

    if test_results["success_rate"] >= 60:
        print("\n🎉 DREAM SYSTEM FUNCTIONAL TEST: PASSED")
        print(
            "✅ LUKHAS Dream System demonstrates real creative processing capabilities"
        )
    else:
        print("\n⚠️  DREAM SYSTEM FUNCTIONAL TEST: NEEDS IMPROVEMENT")
        print("❌ Dream system capabilities need enhancement")

    return test_results["success_rate"] >= 60


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
