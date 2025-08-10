"""
Specialized fixtures for symbolic system testing.

Provides comprehensive test data generators and fixtures specifically
for GLYPH, drift, and collapse testing in the LUKHAS symbolic system.
"""

import itertools
import random
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

# Symbolic test data constants
GLYPH_SYMBOLS = ["Λ", "Ψ", "Ω", "Δ", "Σ", "Φ", "Θ", "Ξ", "Π"]
GLYPH_MEANINGS = {
    "Λ": "transformation",
    "Ψ": "consciousness",
    "Ω": "completion",
    "Δ": "change",
    "Σ": "summation",
    "Φ": "golden_ratio",
    "Θ": "angle",
    "Ξ": "cascade",
    "Π": "product",
}


@pytest.fixture
def glyph_sequences():
    """Generate test GLYPH sequences."""
    sequences = [
        ["Λ", "Ψ", "Ω"],  # Transformation sequence
        ["Δ", "Δ", "Δ"],  # Repetition pattern
        ["Σ", "Λ", "Σ"],  # Oscillation pattern
        ["Φ", "Θ", "Λ", "Ψ", "Ω"],  # Extended sequence
        ["Λ", "Δ", "Λ", "Δ"],  # Alternating pattern
        ["Ω", "Ψ", "Λ"],  # Reverse transformation
        ["Ξ", "Π", "Σ", "Φ"],  # Complex symbols
    ]
    return sequences


@pytest.fixture
def glyph_transformation_rules():
    """Define GLYPH transformation rules for testing."""
    return {
        "rotate": {"Λ": "Ψ", "Ψ": "Ω", "Ω": "Δ", "Δ": "Σ", "Σ": "Λ"},
        "invert": {"Λ": "Ω", "Ω": "Λ", "Ψ": "Ψ", "Δ": "Σ", "Σ": "Δ"},
        "evolve": {"Λ": "Δ", "Δ": "Ψ", "Ψ": "Σ", "Σ": "Ω", "Ω": "Λ"},
    }


@pytest.fixture
def drift_scenarios():
    """Pre-defined drift test scenarios with detailed configurations."""
    return {
        "stable": {
            "states": [
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.5,
                    "entropy": 0.3,
                    "emotional_vector": [0.5, 0.5, 0.5],
                },
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.51,
                    "entropy": 0.31,
                    "emotional_vector": [0.49, 0.51, 0.5],
                },
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.49,
                    "entropy": 0.29,
                    "emotional_vector": [0.51, 0.49, 0.5],
                },
            ],
            "expected_drift": "low",
            "expected_score_range": (0.0, 0.2),
            "expected_alerts": 0,
        },
        "drifting": {
            "states": [
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.3,
                    "entropy": 0.2,
                    "emotional_vector": [0.3, 0.3, 0.3],
                },
                {
                    "glyphs": ["Ψ"],
                    "resonance": 0.5,
                    "entropy": 0.4,
                    "emotional_vector": [0.5, 0.5, 0.5],
                },
                {
                    "glyphs": ["Ω"],
                    "resonance": 0.7,
                    "entropy": 0.6,
                    "emotional_vector": [0.7, 0.7, 0.7],
                },
            ],
            "expected_drift": "medium",
            "expected_score_range": (0.3, 0.6),
            "expected_alerts": 1,
        },
        "chaotic": {
            "states": [
                {
                    "glyphs": ["Λ", "Ψ", "Ω"],
                    "resonance": 0.1,
                    "entropy": 0.9,
                    "emotional_vector": [0.9, 0.1, 0.5],
                },
                {
                    "glyphs": ["Δ"],
                    "resonance": 0.9,
                    "entropy": 0.1,
                    "emotional_vector": [0.1, 0.9, 0.5],
                },
                {
                    "glyphs": ["Σ", "Φ", "Θ"],
                    "resonance": 0.5,
                    "entropy": 0.5,
                    "emotional_vector": [0.5, 0.5, 0.5],
                },
            ],
            "expected_drift": "high",
            "expected_score_range": (0.7, 1.0),
            "expected_alerts": 2,
        },
        "oscillating": {
            "states": [
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.2,
                    "entropy": 0.3,
                    "emotional_vector": [0.2, 0.8, 0.5],
                },
                {
                    "glyphs": ["Ω"],
                    "resonance": 0.8,
                    "entropy": 0.7,
                    "emotional_vector": [0.8, 0.2, 0.5],
                },
                {
                    "glyphs": ["Λ"],
                    "resonance": 0.2,
                    "entropy": 0.3,
                    "emotional_vector": [0.2, 0.8, 0.5],
                },
                {
                    "glyphs": ["Ω"],
                    "resonance": 0.8,
                    "entropy": 0.7,
                    "emotional_vector": [0.8, 0.2, 0.5],
                },
            ],
            "expected_drift": "cyclic",
            "expected_score_range": (0.5, 0.8),
            "expected_alerts": 3,
        },
    }


