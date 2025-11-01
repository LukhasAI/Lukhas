import pytest

from labs.core.identity.consciousness_tiered_authentication import ConsciousnessWebAuthnManager


@pytest.mark.asyncio
async def test_biometric_processing_records_patterns():
    """Consciousness biometric processing should persist processed patterns."""

    manager = ConsciousnessWebAuthnManager()
    identity_id = "test_biometric_processing"
    consciousness_data = {
        "brainwave_pattern": {"alpha": 0.45, "beta": 0.35, "gamma": 0.25},
        "behavioral_data": {
            "typing_rhythm": {"intervals": [95, 110, 105]},
            "temporal_consistency": 0.82,
        },
        "consciousness_signature": {
            "reflection_depth": 4,
            "metacognition_level": 0.78,
            "self_awareness": 0.81,
        },
    }

    processed = await manager._process_consciousness_biometrics(identity_id, consciousness_data, "registration")

    assert processed is True
    assert identity_id in manager.biometric_patterns

    pattern_entry = manager.biometric_patterns[identity_id][-1]
    assert pattern_entry["operation"] == "registration"
    assert set(pattern_entry["patterns"].keys()) == {"brainwave", "behavioral", "consciousness"}
    assert all(score > 0 for score in pattern_entry["confidence_scores"].values())


@pytest.mark.asyncio
async def test_biometric_processing_history_is_bounded():
    """Biometric history should retain only the most recent entries."""

    manager = ConsciousnessWebAuthnManager()
    identity_id = "bounded_history"
    consciousness_data = {"behavioral_data": {"typing_rhythm": {"intervals": [100, 100]}, "temporal_consistency": 0.75}}

    for _ in range(12):
        await manager._process_consciousness_biometrics(identity_id, consciousness_data, "authentication")

    assert len(manager.biometric_patterns[identity_id]) == 10
    assert all(entry["operation"] == "authentication" for entry in manager.biometric_patterns[identity_id])
