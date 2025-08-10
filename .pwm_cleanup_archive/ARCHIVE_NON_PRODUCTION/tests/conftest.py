import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


# Configure event loop for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Shared fixtures for all tests
@pytest.fixture
def symbolic_state():
    """Provide test symbolic state."""
    return {
        "glyphs": ["Λ", "Ψ", "Ω"],
        "drift_score": 0.15,
        "collapse_threshold": 0.7,
        "entropy": 0.3,
        "coherence": 0.85,
    }


@pytest.fixture
def memory_context():
    """Provide test memory context."""
    return {
        "fold_level": 3,
        "causal_lineage": ["event_1", "event_2", "event_3"],
        "compression_ratio": 0.6,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"source": "test_fixture", "version": "1.0"},
    }


@pytest.fixture
def mock_consciousness():
    """Mock consciousness state for testing."""
    consciousness = Mock(
        awareness_level=0.8,
        emotional_state="neutral",
        cognitive_load=0.5,
        symbolic_resonance=0.7,
    )
    consciousness.process_awareness = Mock(return_value={"processed": True})
    consciousness.introspect = Mock(return_value={"insights": []})
    return consciousness


@pytest.fixture
def emotion_vector():
    """Provide test emotion vector."""
    return {
        "joy": 0.3,
        "sadness": 0.1,
        "anger": 0.0,
        "fear": 0.2,
        "surprise": 0.1,
        "disgust": 0.0,
        "trust": 0.5,
        "anticipation": 0.4,
        "valence": 0.6,
        "arousal": 0.4,
        "dominance": 0.5,
    }


@pytest.fixture
def test_memory_entry():
    """Provide a standard test memory entry."""
    return {
        "id": "test_mem_001",
        "content": "Test memory content with symbolic markers Λ and Ψ",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "emotional_valence": 0.7,
        "symbolic_markers": ["Λ", "Ψ"],
        "importance_score": 0.8,
        "causal_lineage": ["genesis", "event_1"],
        "fold_eligible": True,
        "metadata": {"source": "test", "category": "episodic"},
    }


@pytest.fixture
def mock_fold_engine():
    """Mock fold engine for testing."""
    engine = MagicMock()
    engine.fold = Mock(
        side_effect=lambda x: {
            "compressed_data": f"folded_{x.get('id', 'unknown')}",
            "fold_metadata": {
                "fold_level": 1,
                "compression_ratio": 0.6,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "symbolic_hash": "test_hash",
            },
        }
    )
    engine.unfold = Mock(
        side_effect=lambda x: {
            "id": x["compressed_data"].replace("folded_", ""),
            "content": "Unfolded test content",
        }
    )
    return engine


@pytest.fixture
def test_dream_state():
    """Provide test dream state."""
    return {
        "phase": "REM",
        "depth": 0.7,
        "symbolic_density": 0.8,
        "emotional_tone": "contemplative",
        "narrative_coherence": 0.6,
        "memory_consolidation_active": True,
    }


@pytest.fixture
def mock_drift_tracker():
    """Mock drift tracker for testing."""
    tracker = Mock()
    tracker.calculate_drift = Mock(return_value=0.15)
    tracker.register_state = Mock()
    tracker.get_drift_history = Mock(return_value=[])
    return tracker


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return {
        "memory": {
            "max_fold_level": 10,
            "compression_threshold": 0.5,
            "retention_period_days": 30,
        },
        "consciousness": {"awareness_threshold": 0.6, "introspection_interval": 300},
        "emotion": {"stagnation_threshold_hours": 1, "volatility_damping": 0.3},
        "symbolic": {
            "glyph_set": ["Λ", "Ψ", "Ω", "Δ", "Σ"],
            "resonance_threshold": 0.7,
        },
    }


@pytest.fixture(autouse=True)
def reset_test_environment():
    """Reset test environment before each test."""
    # Clear any test files
    test_files = Path("tests/test_output")
    if test_files.exists():
        import shutil

        shutil.rmtree(test_files)
    test_files.mkdir(exist_ok=True)

    yield

    # Cleanup after test
    if test_files.exists():
        import shutil

        shutil.rmtree(test_files)


@pytest.fixture
def async_mock():
    """Create an async mock helper."""

    def _async_mock(*args, **kwargs):
        m = Mock(*args, **kwargs)

        async def async_side_effect(*args, **kwargs):
            return m(*args, **kwargs)

        return async_side_effect

    return _async_mock


# Markers for test organization
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "requires_gpu: mark test as requiring GPU")
    config.addinivalue_line(
        "markers", "long_running: mark test as taking significant time"
    )


# Test data generators
@pytest.fixture
def memory_generator():
    """Generate test memory entries."""
    if not HAS_NUMPY:
        pytest.skip("Skipping numpy tests — numpy not installed.")

    def _generate(count=10):
        memories = []
        for i in range(count):
            memories.append(
                {
                    "id": f"mem_{i:04d}",
                    "content": f"Memory content {i} with markers Λ",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "importance_score": np.random.uniform(0.1, 1.0),
                    "fold_eligible": i % 2 == 0,
                    "symbolic_markers": ["Λ"] if i % 3 == 0 else [],
                }
            )
        return memories

    return _generate