@pytest.fixture
def collapse_configurations():
    """Different collapse engine configurations for testing."""
    return {
        "deterministic": {
            "stochastic": False,
            "threshold": 0.7,
            "hysteresis": 0.0,
            "coherence_factor": 1.0,
        },
        "stochastic": {
            "stochastic": True,
            "threshold": 0.7,
            "hysteresis": 0.1,
            "coherence_factor": 1.5,
        },
        "sensitive": {
            "stochastic": True,
            "threshold": 0.3,
            "hysteresis": 0.05,
            "coherence_factor": 2.0,
        },
        "resistant": {
            "stochastic": True,
            "threshold": 0.9,
            "hysteresis": 0.2,
            "coherence_factor": 0.5,
        },
        "adaptive": {
            "stochastic": True,
            "threshold": 0.6,
            "hysteresis": 0.15,
            "coherence_factor": 1.2,
            "adaptive_rate": 0.01,
        },
    }


@pytest.fixture
def quantum_superposition_states():
    """Generate various superposition-like state test states."""
    return [
        {  # Binary choice
            "name": "binary",
            "possibilities": [
                {"action": "yes", "probability": 0.6},
                {"action": "no", "probability": 0.4},
            ],
            "uncertainty": 0.8,
            "coherence": 0.7,
        },
        {  # Multiple equal options
            "name": "equal_choice",
            "possibilities": [
                {"action": f"option_{i}", "probability": 0.25} for i in range(4)
            ],
            "uncertainty": 0.9,
            "coherence": 0.5,
        },
        {  # Weighted distribution
            "name": "weighted",
            "possibilities": [
                {"action": "primary", "probability": 0.7},
                {"action": "secondary", "probability": 0.2},
                {"action": "tertiary", "probability": 0.1},
            ],
            "uncertainty": 0.6,
            "coherence": 0.8,
        },
        {  # Complex multi-dimensional
            "name": "complex",
            "possibilities": [
                {
                    "action": "navigate",
                    "path": ["A", "B", "C"],
                    "cost": 10,
                    "probability": 0.4,
                },
                {"action": "wait", "duration": 5, "probability": 0.3},
                {"action": "retreat", "distance": 100, "probability": 0.3},
            ],
            "uncertainty": 0.85,
            "coherence": 0.6,
        },
    ]


@pytest.fixture
def symbolic_state_generator():
    """Generate random symbolic states for property testing."""

    def _generate(seed=None, count=1):
        if seed:
            random.seed(seed)
            np.random.seed(seed)

        states = []
        for _ in range(count):
            num_glyphs = random.randint(1, 5)
            state = {
                "glyphs": random.sample(GLYPH_SYMBOLS, k=num_glyphs),
                "resonance": random.random(),
                "entropy": random.random(),
                "drift_score": random.random() * 0.5,
                "collapse_threshold": 0.5 + random.random() * 0.4,
                "coherence": random.random(),
                "emotional_vector": [random.random() for _ in range(3)],
                "timestamp": (
                    datetime.now(timezone.utc)
                    + timedelta(seconds=random.randint(-3600, 3600))
                ).isoformat(),
                "metadata": {
                    "source": random.choice(
                        ["sensor", "introspection", "dream", "reasoning"]
                    ),
                    "confidence": random.random(),
                    "tag": f"state_{random.randint(1000, 9999)}",
                },
            }
            states.append(state)

        return states[0] if count == 1 else states

    return _generate


