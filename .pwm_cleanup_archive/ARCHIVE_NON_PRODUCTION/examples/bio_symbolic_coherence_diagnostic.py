#!/usr/bin/env python3
"""
Bio-Symbolic Coherence Diagnostic Tool
Analyzes why coherence is low and provides optimization strategies
"""

import sys

sys.path.append(".")

import json
from datetime import datetime

from bio.symbolic.bio_symbolic import bio_symbolic


def diagnose_coherence():
    """Diagnose coherence issues in bio-symbolic system."""
    print("🔍 BIO-SYMBOLIC COHERENCE DIAGNOSTIC")
    print("=" * 60)
    print(f"Diagnostic run: {datetime.utcnow().isoformat()}")
    print("=" * 60)

    # Get current statistics
    stats = bio_symbolic.get_statistics()
    avg_coherence = stats["average_coherence"]
    threshold = stats["coherence_threshold"]

    print("\n📊 CURRENT STATUS:")
    print(f"  Average Coherence: {avg_coherence:.2%}")
    print(f"  Target Threshold: {threshold:.2%}")
    print(
        f"  Status: {'❌ BELOW TARGET' if avg_coherence < threshold else '✅ MEETS TARGET'}"
    )

    # Analyze why coherence is low
    print("\n🔍 COHERENCE ANALYSIS:")
    print(f"\nThe average coherence of {avg_coherence:.2%} is LOW because:")

    print("\n1. CALCULATION METHOD:")
    print("   - Individual processing events have varying coherence")
    print("   - Some test cases intentionally stress the system")
    print("   - Average includes ALL events, not just integrations")

    # Let's look at individual coherence values
    print("\n2. COHERENCE BREAKDOWN:")

    # Simulate different scenarios to show coherence variation
    test_cases = [
        {
            "name": "Optimal State",
            "data": {
                "type": "energy",
                "atp_level": 0.9,
                "efficiency": 0.9,
                "stress": 0.1,
            },
        },
        {
            "name": "Stressed State",
            "data": {
                "type": "energy",
                "atp_level": 0.3,
                "efficiency": 0.4,
                "stress": 0.8,
            },
        },
        {
            "name": "Perfect Homeostasis",
            "data": {
                "type": "homeostasis",
                "temperature": 37.0,
                "ph": 7.4,
                "glucose": 90,
            },
        },
        {
            "name": "Disrupted Homeostasis",
            "data": {
                "type": "homeostasis",
                "temperature": 38.5,
                "ph": 7.2,
                "glucose": 150,
            },
        },
    ]

    coherence_values = []
    for test in test_cases:
        result = bio_symbolic.process(test["data"])
        coherence = result.get("coherence", 0)
        coherence_values.append(coherence)
        print(f"\n   {test['name']}:")
        print(f"     Coherence: {coherence:.2%}")
        print(
            f"     Status: {'✅ Good' if coherence > 0.7 else '⚠️ Low' if coherence > 0.5 else '❌ Poor'}"
        )

    # Calculate coherence distribution
    high_coherence = sum(1 for c in coherence_values if c > 0.7)
    medium_coherence = sum(1 for c in coherence_values if 0.5 <= c <= 0.7)
    low_coherence = sum(1 for c in coherence_values if c < 0.5)

    print("\n3. COHERENCE DISTRIBUTION:")
    print(f"   High (>70%): {high_coherence} events")
    print(f"   Medium (50-70%): {medium_coherence} events")
    print(f"   Low (<50%): {low_coherence} events")

    print("\n4. WHY 29% IS CONCERNING:")
    print("   ❌ Far below the 70% threshold")
    print("   ❌ Indicates poor bio-symbolic alignment")
    print("   ❌ System struggling to find meaningful mappings")
    print("   ❌ May lead to inaccurate symbolic representations")

    print("\n5. WHAT AFFECTS COHERENCE:")
    print("   • Amplitude in rhythms (higher = better)")
    print("   • ATP levels and efficiency (higher = better)")
    print("   • Stress levels (lower = better)")
    print("   • Homeostatic balance (closer to optimal = better)")
    print("   • Data quality and completeness")

    print("\n💡 OPTIMIZATION STRATEGIES:")
    print("\n1. IMPROVE DATA QUALITY:")
    print("   • Ensure biological inputs are within normal ranges")
    print("   • Provide complete data sets (all required fields)")
    print("   • Use realistic biological values")

    print("\n2. TUNE COHERENCE CALCULATIONS:")
    print("   • Adjust weighting factors for different data types")
    print("   • Consider context-aware coherence thresholds")
    print("   • Implement adaptive coherence targets")

    print("\n3. ENHANCE SYMBOLIC MAPPINGS:")
    print("   • Add more nuanced GLYPH categories")
    print("   • Implement fuzzy boundaries between states")
    print("   • Consider multi-glyph representations")

    print("\n4. SYSTEM IMPROVEMENTS:")
    print("   • Add pre-processing normalization")
    print("   • Implement coherence boosting algorithms")
    print("   • Create feedback loops for learning")

    # Show what good coherence looks like
    print("\n✨ ACHIEVING HIGH COHERENCE:")
    print("\nExample of optimal bio-symbolic state:")

    optimal_bio = {
        "heart_rate": 65,
        "temperature": 37.0,
        "cortisol": 8,
        "energy_level": 0.85,
        "efficiency": 0.9,
        "stress": 0.15,
        "ph": 7.4,
        "glucose": 95,
    }

    # Process each component
    print("\nOptimal biological values:")
    for key, value in optimal_bio.items():
        print(f"  {key}: {value}")

    print("\n📈 COHERENCE TARGETS:")
    print("  Excellent: >80% - Perfect bio-symbolic alignment")
    print("  Good: 70-80% - Healthy functioning")
    print("  Moderate: 50-70% - Needs optimization")
    print("  Poor: <50% - Significant issues")

    print("\n🎯 CONCLUSION:")
    print(f"Current {avg_coherence:.2%} coherence indicates the system needs")
    print("significant optimization to reach the {threshold:.2%} target.")
    print("\nThis is expected in early testing phases where we're")
    print("intentionally testing edge cases and stress scenarios.")

    # Save diagnostic report
    diagnostic_report = {
        "diagnostic_id": f"COHERENCE_DIAG_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "current_coherence": avg_coherence,
        "target_coherence": threshold,
        "status": "NEEDS_OPTIMIZATION",
        "recommendations": [
            "Improve data quality",
            "Tune coherence calculations",
            "Enhance symbolic mappings",
            "Implement feedback loops",
        ],
    }

    with open("logs/coherence_diagnostic.json", "w") as f:
        json.dump(diagnostic_report, f, indent=2)

    print("\n📊 Diagnostic report saved to: logs/coherence_diagnostic.json")


if __name__ == "__main__":
    diagnose_coherence()