# Symbolic state fixtures
@pytest.fixture
def base_symbolic_state():
    """Base symbolic state for testing."""
    return {
        "glyphs": ["Λ", "Ψ", "Ω"],
        "resonance": 0.5,
        "entropy": 0.3,
        "drift_score": 0.15,
        "collapse_threshold": 0.7,
        "coherence": 0.8,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def cognitive_state_factory():
    """Factory for creating cognitive states."""

    def _create_state(
        awareness_level: float = 0.7,
        emotional_valence: float = 0.0,
        cognitive_load: float = 0.5,
        symbolic_density: float = 0.6,
    ):
        return {
            "awareness": awareness_level,
            "emotion": {
                "valence": emotional_valence,
                "arousal": abs(emotional_valence) * 0.8,
                "dominance": 0.5,
            },
            "cognitive": {
                "load": cognitive_load,
                "capacity": 1.0 - cognitive_load,
                "efficiency": 0.8,
            },
            "symbolic": {
                "density": symbolic_density,
                "glyphs": ["Λ"] * int(symbolic_density * 10),
                "resonance": symbolic_density * 0.9,
            },
        }

    return _create_state


@pytest.fixture
def guardian_alert_factory():
    """Factory for creating guardian alerts."""
    if not HAS_NUMPY:
        pytest.skip("Skipping numpy tests — numpy not installed.")

    def _create_alert(
        alert_type: str = "drift", severity: str = "warning", source: str = "test"
    ):
        return {
            "type": alert_type,
            "severity": severity,
            "source": source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "drift_score": 0.8 if alert_type == "drift" else 0.0,
                "collapse_risk": 0.7 if alert_type == "collapse" else 0.0,
                "entropy": np.random.uniform(0.1, 0.9),
                "affected_glyphs": ["Λ", "Ψ"] if alert_type == "drift" else [],
            },
            "recommendations": [
                (
                    "Monitor symbolic state closely"
                    if severity == "warning"
                    else "Immediate intervention required"
                )
            ],
        }

    return _create_alert


@pytest.fixture
def collapse_event_factory():
    """Factory for creating collapse events."""
    if not HAS_NUMPY:
        pytest.skip("Skipping numpy tests — numpy not installed.")

    def _create_event(
        collapsed: bool = True,
        selected_action: str = "default",
        uncertainty_before: float = 0.9,
        uncertainty_after: float = 0.1,
    ):
        return {
            "collapsed": collapsed,
            "selected_action": selected_action if collapsed else None,
            "uncertainty": {
                "before": uncertainty_before,
                "after": uncertainty_after if collapsed else uncertainty_before,
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": np.random.randint(10, 100),
            "quantum_like_state": {
                "superposition": not collapsed,
                "coherence": 0.1 if collapsed else 0.9,
            },
        }

    return _create_event


@pytest.fixture
def mock_symbolic_engine():
    """Mock symbolic engine for dependency injection."""
    engine = Mock()
    engine.generate_glyph.return_value = "Λ"
    engine.calculate_drift.return_value = 0.3
    engine.check_collapse.return_value = {"collapsed": False}
    engine.get_state.return_value = {"glyphs": ["Λ", "Ψ"], "drift": 0.3, "stable": True}
    engine.transform_glyph = Mock(
        side_effect=lambda g, t: g if t == "identity" else "Ω"
    )
    return engine


@pytest.fixture
def drift_scenario_factory():
    """Factory for creating drift test scenarios."""

    def _create_scenario(scenario_type: str = "stable"):
        scenarios = {
            "stable": {
                "states": [
                    {"glyphs": ["Λ"], "resonance": 0.5, "entropy": 0.3},
                    {"glyphs": ["Λ"], "resonance": 0.51, "entropy": 0.31},
                    {"glyphs": ["Λ"], "resonance": 0.49, "entropy": 0.29},
                ],
                "expected_drift": "low",
                "expected_phase": "EARLY",
            },
            "drifting": {
                "states": [
                    {"glyphs": ["Λ"], "resonance": 0.3, "entropy": 0.2},
                    {"glyphs": ["Ψ"], "resonance": 0.5, "entropy": 0.4},
                    {"glyphs": ["Ω"], "resonance": 0.7, "entropy": 0.6},
                ],
                "expected_drift": "medium",
                "expected_phase": "MIDDLE",
            },
            "chaotic": {
                "states": [
                    {"glyphs": ["Λ", "Ψ", "Ω"], "resonance": 0.1, "entropy": 0.9},
                    {"glyphs": ["Δ"], "resonance": 0.9, "entropy": 0.1},
                    {"glyphs": ["Σ", "Φ", "Θ"], "resonance": 0.5, "entropy": 0.5},
                ],
                "expected_drift": "high",
                "expected_phase": "CASCADE",
            },
        }
        return scenarios.get(scenario_type, scenarios["stable"])

    return _create_scenario


@pytest.fixture
def quantum_like_state_factory():
    """Factory for creating quantum-like superposition states."""
    if not HAS_NUMPY:
        pytest.skip("Skipping numpy tests — numpy not installed.")

    def _create_state(
        num_possibilities: int = 3, uncertainty: float = 0.5, coherence: float = 0.8
    ):
        # Generate possibilities with random probabilities
        possibilities = []
        remaining_prob = 1.0

        for i in range(num_possibilities):
            if i == num_possibilities - 1:
                prob = remaining_prob
            else:
                prob = np.random.uniform(0, remaining_prob)
                remaining_prob -= prob

            possibilities.append(
                {
                    "action": f"action_{i}",
                    "probability": prob,
                    "metadata": {
                        "cost": np.random.uniform(1, 100),
                        "risk": np.random.uniform(0, 1),
                    },
                }
            )

        return {
            "possibilities": possibilities,
            "uncertainty": uncertainty,
            "coherence": coherence,
            "entanglement": np.random.uniform(0, 1),
            "decoherence_rate": np.random.uniform(0.01, 0.1),
        }

    return _create_state
