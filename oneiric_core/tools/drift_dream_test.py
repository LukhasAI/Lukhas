#!/usr/bin/env python3
"""
Drift Dream Test CLI

Deterministic drift analysis through oneiric symbol processing.
Maps to DoD 5(18) - Drift Dream Test tool writes concise report; reproducible.

Usage:
  python -m oneiric_core.tools.drift_dream_test --symbol LOYALTY --user sid-demo --seed 42 --json
  python -m oneiric_core.tools.drift_dream_test --symbol TRUST --user alice --seed 123

Features:
- Deterministic: fixed --seed produces byte-identical JSON
- No network by default (pure analysis)
- Zero import side-effects
- Symbol-based dream drift detection
"""

import argparse
import json
import hashlib
import sys
import time
from typing import Dict, Any, List

# Telemetry counters (no-op for v1)
class TelemetryCounter:
    def __init__(self, name: str):
        self.name = name
        self.value = 0

    def inc(self):
        self.value += 1

ATTEMPTS = TelemetryCounter("drift_dream_test_attempts")
SUCCESSES = TelemetryCounter("drift_dream_test_successes")
FAILURES = TelemetryCounter("drift_dream_test_failures")

SYMBOL_BASELINE_WEIGHTS = {
    "LOYALTY": {"core": 0.85, "peripheral": 0.15, "stability": 0.92},
    "TRUST": {"core": 0.78, "peripheral": 0.22, "stability": 0.88},
    "FREEDOM": {"core": 0.65, "peripheral": 0.35, "stability": 0.75},
    "JUSTICE": {"core": 0.82, "peripheral": 0.18, "stability": 0.89},
    "WISDOM": {"core": 0.90, "peripheral": 0.10, "stability": 0.95}
}

def analyze_symbol_drift(symbol: str, user_id: str, seed: int) -> Dict[str, Any]:
    """Analyze dream-state drift for given symbol."""
    # Get baseline weights
    baseline = SYMBOL_BASELINE_WEIGHTS.get(symbol, {
        "core": 0.75, "peripheral": 0.25, "stability": 0.80
    })

    # Deterministic hash-based analysis (no random)
    combined_input = f"{symbol}:{user_id}:{seed}"
    hash_bytes = hashlib.sha256(combined_input.encode()).digest()

    # Dream state analysis phases
    phases = []
    current_weight = baseline["core"]

    for phase_idx in range(5):  # 5-phase dream analysis
        # Deterministic drift calculation using hash bytes
        byte_val = hash_bytes[(phase_idx * 4) % len(hash_bytes)]
        drift_factor = (byte_val / 255.0 - 0.5) * 0.2  # Range -0.1 to +0.1
        new_weight = max(0.0, min(1.0, current_weight + drift_factor))

        phase_analysis = {
            "phase": phase_idx + 1,
            "symbol_weight": round(new_weight, 4),
            "drift_magnitude": round(abs(drift_factor), 4),
            "drift_direction": "positive" if drift_factor >= 0 else "negative",
            "coherence": round(1.0 - abs(new_weight - baseline["core"]), 4)
        }

        phases.append(phase_analysis)
        current_weight = new_weight

    # Calculate overall drift metrics
    total_drift = sum(p["drift_magnitude"] for p in phases)
    avg_coherence = sum(p["coherence"] for p in phases) / len(phases)
    stability_score = baseline["stability"] * avg_coherence

    return {
        "symbol": symbol,
        "user_id": user_id,
        "baseline": baseline,
        "phases": phases,
        "metrics": {
            "total_drift": round(total_drift, 4),
            "average_coherence": round(avg_coherence, 4),
            "stability_score": round(stability_score, 4),
            "risk_level": "high" if stability_score < 0.7 else "medium" if stability_score < 0.85 else "low"
        }
    }

def generate_dream_sequence(symbol: str, user_id: str, seed: int) -> List[Dict[str, Any]]:
    """Generate deterministic dream sequence for symbol analysis."""
    # Deterministic hash-based sequence generation
    combined_input = f"dreams:{symbol}:{user_id}:{seed}"
    hash_bytes = hashlib.sha256(combined_input.encode()).digest()

    sequence = []
    for i in range(3):  # 3-element dream sequence
        # Use different hash bytes for each element
        intensity_byte = hash_bytes[(i * 2) % len(hash_bytes)]
        clarity_byte = hash_bytes[(i * 2 + 1) % len(hash_bytes)]

        # Convert to ranges: intensity 0.3-0.9, clarity 0.4-0.8
        intensity = 0.3 + (intensity_byte / 255.0) * 0.6
        clarity = 0.4 + (clarity_byte / 255.0) * 0.4

        sequence.append({
            "sequence_id": i + 1,
            "dream_element": f"{symbol.lower()}_fragment_{i + 1}",
            "intensity": round(intensity, 3),
            "clarity": round(clarity, 3)
        })

    return sequence

def run_drift_test(symbol: str, user_id: str, seed: int) -> Dict[str, Any]:
    """Run complete drift dream test analysis."""
    ATTEMPTS.inc()

    try:
        # Core drift analysis
        drift_analysis = analyze_symbol_drift(symbol, user_id, seed)

        # Dream sequence generation
        dream_sequence = generate_dream_sequence(symbol, user_id, seed)

        # Compile results
        result = {
            "test_type": "drift_dream_test",
            "symbol": symbol,
            "user_id": user_id,
            "seed": seed,
            "drift_analysis": drift_analysis,
            "dream_sequence": dream_sequence,
            "summary": {
                "drift_detected": drift_analysis["metrics"]["total_drift"] > 0.2,
                "confidence": round(drift_analysis["metrics"]["stability_score"], 3),
                "recommendation": "monitor" if drift_analysis["metrics"]["risk_level"] == "medium" else
                                "investigate" if drift_analysis["metrics"]["risk_level"] == "high" else "stable"
            }
        }

        SUCCESSES.inc()
        return result

    except Exception as e:
        FAILURES.inc()
        raise

def main():
    parser = argparse.ArgumentParser(description="Oneiric Drift Dream Test CLI")
    parser.add_argument("--symbol",
                       type=str,
                       default="LOYALTY",
                       help="Symbol to analyze for drift")
    parser.add_argument("--user",
                       type=str,
                       default="test-user",
                       help="User ID for personalized analysis")
    parser.add_argument("--seed",
                       type=int,
                       default=42,
                       help="Random seed for deterministic analysis")
    parser.add_argument("--json",
                       action="store_true",
                       help="Output results as JSON")
    parser.add_argument("--verbose",
                       action="store_true",
                       help="Verbose output")

    args = parser.parse_args()

    try:
        # Run drift test
        start_time = time.perf_counter()
        result = run_drift_test(args.symbol.upper(), args.user, args.seed)
        execution_time = time.perf_counter() - start_time

        # Add execution metadata (no execution_time for determinism)
        result["metadata"] = {
            "cli_version": "1.0.0",
            "deterministic": True
        }

        if args.json:
            # Deterministic JSON output with sorted keys
            print(json.dumps(result, sort_keys=True, indent=2))
        else:
            # Human-readable output
            print(f"Drift Dream Test Results:")
            print(f"Symbol: {result['symbol']}")
            print(f"User: {result['user_id']}")
            print(f"Confidence: {result['summary']['confidence']}")
            print(f"Recommendation: {result['summary']['recommendation']}")

            if args.verbose:
                print(f"Raw Result: {json.dumps(result, sort_keys=True, indent=2)}")

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())