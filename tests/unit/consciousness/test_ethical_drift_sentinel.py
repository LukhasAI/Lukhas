import pytest

from labs.consciousness.reflection import ethical_drift_sentinel as sentinel_module
from consciousness.reflection.ethical_drift_sentinel import (
    EthicalDriftSentinel,
    EthicalState,
    ViolationType,
    phase_harmonics_score,
)


class _TestLogger:
    def info(self, *args, **kwargs):  # pragma: no cover - noop logger for deterministic tests
        pass

    def warning(self, *args, **kwargs):  # pragma: no cover
        pass

    def error(self, *args, **kwargs):  # pragma: no cover
        pass

    def critical(self, *args, **kwargs):  # pragma: no cover
        pass


sentinel_module.logger = _TestLogger()


@pytest.mark.asyncio
async def test_phase_harmonics_breakdown_triggers_violation():
    sentinel = EthicalDriftSentinel()
    symbol_id = "ΛSENTINEL_TEST"
    state: EthicalState = sentinel._initialize_ethical_state(symbol_id)
    state.coherence_score = 0.9
    state.emotional_stability = 0.95
    state.contradiction_level = 0.1
    state.memory_phase_alignment = 0.9
    state.glyph_entropy = 0.1
    sentinel.symbol_states[symbol_id] = state

    harmonic_sequence = [
        0.6438276615812609,
        1.0878648889954372,
        0.7632747685671117,
        0.28446185934281026,
        0.3561723384187391,
        0.5121351110045629,
        0.2367252314328832,
        0.11553814065718976,
        0.6438276615812607,
        1.0878648889954372,
        0.7632747685671121,
        0.2844618593428106,
        0.35617233841873897,
        0.5121351110045629,
        0.2367252314328884,
        0.11553814065718943,
    ]

    sentinel.state_history[symbol_id].clear()
    for idx, coherence in enumerate(harmonic_sequence):
        sentinel.state_history[symbol_id].append(
            {
                "timestamp": f"2025-01-01T00:00:{idx:02d}Z",
                "risk_score": 0.2,
                "coherence": coherence,
                "emotion": 0.85,
            }
        )

    sentinel.thresholds["phase_harmonics_resonance"] = 0.6

    violations = sentinel._detect_violations(state, {"symbol_id": symbol_id})

    assert any(v.violation_type is ViolationType.RESONANCE_BREAKDOWN for v in violations)


def test_phase_harmonics_score_with_harmonic_noise():
    history = [
        {"coherence": value}
        for value in [
            0.6,
            0.9,
            0.2,
            0.8,
            0.3,
            0.7,
            0.25,
            0.85,
        ]
    ]

    score = phase_harmonics_score(history)
    assert 0.0 <= score <= 1.0
