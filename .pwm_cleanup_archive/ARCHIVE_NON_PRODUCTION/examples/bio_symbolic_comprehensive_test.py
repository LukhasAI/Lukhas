#!/usr/bin/env python3
"""
Comprehensive Bio-Symbolic System Test
Demonstrates full capabilities of LUKHAS bio-symbolic integration
"""

import asyncio
import json
import sys
from datetime import datetime

sys.path.append(".")

from bio.symbolic.bio_symbolic import bio_symbolic, integrate_biological_state


async def run_comprehensive_test():
    """Run comprehensive bio-symbolic tests."""
    print("🧬 LUKHAS BIO-SYMBOLIC COMPREHENSIVE TEST")
    print("=" * 70)
    print(f"Test started at: {datetime.utcnow().isoformat()}")
    print("=" * 70)

    # Test 1: Circadian Rhythm Simulation
    print("\n📊 TEST 1: Circadian Rhythm Cycle (24-hour simulation)")
    print("-" * 60)

    for hour in [0, 6, 12, 18, 24]:
        # Simulate different times of day
        energy = 0.3 + 0.5 * abs(12 - hour) / 12  # Peak at noon
        hr = 60 + 20 * (1 - energy)  # Lower HR when more energy

        rhythm_data = {
            "type": "rhythm",
            "period": 24,
            "phase": "night" if hour < 6 or hour > 18 else "day",
            "amplitude": energy,
        }

        result = bio_symbolic.process(rhythm_data)
        print(f"\nHour {hour:02d}:00")
        print(f"  Energy: {energy:.2f}")
        print(f"  Heart Rate: {hr:.0f}")
        print(f"  Symbol: {result['glyph']} - {result['meaning']}")
        print(f"  Coherence: {result['coherence']:.2%}")

    # Test 2: Stress Response Test
    print("\n\n📊 TEST 2: Stress Response Adaptation")
    print("-" * 60)

    stress_scenarios = [
        ("Baseline", 0.2, "chronic"),
        ("Work Deadline", 0.6, "acute"),
        ("Emergency", 0.9, "acute"),
        ("Recovery", 0.4, "intermittent"),
    ]

    for scenario, level, duration in stress_scenarios:
        stress_data = {
            "type": "stress",
            "stress_type": "psychological",
            "level": level,
            "duration": duration,
        }

        result = bio_symbolic.process(stress_data)
        print(f"\n{scenario}:")
        print(f"  Stress Level: {level:.1f}")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Strategy: {result['strategy']}")
        print(f"  Protection: {result['protection']:.2%}")

    # Test 3: Energy State Transitions
    print("\n\n📊 TEST 3: Mitochondrial Energy States")
    print("-" * 60)

    energy_states = [
        ("Morning Wake", 0.4, 0.5, 0.6),
        ("Post-Breakfast", 0.8, 0.8, 0.2),
        ("Peak Performance", 0.95, 0.9, 0.1),
        ("Afternoon Dip", 0.5, 0.6, 0.4),
        ("Evening Wind-down", 0.3, 0.4, 0.7),
    ]

    for state_name, atp, efficiency, stress in energy_states:
        energy_data = {
            "type": "energy",
            "atp_level": atp,
            "efficiency": efficiency,
            "stress": stress,
        }

        result = bio_symbolic.process(energy_data)
        print(f"\n{state_name}:")
        print(f"  ATP: {atp:.2f}, Efficiency: {efficiency:.2f}")
        print(f"  Symbol: {result['power_glyph']}")
        print(f"  State: {result['interpretation']}")
        print(f"  Action: {result['recommended_action']}")

    # Test 4: Homeostatic Balance
    print("\n\n📊 TEST 4: Homeostatic Balance States")
    print("-" * 60)

    homeo_states = [
        ("Perfect Balance", 37.0, 7.4, 90),
        ("Slight Fever", 38.2, 7.35, 110),
        ("Dehydration", 37.5, 7.3, 120),
        ("Hypothermia Risk", 35.8, 7.45, 70),
    ]

    for state_name, temp, ph, glucose in homeo_states:
        homeo_data = {
            "type": "homeostasis",
            "temperature": temp,
            "ph": ph,
            "glucose": glucose,
        }

        result = bio_symbolic.process(homeo_data)
        print(f"\n{state_name}:")
        print(f"  Temp: {temp}°C, pH: {ph}, Glucose: {glucose}")
        print(f"  Symbol: {result['symbol']}")
        print(f"  State: {result['description']}")
        print(f"  Balance Score: {result['balance_score']:.2%}")

    # Test 5: Neural/Dream States
    print("\n\n📊 TEST 5: Neural States & Dream Generation")
    print("-" * 60)

    sleep_stages = [
        (
            "REM Sleep",
            {"theta": 0.8, "beta": 0.2},
            {"serotonin": 0.3, "acetylcholine": 0.9},
        ),
        (
            "Deep Sleep",
            {"delta": 0.9, "theta": 0.1},
            {"serotonin": 0.7, "acetylcholine": 0.2},
        ),
        (
            "Light Sleep",
            {"alpha": 0.6, "theta": 0.4},
            {"serotonin": 0.5, "acetylcholine": 0.5},
        ),
        (
            "Meditation",
            {"alpha": 0.8, "theta": 0.2},
            {"serotonin": 0.8, "dopamine": 0.6},
        ),
    ]

    for stage_name, waves, neurotrans in sleep_stages:
        neural_data = {
            "type": "neural",
            "stage": stage_name,
            "brain_waves": waves,
            "neurotransmitters": neurotrans,
        }

        result = bio_symbolic.process(neural_data)
        print(f"\n{stage_name}:")
        print(f"  Brain Waves: {waves}")
        print(f"  Symbol: {result['primary_symbol']}")
        print(f"  Theme: {result['theme']}")
        print(f"  Dream: {result['narrative_snippet']}")

    # Test 6: Full Integration Scenarios
    print("\n\n📊 TEST 6: Full Bio-Symbolic Integration Scenarios")
    print("-" * 60)

    scenarios = [
        {
            "name": "Peak Performance",
            "data": {
                "heart_rate": 65,
                "temperature": 37.0,
                "cortisol": 8,
                "energy_level": 0.9,
                "ph": 7.4,
                "glucose": 95,
            },
        },
        {
            "name": "Stress Response",
            "data": {
                "heart_rate": 95,
                "temperature": 37.8,
                "cortisol": 18,
                "energy_level": 0.6,
                "ph": 7.35,
                "glucose": 130,
            },
        },
        {
            "name": "Deep Rest",
            "data": {
                "heart_rate": 55,
                "temperature": 36.5,
                "cortisol": 4,
                "energy_level": 0.3,
                "ph": 7.42,
                "glucose": 85,
            },
        },
    ]

    for scenario in scenarios:
        print(f"\n🔗 Scenario: {scenario['name']}")
        integrated = await integrate_biological_state(scenario["data"])

        print(f"  Primary Symbol: {integrated['primary_symbol']}")
        print(f"  All Symbols: {' + '.join(integrated['all_symbols'])}")
        print(f"  Coherence: {integrated['coherence']:.2%}")
        print(f"  Quality: {integrated['integration_quality']}")

        # Show biological readings
        print("  Biological State:")
        for key, value in scenario["data"].items():
            print(f"    - {key}: {value}")

    # Test 7: DNA Sequence Processing
    print("\n\n📊 TEST 7: DNA Sequence Analysis")
    print("-" * 60)

    dna_samples = [
        ("Gene Promoter", "TATAAAAGGCC", "promoter"),
        ("Structural Region", "GGCCGGCCGGCC", "structural"),
        ("Regulatory Element", "ATCGATCGATCG", "regulatory"),
        ("Coding Sequence", "ATGGCATTAGCA", "coding"),
    ]

    for sample_name, sequence, function in dna_samples:
        dna_data = {"type": "dna", "sequence": sequence, "function": function}

        result = bio_symbolic.process(dna_data)
        print(f"\n{sample_name}:")
        print(f"  Sequence: {sequence}")
        print(f"  Function: {function}")
        print(f"  Symbol: {result['symbol']}")
        print(f"  Properties: {', '.join(result['properties'])}")
        print(f"  GC Content: {result['gc_content']:.2%}")

    # Final Statistics
    print("\n\n📊 FINAL STATISTICS")
    print("=" * 70)

    stats = bio_symbolic.get_statistics()
    print(f"Total Bio States Processed: {stats['total_bio_states']}")
    print(f"Total Symbolic Mappings: {stats['total_symbolic_mappings']}")
    print(f"Total Integration Events: {stats['total_integration_events']}")
    print(f"Average Coherence: {stats['average_coherence']:.2%}")

    # Save test results
    test_results = {
        "test_id": f"BIO_SYM_TEST_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.utcnow().isoformat(),
        "statistics": stats,
        "test_sections": [
            "Circadian Rhythm Cycle",
            "Stress Response Adaptation",
            "Mitochondrial Energy States",
            "Homeostatic Balance States",
            "Neural States & Dream Generation",
            "Full Bio-Symbolic Integration",
            "DNA Sequence Analysis",
        ],
    }

    with open("logs/bio_symbolic_test_results.json", "w") as f:
        json.dump(test_results, f, indent=2)

    print("\n✅ Test results saved to: logs/bio_symbolic_test_results.json")
    print("\n🎉 COMPREHENSIVE TEST COMPLETE!")
    print(f"Test ended at: {datetime.utcnow().isoformat()}")


if __name__ == "__main__":
    # Reset bio_symbolic processor before test
    bio_symbolic.reset()

    # Run the comprehensive test
    asyncio.run(run_comprehensive_test())