@pytest.fixture
def glyph_pair_generator():
    """Generate pairs of glyphs for transformation testing."""

    def _generate_pairs(transformation_type="all"):
        pairs = []

        if transformation_type in ["all", "identity"]:
            # Identity pairs
            for glyph in GLYPH_SYMBOLS[:5]:
                pairs.append((glyph, glyph))

        if transformation_type in ["all", "adjacent"]:
            # Adjacent transformations
            for i in range(len(GLYPH_SYMBOLS) - 1):
                pairs.append((GLYPH_SYMBOLS[i], GLYPH_SYMBOLS[i + 1]))

        if transformation_type in ["all", "inverse"]:
            # Inverse pairs
            inverse_map = {"Λ": "Ω", "Ω": "Λ", "Ψ": "Ψ", "Δ": "Σ", "Σ": "Δ"}
            for g1, g2 in inverse_map.items():
                pairs.append((g1, g2))

        return pairs

    return _generate_pairs


@pytest.fixture
def drift_trajectory_generator():
    """Generate drift trajectories for testing drift patterns."""

    def _generate_trajectory(pattern: str = "linear", length: int = 10):
        trajectories = {
            "linear": lambda i: i / (length - 1),
            "exponential": lambda i: (np.exp(i / (length - 1)) - 1) / (np.e - 1),
            "logarithmic": lambda i: np.log(i + 1) / np.log(length),
            "sinusoidal": lambda i: (np.sin(2 * np.pi * i / length) + 1) / 2,
            "step": lambda i: 0.0 if i < length // 2 else 1.0,
            "random": lambda i: random.random(),
        }

        func = trajectories.get(pattern, trajectories["linear"])
        return [func(i) for i in range(length)]

    return _generate_trajectory


@pytest.fixture
def symbolic_event_stream():
    """Generate stream of symbolic events for testing."""

    def _generate_stream(duration_seconds: int = 60, events_per_second: float = 1.0):
        events = []
        current_time = datetime.now(timezone.utc)

        num_events = int(duration_seconds * events_per_second)
        for i in range(num_events):
            event_time = current_time + timedelta(seconds=i / events_per_second)

            event = {
                "timestamp": event_time.isoformat(),
                "event_type": random.choice(
                    [
                        "glyph_change",
                        "drift_detected",
                        "collapse_triggered",
                        "resonance_shift",
                    ]
                ),
                "glyph": random.choice(GLYPH_SYMBOLS),
                "metrics": {
                    "drift": random.random() * 0.5,
                    "entropy": random.random(),
                    "resonance": random.random(),
                },
                "triggered_by": random.choice(
                    ["user", "system", "autonomous", "cascade"]
                ),
            }
            events.append(event)

        return events

    return _generate_stream


@pytest.fixture
def collapse_test_matrix():
    """Generate test matrix for collapse boundary testing."""
    thresholds = [0.3, 0.5, 0.7, 0.9]
    uncertainties = [0.0, 0.25, 0.5, 0.75, 1.0]
    coherences = [0.1, 0.5, 0.9]

    test_cases = []
    for threshold, uncertainty, coherence in itertools.product(
        thresholds, uncertainties, coherences
    ):
        # Determine expected outcome
        effective_threshold = threshold * (2.0 - coherence)
        should_collapse = uncertainty >= effective_threshold

        test_cases.append(
            {
                "threshold": threshold,
                "uncertainty": uncertainty,
                "coherence": coherence,
                "expected_collapse": should_collapse,
                "effective_threshold": effective_threshold,
            }
        )

    return test_cases


@pytest.fixture
def symbolic_benchmark_data():
    """Large dataset for performance benchmarking."""

    def _generate_benchmark(size: str = "small"):
        sizes = {"small": 100, "medium": 1000, "large": 10000, "xlarge": 100000}

        num_states = sizes.get(size, sizes["small"])

        # Pre-generate to avoid overhead during tests
        states = []
        for i in range(num_states):
            states.append(
                {
                    "id": f"benchmark_{i}",
                    "glyphs": random.sample(GLYPH_SYMBOLS, k=random.randint(1, 3)),
                    "metrics": {
                        "resonance": random.random(),
                        "entropy": random.random(),
                        "drift": random.random() * 0.5,
                    },
                }
            )

        return states

    return _generate_benchmark
