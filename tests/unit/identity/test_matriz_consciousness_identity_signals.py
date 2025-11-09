# owner: Jules-02
# tier: tier1
# module_uid: candidate.core.identity.matriz_consciousness_identity_signals
# criticality: P0

import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import pytest

# Add the project root to the path to allow for absolute imports
project_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(project_root))

from core.identity.matriz_consciousness_identity_signals import (
    ConsciousnessIdentitySignalProcessor,
    CorrelationMatrix,
    IdentitySignalType,
    ProcessedBatch,
    ValidationResult,
)


# Mock ConsciousnessSignal for testing purposes
@dataclass
class MockBioSymbolicData:
    coherence_score: float = 0.5

@dataclass
class MockConsciousnessSignal:
    consciousness_id: str
    signal_id: str = "test_signal_id"
    created_timestamp: float = field(default_factory=time.time)
    processing_hints: dict = field(default_factory=dict)
    awareness_level: float = 0.5
    reflection_depth: float = 0.5
    bio_symbolic_data: MockBioSymbolicData = field(default_factory=MockBioSymbolicData)

# Patch the ConsciousnessSignal in the module with our mock

candidate.core.identity.matriz_consciousness_identity_signals.ConsciousnessSignal = MockConsciousnessSignal  # TODO: candidate


class TestConsciousnessIdentitySignalProcessor:
    def setup_method(self):
        self.processor = ConsciousnessIdentitySignalProcessor()

    def test_process_signal_batch_valid_signals(self):
        # Arrange
        signals = [
            MockConsciousnessSignal(consciousness_id="id1"),
            MockConsciousnessSignal(consciousness_id="id2"),
            MockConsciousnessSignal(consciousness_id="id1"),
        ]

        # Act
        result = self.processor.process_signal_batch(signals)

        # Assert
        assert isinstance(result, ProcessedBatch)
        assert len(result.signals_by_identity["id1"]) == 2
        assert len(result.signals_by_identity["id2"]) == 1
        assert not result.invalid_signals
        assert result.trace_info['data']['status'] == 'SUCCESS'

    def test_process_signal_batch_invalid_signals(self):
        # Arrange
        signals = ["not a signal", object()]

        # Act
        result = self.processor.process_signal_batch(signals)

        # Assert
        assert not result.signals_by_identity
        assert len(result.invalid_signals) == 2
        assert result.invalid_signals[0][1] == "Not a ConsciousnessSignal instance"

    def test_process_signal_batch_empty_list(self):
        # Arrange
        signals = []

        # Act
        result = self.processor.process_signal_batch(signals)

        # Assert
        assert not result.signals_by_identity
        assert not result.invalid_signals
        assert result.trace_info['data']['num_signals'] == 0

    def test_validate_identity_coherence_success(self):
        # Arrange
        request_signal = MockConsciousnessSignal(
            consciousness_id="id1",
            created_timestamp=time.time() - 10,
            processing_hints={"identity_signal_type": IdentitySignalType.AUTHENTICATION_REQUEST.value},
        )
        success_signal = MockConsciousnessSignal(
            consciousness_id="id1",
            processing_hints={"identity_signal_type": IdentitySignalType.AUTHENTICATION_SUCCESS.value},
        )
        context = {"recent_signals": [request_signal]}

        # Act
        result = self.processor.validate_identity_coherence(success_signal, context)

        # Assert
        assert isinstance(result, ValidationResult)
        assert result.is_coherent
        assert result.trace_info['data']['status'] == 'SUCCESS'

    def test_validate_identity_coherence_failure_no_request(self):
        # Arrange
        success_signal = MockConsciousnessSignal(
            consciousness_id="id1",
            processing_hints={"identity_signal_type": IdentitySignalType.AUTHENTICATION_SUCCESS.value},
        )
        context = {"recent_signals": []}

        # Act
        result = self.processor.validate_identity_coherence(success_signal, context)

        # Assert
        assert not result.is_coherent
        assert "without a recent AUTHENTICATION_REQUEST" in result.reason
        assert result.trace_info['data']['status'] == 'FAILURE'

    def test_validate_identity_coherence_anomaly_detection(self):
        # Arrange
        failures = [
            MockConsciousnessSignal(
                consciousness_id="id1",
                processing_hints={"identity_signal_type": IdentitySignalType.AUTHENTICATION_FAILURE.value}
            ) for _ in range(6)
        ]
        context = {"recent_signals": failures}

        # Act
        result = self.processor.validate_identity_coherence(failures[0], context)

        # Assert
        assert not result.is_coherent
        assert "consecutive authentication failures" in result.reason
        assert result.trace_info['data']['check'] == 'anomaly_detection'

    def test_correlate_consciousness_state(self):
        # Arrange
        signals = [
            MockConsciousnessSignal(
                consciousness_id="id1",
                processing_hints={"identity_signal_type": "TYPE_A"},
                awareness_level=0.8,
                reflection_depth=0.7,
                bio_symbolic_data=MockBioSymbolicData(coherence_score=0.9)
            ),
            MockConsciousnessSignal(
                consciousness_id="id1",
                processing_hints={"identity_signal_type": "TYPE_A"},
                awareness_level=0.6,
                reflection_depth=0.5,
                bio_symbolic_data=MockBioSymbolicData(coherence_score=0.7)
            ),
            MockConsciousnessSignal(
                consciousness_id="id2",
                processing_hints={"identity_signal_type": "TYPE_B"},
                awareness_level=0.4,
                reflection_depth=0.3,
                bio_symbolic_data=MockBioSymbolicData(coherence_score=0.5)
            ),
        ]

        # Act
        result = self.processor.correlate_consciousness_state(signals)

        # Assert
        assert isinstance(result, CorrelationMatrix)
        assert "TYPE_A" in result.matrix
        assert "TYPE_B" in result.matrix
        assert pytest.approx(result.matrix["TYPE_A"]["awareness_level"]) == 0.7
        assert pytest.approx(result.matrix["TYPE_A"]["reflection_depth"]) == 0.6
        assert pytest.approx(result.matrix["TYPE_A"]["coherence_score"]) == 0.8
        assert pytest.approx(result.matrix["TYPE_B"]["awareness_level"]) == 0.4
        assert result.trace_info['data']['status'] == 'SUCCESS'

    def test_correlate_consciousness_state_empty_list(self):
        # Arrange
        signals = []

        # Act
        result = self.processor.correlate_consciousness_state(signals)

        # Assert
        assert not result.matrix
        assert result.trace_info['data']['num_signals'] == 0
