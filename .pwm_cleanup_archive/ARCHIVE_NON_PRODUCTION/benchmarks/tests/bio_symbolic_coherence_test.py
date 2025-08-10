#!/usr/bin/env python3
"""
🚀 LUKHAS Bio-Symbolic Coherence Optimization Test
Comprehensive test of the new colony-based coherence system
"""

import asyncio
import json
import sys
from datetime import datetime

import numpy as np

sys.path.append(".")

from bio.symbolic.bio_symbolic_orchestrator import (
    create_bio_symbolic_orchestrator,
)


async def run_coherence_optimization_test():
    """Run comprehensive coherence optimization test."""
    print("🚀 LUKHAS BIO-SYMBOLIC COHERENCE OPTIMIZATION TEST")
    print("=" * 80)
    print(f"Test started at: {datetime.utcnow().isoformat()}")
    print("=" * 80)

    # Create orchestrator
    orchestrator = create_bio_symbolic_orchestrator("coherence_test_orchestrator")

    # Display system status
    status = await orchestrator.get_system_status()
    print("\n📊 SYSTEM STATUS:")
    print(f"  Orchestrator: {status['orchestrator_id']}")
    print(f"  Colonies: {', '.join(status['colonies'])}")
    print(f"  Coherence Target: {status['coherence_target']:.0%}")
    print(f"  Coherence Threshold: {status['coherence_threshold']:.0%}")

    # Test scenarios
    test_scenarios = [
        {
            "name": "Optimal State",
            "bio_data": {
                "heart_rate": 68,
                "temperature": 37.0,
                "energy_level": 0.85,
                "cortisol": 8,
                "ph": 7.4,
                "glucose": 95,
                "atp_level": 0.9,
                "efficiency": 0.88,
            },
            "context": {
                "environment": {"temperature": 22, "humidity": 45, "light_level": 0.7},
                "user_profile": {
                    "age_group": "adult",
                    "fitness_level": "high",
                    "chronotype": "neutral",
                },
                "quantum": {"coherence": 0.9, "entanglement": 0.8},
            },
        },
        {
            "name": "Stress Response",
            "bio_data": {
                "heart_rate": 95,
                "temperature": 37.8,
                "energy_level": 0.6,
                "cortisol": 18,
                "ph": 7.35,
                "glucose": 130,
                "atp_level": 0.5,
                "efficiency": 0.6,
            },
            "context": {
                "environment": {"temperature": 26, "humidity": 60, "noise_level": 0.8},
                "user_profile": {"age_group": "adult", "stress_tolerance": 0.4},
                "recent_activities": {"mental": 0.9, "social": 0.7},
            },
        },
        {
            "name": "Deep Rest",
            "bio_data": {
                "heart_rate": 55,
                "temperature": 36.5,
                "energy_level": 0.3,
                "cortisol": 4,
                "ph": 7.42,
                "glucose": 85,
                "atp_level": 0.4,
                "efficiency": 0.5,
            },
            "context": {
                "environment": {"temperature": 20, "humidity": 40, "light_level": 0.1},
                "personal_state": {"mood": "peaceful", "energy_perception": 0.2},
                "quantum": {"coherence": 0.7},
            },
        },
        {
            "name": "High Performance",
            "bio_data": {
                "heart_rate": 75,
                "temperature": 37.2,
                "energy_level": 0.95,
                "cortisol": 10,
                "ph": 7.38,
                "glucose": 98,
                "atp_level": 0.95,
                "efficiency": 0.92,
            },
            "context": {
                "environment": {"temperature": 21, "humidity": 50},
                "user_profile": {"fitness_level": "elite", "chronotype": "morning"},
                "recent_activities": {"physical": 0.8, "mental": 0.7},
                "quantum": {"coherence": 0.95, "entanglement": 0.9},
            },
        },
        {
            "name": "Anomalous Data",
            "bio_data": {
                "heart_rate": 200,  # Anomalous
                "temperature": 39.5,  # High fever
                "energy_level": -0.2,  # Invalid
                "cortisol": 50,  # Very high
                "ph": 6.8,  # Too low
                "glucose": 300,  # Diabetic range
                "atp_level": 1.5,  # Invalid
                "efficiency": 0.1,
            },
            "context": {
                "environment": {"temperature": 35, "humidity": 90},  # Hot
                "user_profile": {"age_group": "elderly"},
            },
        },
    ]

    test_results = []
    coherence_improvements = []

    print(f"\n🧪 RUNNING {len(test_scenarios)} TEST SCENARIOS")
    print("=" * 80)

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🔬 TEST {i}: {scenario['name']}")
        print("-" * 60)

        try:
            # Execute orchestration
            result = await orchestrator.execute_task(
                f"coherence_test_{i}",
                {"bio_data": scenario["bio_data"], "context": scenario["context"]},
            )

            # Extract key metrics
            coherence = result["coherence_metrics"]

            print("  📊 COHERENCE METRICS:")
            print(f"    Overall Coherence: {coherence.overall_coherence:.2%}")
            print(f"    Preprocessing Quality: {coherence.preprocessing_quality:.2%}")
            print(f"    Threshold Confidence: {coherence.threshold_confidence:.2%}")
            print(f"    Mapping Confidence: {coherence.mapping_confidence:.2%}")
            print(f"    Anomaly Confidence: {coherence.anomaly_confidence:.2%}")
            print(f"    Quantum Alignment: {coherence.quantum_alignment:.2%}")
            print(f"    Colony Consensus: {coherence.colony_consensus:.2%}")

            print("\n  🎯 PROCESSING RESULTS:")
            print(f"    Quality Assessment: {result['quality_assessment']}")
            print(f"    Processing Time: {result['processing_time_ms']:.1f}ms")
            print(
                f"    Primary GLYPH: {result['bio_symbolic_state'].get('primary_glyph', 'None')}"
            )

            # Check for enhancements
            bio_state = result["bio_symbolic_state"]
            enhancements = []
            if bio_state.get("quantum_enhanced"):
                enhancements.append("Quantum Enhanced")
            if bio_state.get("self_healing_activated"):
                enhancements.append("Self-Healing Applied")
            if bio_state.get("quantum_phase_aligned"):
                enhancements.append("Phase Aligned")

            if enhancements:
                print(f"    Enhancements: {', '.join(enhancements)}")

            # Check for anomalies
            if bio_state.get("anomalies_detected"):
                anomaly_count = len(bio_state.get("anomaly_details", []))
                print(f"    ⚠️  Anomalies Detected: {anomaly_count}")

                # Show anomaly explanations
                for detail in bio_state.get("anomaly_details", [])[:3]:  # Show first 3
                    print(
                        f"      - {detail.get('type', 'Unknown')}: Severity {detail.get('severity', 0):.1f}"
                    )

            # Recommendations
            recommendations = result["recommendations"]
            if recommendations and recommendations != [
                "Maintain current excellent performance"
            ]:
                print("    💡 Recommendations:")
                for rec in recommendations[:3]:  # Show first 3
                    print(f"      - {rec}")

            # Store results
            test_results.append(
                {
                    "scenario": scenario["name"],
                    "coherence": coherence.overall_coherence,
                    "quality": result["quality_assessment"],
                    "processing_time": result["processing_time_ms"],
                    "enhancements": enhancements,
                    "anomalies": bio_state.get("anomalies_detected", False),
                }
            )

            # Track improvements from original 29% baseline
            improvement = (coherence.overall_coherence - 0.29) / 0.29 * 100
            coherence_improvements.append(improvement)

            print(f"    📈 Improvement vs 29% baseline: {improvement:+.1f}%")

        except Exception as e:
            print(f"    ❌ Test failed: {str(e)}")
            import traceback

            traceback.print_exc()
            test_results.append({"scenario": scenario["name"], "error": str(e)})

    # Summary analysis
    print("\n\n📈 PERFORMANCE ANALYSIS")
    print("=" * 80)

    successful_tests = [r for r in test_results if "error" not in r]

    # Initialize variables with defaults
    coherences = []
    processing_times = []
    quality_counts = {}
    target_achieved = 0
    threshold_achieved = 0

    if successful_tests:
        coherences = [r["coherence"] for r in successful_tests]
        processing_times = [r["processing_time"] for r in successful_tests]

        print(f"  Successful Tests: {len(successful_tests)}/{len(test_scenarios)}")
        print(f"  Average Coherence: {np.mean(coherences):.2%}")
        print(f"  Coherence Range: {min(coherences):.2%} - {max(coherences):.2%}")
        print(f"  Average Processing Time: {np.mean(processing_times):.1f}ms")
        print(f"  Average Improvement: {np.mean(coherence_improvements):+.1f}%")

        # Quality distribution
        qualities = [r["quality"] for r in successful_tests]
        quality_counts = {}
        for q in qualities:
            quality_counts[q] = quality_counts.get(q, 0) + 1

        print("\n  📊 Quality Distribution:")
        for quality, count in quality_counts.items():
            print(
                f"    {quality}: {count}/{len(successful_tests)} ({count/len(successful_tests)*100:.0f}%)"
            )

        # Enhancement usage
        all_enhancements = []
        for r in successful_tests:
            all_enhancements.extend(r.get("enhancements", []))

        if all_enhancements:
            print("\n  🚀 Enhancement Usage:")
            enhancement_counts = {}
            for e in all_enhancements:
                enhancement_counts[e] = enhancement_counts.get(e, 0) + 1

            for enhancement, count in enhancement_counts.items():
                print(f"    {enhancement}: {count} times")

        # Target achievement
        target_achieved = sum(1 for c in coherences if c >= 0.85)
        threshold_achieved = sum(1 for c in coherences if c >= 0.7)

        print("\n  🎯 Target Achievement:")
        print(
            f"    Target (85%+): {target_achieved}/{len(successful_tests)} ({target_achieved/len(successful_tests)*100:.0f}%)"
        )
        print(
            f"    Threshold (70%+): {threshold_achieved}/{len(successful_tests)} ({threshold_achieved/len(successful_tests)*100:.0f}%)"
        )

        # Comparison with baseline
        baseline_coherence = 0.29
        avg_coherence = np.mean(coherences)
        improvement_factor = avg_coherence / baseline_coherence

        print("\n  📊 BASELINE COMPARISON:")
        print(f"    Original System: {baseline_coherence:.0%}")
        print(f"    Optimized System: {avg_coherence:.2%}")
        print(f"    Improvement Factor: {improvement_factor:.1f}x")
        print(
            f"    Absolute Improvement: {(avg_coherence - baseline_coherence)*100:+.0f} percentage points"
        )

    # System health check
    final_status = await orchestrator.get_system_status()
    print("\n  🏥 SYSTEM HEALTH:")
    print(f"    Status: {final_status['status']}")
    print(
        f"    Learning Rate: {final_status['optimization_state']['learning_rate']:.4f}"
    )
    if final_status["optimization_state"]["baselines"]:
        baselines = final_status["optimization_state"]["baselines"]
        if "coherence" in baselines:
            print(f"    Coherence Baseline: {baselines['coherence']:.2%}")

    # Save detailed results
    detailed_results = {
        "test_id": f"COHERENCE_OPT_TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "system_status": final_status,
        "test_scenarios": len(test_scenarios),
        "successful_tests": len(successful_tests),
        "average_coherence": np.mean(coherences) if coherences else 0,
        "coherence_improvement": (
            np.mean(coherence_improvements) if coherence_improvements else 0
        ),
        "test_results": test_results,
        "performance_metrics": {
            "target_achievement_rate": (
                target_achieved / len(successful_tests) if successful_tests else 0
            ),
            "threshold_achievement_rate": (
                threshold_achieved / len(successful_tests) if successful_tests else 0
            ),
            "average_processing_time_ms": (
                np.mean(processing_times) if processing_times else 0
            ),
            "quality_distribution": quality_counts if successful_tests else {},
        },
    }

    with open("logs/coherence_optimization_test_results.json", "w") as f:
        json.dump(detailed_results, f, indent=2, default=str)

    print(
        "\n💾 Detailed results saved to: logs/coherence_optimization_test_results.json"
    )

    # Final verdict
    print("\n🏆 FINAL VERDICT")
    print("=" * 80)

    if successful_tests:
        avg_coherence = np.mean(coherences)

        if avg_coherence >= 0.85:
            verdict = "🌟 EXCELLENT - Target coherence achieved!"
            color = "green"
        elif avg_coherence >= 0.7:
            verdict = "✅ SUCCESS - Threshold coherence achieved!"
            color = "blue"
        elif avg_coherence > 0.5:
            verdict = "⚠️  MODERATE - Improvement needed"
            color = "yellow"
        else:
            verdict = "❌ POOR - Significant optimization required"
            color = "red"

        print(f"  {verdict}")
        print(f"  Average coherence: {avg_coherence:.2%} (target: 85%)")
        print(f"  System improvement: {improvement_factor:.1f}x better than baseline")

        if target_achieved == len(successful_tests):
            print("  🎯 Perfect score: All tests achieved target coherence!")
        elif threshold_achieved == len(successful_tests):
            print("  ✅ All tests achieved minimum threshold coherence!")
        else:
            print(
                f"  📊 {threshold_achieved}/{len(successful_tests)} tests achieved threshold coherence"
            )

    else:
        print("  ❌ SYSTEM FAILURE - No tests completed successfully")

    print(f"\n🕒 Test completed at: {datetime.utcnow().isoformat()}")
    print("=" * 80)


if __name__ == "__main__":
    try:
        asyncio.run(run_coherence_optimization_test())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {str(e)}")
        import traceback

        traceback.print_exc()
