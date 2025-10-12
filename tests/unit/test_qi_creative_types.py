import numpy as np
import pytest

try:
    from products.content.poetica.creativity_engines.qi_creative_types import (
        CognitiveState,
        CreativeQuantumLikeState,
        EnhancedCreativeState,
        NeuroHaikuGenerator,
        QuantumHaiku,
    )
except Exception as exc:  # pragma: no cover - skip when quantum stack unavailable
    pytest.skip(f"Quantum creative types unavailable: {exc}", allow_module_level=True)


@pytest.mark.asyncio
async def test_neuro_haiku_generator_returns_quantum_haiku() -> None:
    generator = NeuroHaikuGenerator()
    await generator.initialize()

    result = await generator.process("consciousness")

    assert isinstance(result, QuantumHaiku)
    assert result.modality == "haiku"
    assert len(result.lines) == 3


def test_enhanced_creative_state_accepts_quantum_state() -> None:
    state = CreativeQuantumLikeState(
        amplitude_vector=np.ones(3, dtype=np.complex128),
        entanglement_map={"alpha": 0.5},
        coherence_time=1.2,
        cultural_resonance={"global": 0.8},
        emotional_spectrum=np.ones(3),
    )
    cognitive = CognitiveState(
        attention_focus=0.7,
        working_memory_load=0.4,
        emotional_valence=0.6,
        arousal_level=0.5,
        neurotransmitter_levels={"dopamine": 0.7},
        neural_oscillations={"gamma": 0.3},
    )

    enhanced = EnhancedCreativeState(
        base_state=state,
        cognitive_enhancement=cognitive,
        synaptic_plasticity=0.9,
        creative_flow_intensity=0.8,
        inspiration_sources=["dream", "lukhas.memory"],
    )

    assert enhanced.base_state is state
    assert enhanced.cognitive_enhancement.attention_focus == pytest.approx(0.7)
