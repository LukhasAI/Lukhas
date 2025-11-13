import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from core.bio_symbolic_processor import (
    AdaptationRule,
    BioPatternType,
    BioSymbolicPattern,
    BioSymbolicProcessor,
    SymbolicRepresentationType,
    create_bio_symbolic_processor,
    get_bio_symbolic_processor,
)
from core.matriz_consciousness_signals import (
    BioSymbolicData,
    ConsciousnessSignal,
    ConsciousnessSignalFactory,
    ConsciousnessSignalType,
)


# Basic test structure
class TestBioSymbolicProcessor:
    def test_initialization(self):
        processor = BioSymbolicProcessor()
        assert isinstance(processor.patterns, dict)
        assert len(processor.patterns) == 0
        assert isinstance(processor.adaptation_rules, list)
        assert len(processor.adaptation_rules) == 3
        assert all(isinstance(rule, AdaptationRule) for rule in processor.adaptation_rules)
        assert isinstance(processor.processing_cache, dict)
        assert len(processor.processing_cache) == 0
        assert processor.coherence_threshold == 0.7
        assert processor.adaptation_learning_rate == 0.01
        assert processor.entropy_window_size == 100
        assert isinstance(processor.resonance_database, dict)
        assert len(processor.resonance_database) == 0

        expected_stats = {
            "signals_processed": 0,
            "adaptations_applied": 0,
            "patterns_evolved": 0,
            "coherence_violations": 0,
            "processing_time_ms": [],
        }
        assert processor.processing_stats == expected_stats

    def test_create_default_bio_symbolic_data(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.AWARENESS,
            awareness_level=0.8
        )

        bio_data = processor._create_default_bio_symbolic_data(signal)

        assert isinstance(bio_data, BioSymbolicData)
        assert bio_data.pattern_type == "sensory_awareness"
        assert bio_data.oscillation_frequency == 10.0 + 0.8 * 30
        assert bio_data.coherence_score == 0.8 * 0.8
        assert bio_data.adaptation_vector == {"awareness": 0.8}
        assert bio_data.entropy_delta == 0.0
        assert bio_data.resonance_patterns == ["sensory_awareness"]
        assert bio_data.membrane_permeability == 0.7
        assert bio_data.temporal_decay == 0.9

    def test_extract_bio_patterns(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignal(signal_id="test_signal", awareness_level=0.6)
        bio_data = BioSymbolicData(
            pattern_type="test_pattern",
            oscillation_frequency=25.0,
            coherence_score=0.8,
            adaptation_vector={"test": 0.5},
            entropy_delta=0.1,
            resonance_patterns=["test"],
            membrane_permeability=0.6,
            temporal_decay=0.95,
        )

        patterns = processor._extract_bio_patterns(signal, bio_data)

        assert len(patterns) == 3

        # Neural oscillation pattern
        neural_pattern = next(p for p in patterns if p.bio_pattern_type == BioPatternType.NEURAL_OSCILLATION)
        assert neural_pattern.pattern_id == "neural_osc_test_signal"
        assert neural_pattern.frequency_components == [25.0]
        assert neural_pattern.amplitude_envelope == [0.6]

        # Membrane dynamics pattern
        membrane_pattern = next(p for p in patterns if p.bio_pattern_type == BioPatternType.MEMBRANE_DYNAMICS)
        assert membrane_pattern.pattern_id == "membrane_dyn_test_signal"
        assert membrane_pattern.amplitude_envelope == [0.6]

        # Metabolic flow pattern
        metabolic_pattern = next(p for p in patterns if p.bio_pattern_type == BioPatternType.METABOLIC_FLOW)
        assert metabolic_pattern.pattern_id == "metabolic_test_signal"
        assert metabolic_pattern.amplitude_envelope == [1.0 - 0.95]

    def test_apply_symbolic_representations(self):
        processor = BioSymbolicProcessor()
        patterns = [
            BioSymbolicPattern(
                pattern_id="p1",
                bio_pattern_type=BioPatternType.NEURAL_OSCILLATION,
                symbolic_representation=SymbolicRepresentationType.VECTOR_SPACE,
                frequency_components=[10.0, 20.0],
                amplitude_envelope=[0.5, 0.8],
                phase_relationships={}, coherence_matrix=[], entropy_measures={},
                adaptation_coefficients={}, temporal_evolution=[], resonance_fingerprint=""
            ),
            BioSymbolicPattern(
                pattern_id="p2",
                bio_pattern_type=BioPatternType.METABOLIC_FLOW,
                symbolic_representation=SymbolicRepresentationType.GRAPH_TOPOLOGY,
                frequency_components=[], amplitude_envelope=[], phase_relationships={},
                coherence_matrix=[], entropy_measures={},
                adaptation_coefficients={"a": 0.1, "b": 0.2},
                temporal_evolution=[], resonance_fingerprint=""
            ),
            BioSymbolicPattern(
                pattern_id="p3",
                bio_pattern_type=BioPatternType.MEMBRANE_DYNAMICS,
                symbolic_representation=SymbolicRepresentationType.GEOMETRIC_MANIFOLD,
                frequency_components=[], amplitude_envelope=[], phase_relationships={},
                coherence_matrix=[[1.0, 0.5], [0.5, 1.0]],
                entropy_measures={}, adaptation_coefficients={},
                temporal_evolution=[], resonance_fingerprint=""
            )
        ]

        symbolic_data = processor._apply_symbolic_representations(patterns)

        assert "vector_p1" in symbolic_data
        assert symbolic_data["vector_p1"]["type"] == "vector_space"
        assert symbolic_data["vector_p1"]["dimension"] == 4

        assert "graph_p2" in symbolic_data
        assert symbolic_data["graph_p2"]["type"] == "graph_topology"
        assert symbolic_data["graph_p2"]["node_count"] == 2

        assert "manifold_p3" in symbolic_data
        assert symbolic_data["manifold_p3"]["type"] == "geometric_manifold"
        assert "curvature" in symbolic_data["manifold_p3"]

    def test_calculate_manifold_curvature(self):
        processor = BioSymbolicProcessor()

        # Low variance -> low curvature
        matrix1 = [[0.8, 0.8], [0.8, 0.8]]
        curvature1 = processor._calculate_manifold_curvature(matrix1)
        assert curvature1 == 0.0

        # High variance -> high curvature
        matrix2 = [[1.0, 0.0], [0.0, 1.0]]
        curvature2 = processor._calculate_manifold_curvature(matrix2)
        assert curvature2 > 0.5

        # Empty matrix -> zero curvature
        matrix3 = []
        curvature3 = processor._calculate_manifold_curvature(matrix3)
        assert curvature3 == 0.0

    def test_check_adaptation_triggers(self):
        processor = BioSymbolicProcessor()
        rule = processor.adaptation_rules[0]  # neural_osc_to_plasticity

        # Triggering signal and bio_data
        signal = ConsciousnessSignal(awareness_level=0.7)
        bio_data = BioSymbolicData(
            pattern_type="", oscillation_frequency=15.0, coherence_score=0.7,
            adaptation_vector={}, entropy_delta=0.0, resonance_patterns=[],
            membrane_permeability=0.0, temporal_decay=0.0
        )
        assert processor._check_adaptation_triggers(rule, bio_data, signal)

        # Non-triggering (frequency too low)
        bio_data.oscillation_frequency = 5.0
        assert not processor._check_adaptation_triggers(rule, bio_data, signal)

        # Non-triggering (coherence too low)
        bio_data.oscillation_frequency = 15.0
        bio_data.coherence_score = 0.5
        assert not processor._check_adaptation_triggers(rule, bio_data, signal)

    def test_apply_single_adaptation(self):
        processor = BioSymbolicProcessor()
        rule = processor.adaptation_rules[0]
        bio_data = BioSymbolicData(
            pattern_type="test", oscillation_frequency=20.0, coherence_score=0.7,
            adaptation_vector={}, entropy_delta=0.0, resonance_patterns=[],
            membrane_permeability=0.5, temporal_decay=0.9
        )

        adapted_data = processor._apply_single_adaptation(rule, bio_data, {})

        assert adapted_data.oscillation_frequency > bio_data.oscillation_frequency
        assert adapted_data.coherence_score > bio_data.coherence_score
        assert "synaptic_plasticity" in adapted_data.adaptation_vector

    def test_apply_adaptations(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignal(awareness_level=0.9)
        bio_data = BioSymbolicData(
            pattern_type="test", oscillation_frequency=30.0, coherence_score=0.8,
            adaptation_vector={}, entropy_delta=0.1, resonance_patterns=[],
            membrane_permeability=0.5, temporal_decay=0.4
        )

        # Mock to ensure triggers are checked
        with patch.object(processor, '_check_adaptation_triggers', return_value=True) as mock_check:
            adapted_data = processor._apply_adaptations(bio_data, {}, signal)
            assert mock_check.call_count == len(processor.adaptation_rules)

        assert adapted_data.oscillation_frequency != bio_data.oscillation_frequency
        assert "adaptations_applied" in adapted_data.adaptation_vector

    def test_process_consciousness_signal_success(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignalFactory.create_awareness_signal(
            consciousness_id="test_consciousness",
            producer_module="test_module",
            awareness_level=0.8,
            sensory_inputs={"vision": 0.7, "audio": 0.6}
        )

        processed_data = processor.process_consciousness_signal(signal)

        assert isinstance(processed_data, BioSymbolicData)
        assert processed_data.coherence_score > signal.bio_symbolic_data.coherence_score
        assert processor.processing_stats["signals_processed"] == 1
        assert len(processor.processing_stats["processing_time_ms"]) == 1

    def test_process_consciousness_signal_no_bio_data(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignal(
            awareness_level=0.5,
            signal_type=ConsciousnessSignalType.TRINITY_SYNC
        )

        processed_data = processor.process_consciousness_signal(signal)

        assert isinstance(processed_data, BioSymbolicData)
        assert processed_data.pattern_type == "generic_consciousness"
        assert processor.processing_stats["signals_processed"] == 1

    def test_process_consciousness_signal_error_handling(self):
        processor = BioSymbolicProcessor()
        signal = ConsciousnessSignal(awareness_level=0.5)

        with patch.object(processor, '_extract_bio_patterns', side_effect=Exception("Test error")):
            processed_data = processor.process_consciousness_signal(signal)

        assert processed_data is not None
        assert processor.processing_stats["coherence_violations"] == 1

@pytest.mark.asyncio
async def test_process_signal_batch():
    processor = BioSymbolicProcessor()
    signals = [
        ConsciousnessSignalFactory.create_awareness_signal("c1", "p1", 0.7),
        ConsciousnessSignalFactory.create_reflection_signal("c2", "p2", 3),
        ConsciousnessSignal(signal_id="error_signal") # Signal that might cause an error
    ]

    with patch.object(processor, 'process_consciousness_signal', wraps=processor.process_consciousness_signal) as mock_process:
        results = await processor.process_signal_batch(signals)

        assert len(results) == 3
        assert all(isinstance(r, BioSymbolicData) for r in results)
        assert mock_process.call_count == 3

        # Test error handling in batch
        mock_process.side_effect = [
            processor.process_consciousness_signal(signals[0]),
            Exception("Batch error"),
            processor.process_consciousness_signal(signals[2])
        ]
        results_with_error = await processor.process_signal_batch(signals)
        assert len(results_with_error) == 3
        assert isinstance(results_with_error[1], BioSymbolicData) # Fallback data

class TestUtilityMethods:
    def test_get_processing_statistics(self):
        processor = BioSymbolicProcessor()
        processor.processing_stats["signals_processed"] = 100
        processor.processing_stats["adaptations_applied"] = 50
        processor.processing_stats["coherence_violations"] = 10
        processor.processing_stats["processing_time_ms"] = [10, 20, 30]

        stats = processor.get_processing_statistics()

        assert stats["signals_processed"] == 100
        assert stats["adaptation_rate"] == 0.5
        assert stats["coherence_violation_rate"] == 0.1
        assert stats["avg_processing_time_ms"] == 20
        assert stats["max_processing_time_ms"] == 30

    def test_evolve_adaptation_rules(self):
        processor = BioSymbolicProcessor()
        original_strength = processor.adaptation_rules[0].adaptation_strength
        original_lr = processor.adaptation_rules[0].learning_rate

        processor.evolve_adaptation_rules()

        assert processor.adaptation_rules[0].adaptation_strength < original_strength
        assert processor.adaptation_rules[0].learning_rate < original_lr
        assert processor.processing_stats["patterns_evolved"] > 0

def test_create_bio_symbolic_processor():
    processor = create_bio_symbolic_processor()
    assert isinstance(processor, BioSymbolicProcessor)

def test_get_bio_symbolic_processor():
    processor1 = get_bio_symbolic_processor()
    processor2 = get_bio_symbolic_processor()
    assert processor1 is processor2
    assert isinstance(processor1, BioSymbolicProcessor)

@pytest.mark.parametrize("signal_type", list(ConsciousnessSignalType))
def test_create_default_bio_symbolic_data_all_types(signal_type):
    processor = BioSymbolicProcessor()
    signal = ConsciousnessSignal(
        signal_type=signal_type,
        awareness_level=0.6
    )

    bio_data = processor._create_default_bio_symbolic_data(signal)

    assert isinstance(bio_data, BioSymbolicData)
    assert bio_data.oscillation_frequency == 10.0 + 0.6 * 30
    assert bio_data.coherence_score == 0.6 * 0.8
    assert bio_data.adaptation_vector == {"awareness": 0.6}
    assert bio_data.entropy_delta == 0.0
    assert isinstance(bio_data.resonance_patterns, list)
