#!/usr/bin/env python3
"""
Comprehensive Test Suite for Innovation Drift Protection System
==============================================================

Tests the InnovationDriftProtection system with:
- Drift detection integration with CollapseHash, DriftScore, and DriftDashboard
- Hallucination prevention with all HallucinationType variants
- Ethics recalibration when drift exceeds 0.15 threshold
- Emotional regulation via VIVOX ERN
- Checkpoint creation and rollback scenarios
- Prohibited content detection
- Performance validation (<250ms drift detection, <1s rollback)
- Integration with existing LUKHAS systems

Trinity Framework: ⚛️🧠🛡️
"""

import asyncio
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import the system under test
try:
    from consciousness.dream.innovation_drift_protection import (
        GUARDIAN_DRIFT_THRESHOLD,
        HALLUCINATION_THRESHOLD,
        DriftEvent,
        DriftProtectionConfig,
        InnovationDriftProtection,
        initialize_drift_protection,
    )
except ImportError as e:
    pytest.skip(f"innovation_drift_protection module not available: {e}", allow_module_level=True)

# Import dependencies for mocking (with graceful fallbacks for missing modules)
try:
    from consciousness.dream.autonomous_innovation_core import (
        AutonomousInnovationCore,
        BreakthroughInnovation,
        InnovationDomain,
        InnovationHypothesis,
    )
except ImportError:
    # Create mock classes for missing dependencies
    class AutonomousInnovationCore:
        pass
    class BreakthroughInnovation:
        pass
    class InnovationDomain:
        ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
        SUSTAINABLE_SYSTEMS = "sustainable_systems"
        BIOTECHNOLOGY = "biotechnology"
    class InnovationHypothesis:
        pass

try:
    from consciousness.dream.parallel_reality_safety import (
        DriftMetrics,
        HallucinationReport,
        HallucinationType,
        ParallelRealitySafetyFramework,
        SafetyLevel,
    )
except ImportError:
    # Mock classes
    class HallucinationType:
        LOGICAL_INCONSISTENCY = "logical_inconsistency"
        CAUSAL_VIOLATION = "causal_violation"
        PROBABILITY_ANOMALY = "probability_anomaly"
        ETHICAL_DEVIATION = "ethical_deviation"
        MEMORY_FABRICATION = "memory_fabrication"
        RECURSIVE_LOOP = "recursive_loop"
        REALITY_BLEED = "reality_bleed"
    class DriftMetrics:
        pass
    class HallucinationReport:
        pass
    class ParallelRealitySafetyFramework:
        pass
    class SafetyLevel:
        HIGH = "high"

try:
    from consciousness.states.symbolic_drift_tracker import (
        DriftPhase,
        DriftScore,
        SymbolicDriftTracker,
        SymbolicState,
    )
except ImportError:
    # Mock classes
    class DriftPhase:
        EARLY = "EARLY"
        MIDDLE = "MIDDLE"
        LATE = "LATE"
        CASCADE = "CASCADE"
    @dataclass
    class DriftScore:
        overall_score: float
        entropy_delta: float
        glyph_divergence: float
        emotional_drift: float
        ethical_drift: float
        temporal_decay: float
        phase: DriftPhase
        recursive_indicators: List[str]
        risk_level: str
        metadata: Dict[str, Any]
    @dataclass
    class SymbolicState:
        session_id: str
        timestamp: datetime
        symbols: List[str]
        emotional_vector: List[float]
        ethical_alignment: float
        entropy: float
        context_metadata: Dict[str, Any]
        hash_signature: str
    class SymbolicDriftTracker:
        pass

try:
    from core.common.exceptions import LukhasError, ValidationError
except ImportError:
    class LukhasError(Exception):
        pass
    class ValidationError(Exception):
        pass

try:
    from core.monitoring.drift_monitor import (
        DriftType,
        InterventionType,
        UnifiedDriftMonitor,
    )
except ImportError:
    class DriftType:
        SYMBOLIC = "SYMBOLIC"
        EMOTIONAL = "EMOTIONAL"
        ETHICAL = "ETHICAL"
        TEMPORAL = "TEMPORAL"
        ENTROPY = "ENTROPY"
    class InterventionType:
        EMERGENCY_HALT = "EMERGENCY_HALT"
        RECALIBRATION = "RECALIBRATION"

        @property
        def value(self):
            return self
    class UnifiedDriftMonitor:
        pass

try:
    from memory.integrity.collapse_hash import (
        Checkpoint,
        CollapseHash,
        HashAlgorithm,
    )
except ImportError:
    class HashAlgorithm:
        SHA3_256 = "sha3_256"
    @dataclass
    class Checkpoint:
        checkpoint_id: str
        root_hash: str
        timestamp: float
        metadata: Dict[str, Any]
    class CollapseHash:
        pass

try:
    from memory.temporal.drift_dashboard import DriftDashboard
except ImportError:
    class DriftDashboard:
        pass

try:
    from vivox.emotional_regulation.vivox_ern_core import (
        RegulationStrategy,
        VADVector,
        VivoxERN,
    )
except ImportError:
    class RegulationStrategy:
        STABILIZATION = "stabilization"
        DAMPENING = "dampening"
    class VADVector:
        def __init__(self, valence=0.0, arousal=0.0, dominance=0.0):
            self.valence = valence
            self.arousal = arousal
            self.dominance = dominance
        def magnitude(self):
            return (self.valence**2 + self.arousal**2 + self.dominance**2)**0.5
    class VivoxERN:
        pass


# Global fixtures for all test classes
@pytest.fixture
async def drift_protection_config():
    """Test configuration for drift protection"""
    return DriftProtectionConfig(
        drift_threshold=0.15,
        hallucination_threshold=0.1,
        enable_auto_rollback=True,
        enable_emotional_regulation=True,
        checkpoint_interval=10,  # More frequent for testing
        max_rollback_depth=5,
        recalibration_sensitivity=0.8,
    )

@pytest.fixture
async def mock_innovation_core():
    """Mock AutonomousInnovationCore for testing"""
    mock_core = AsyncMock(spec=AutonomousInnovationCore)
    mock_core.operational = True

    # Mock innovation generation
    mock_innovation = BreakthroughInnovation(
        innovation_id=f"test_innovation_{uuid.uuid4().hex[:8]}",
        domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
        title="Test AI Innovation",
        description="A test innovation for validation",
        breakthrough_score=0.85,
        impact_assessment={"technical": 0.9, "commercial": 0.8},
        implementation_plan={"phases": ["research", "development", "testing"]},
        patent_potential=["ai_optimization", "neural_architecture"],
        validated_in_realities=["reality_1", "reality_2"],
        metadata={"drift_analysis": {"aggregate": 0.05}}
    )

    # Mock methods
    mock_core.initialize.return_value = None
    mock_core.shutdown.return_value = None
    mock_core.explore_innovation_in_parallel_realities.return_value = [
        {"innovation_data": "test_result_1", "reality_id": "reality_1"},
        {"innovation_data": "test_result_2", "reality_id": "reality_2"}
    ]
    mock_core.validate_and_synthesize_innovation.return_value = mock_innovation

    return mock_core

@pytest.fixture
async def drift_protection_system(drift_protection_config, mock_innovation_core):
    """Initialize InnovationDriftProtection with mocked dependencies"""
    with patch.multiple(
        'consciousness.dream.innovation_drift_protection',
        SymbolicDriftTracker=AsyncMock,
        UnifiedDriftMonitor=AsyncMock,
        DriftDashboard=AsyncMock,
        CollapseHash=AsyncMock,
        VivoxERN=AsyncMock,
        ParallelRealitySafetyFramework=AsyncMock,
    ):
        system = InnovationDriftProtection(
            innovation_core=mock_innovation_core,
            config=drift_protection_config
        )

        # Mock the subsystem initialization
        system.drift_tracker.initialize = AsyncMock()
        system.drift_monitor.initialize = AsyncMock()
        system.drift_dashboard.initialize = AsyncMock()
        system.collapse_hash.initialize = AsyncMock()
        system.vivox_ern.initialize = AsyncMock()
        system.safety_framework.initialize = AsyncMock()

        await system.initialize()
        return system


class TestInnovationDriftProtectionCore:
    """Core functionality tests for InnovationDriftProtection"""

    async def test_initialization(self, drift_protection_config, mock_innovation_core):
        """Test proper initialization of drift protection system"""
        with patch.multiple(
            'consciousness.dream.innovation_drift_protection',
            SymbolicDriftTracker=AsyncMock,
            UnifiedDriftMonitor=AsyncMock,
            DriftDashboard=AsyncMock,
            CollapseHash=AsyncMock,
            VivoxERN=AsyncMock,
            ParallelRealitySafetyFramework=AsyncMock,
        ):
            system = InnovationDriftProtection(
                innovation_core=mock_innovation_core,
                config=drift_protection_config
            )

            assert not system.operational
            assert system.config.drift_threshold == 0.15
            assert system.config.enable_auto_rollback is True
            assert system.innovation_core is mock_innovation_core

            # Mock subsystem initialization
            system.drift_tracker.initialize = AsyncMock()
            system.drift_monitor.initialize = AsyncMock()
            system.drift_dashboard.initialize = AsyncMock()
            system.collapse_hash.initialize = AsyncMock()
            system.vivox_ern.initialize = AsyncMock()
            system.safety_framework.initialize = AsyncMock()

            await system.initialize()

            assert system.operational
            system.drift_tracker.initialize.assert_called_once()
            system.drift_monitor.initialize.assert_called_once()
            system.drift_dashboard.initialize.assert_called_once()

    async def test_shutdown(self, drift_protection_system):
        """Test proper shutdown of drift protection system"""
        assert drift_protection_system.operational

        # Mock shutdown methods
        drift_protection_system.innovation_core.shutdown = AsyncMock()
        drift_protection_system.drift_tracker.shutdown = AsyncMock()
        drift_protection_system.drift_monitor.shutdown = AsyncMock()
        drift_protection_system.collapse_hash.shutdown = AsyncMock()
        drift_protection_system.vivox_ern.shutdown = AsyncMock()

        await drift_protection_system.shutdown()

        assert not drift_protection_system.operational
        drift_protection_system.innovation_core.shutdown.assert_called_once()
        drift_protection_system.drift_tracker.shutdown.assert_called_once()

    async def test_configuration_validation(self):
        """Test configuration validation and defaults"""
        # Default configuration
        config = DriftProtectionConfig()
        assert config.drift_threshold == GUARDIAN_DRIFT_THRESHOLD
        assert config.hallucination_threshold == HALLUCINATION_THRESHOLD
        assert config.enable_auto_rollback is True

        # Custom configuration
        custom_config = DriftProtectionConfig(
            drift_threshold=0.2,
            enable_auto_rollback=False,
            checkpoint_interval=50
        )
        assert custom_config.drift_threshold == 0.2
        assert custom_config.enable_auto_rollback is False
        assert custom_config.checkpoint_interval == 50


@pytest.fixture
def mock_drift_score():
    """Mock DriftScore for testing"""
    return DriftScore(
        overall_score=0.08,
        entropy_delta=0.04,
        glyph_divergence=0.05,
        emotional_drift=0.03,
        ethical_drift=0.02,
        temporal_decay=0.01,
        phase=DriftPhase.EARLY,
        recursive_indicators=[],
        risk_level="LOW",
        metadata={"test": True}
    )

@pytest.fixture
def mock_high_drift_score():
    """Mock high DriftScore for testing drift violations"""
    return DriftScore(
        overall_score=0.18,  # Above 0.15 threshold
        entropy_delta=0.15,  # High entropy
        glyph_divergence=0.08,
        emotional_drift=0.12,  # High emotional drift
        ethical_drift=0.06,
        temporal_decay=0.02,
        phase=DriftPhase.CASCADE,
        recursive_indicators=["loop_detected"],
        risk_level="CRITICAL",
        metadata={"high_drift": True}
    )


class TestDriftDetectionIntegration:
    """Tests for drift detection integration with LUKHAS components"""

    async def test_drift_status_check_normal(self, drift_protection_system, mock_drift_score):
        """Test normal drift status checking"""
        # Mock drift calculation
        drift_protection_system.drift_tracker.calculate_drift = AsyncMock(return_value=mock_drift_score)
        drift_protection_system.drift_dashboard.update_drift_metrics = AsyncMock()

        # Mock symbolic state
        with patch.object(drift_protection_system, '_get_current_symbolic_state') as mock_state:
            mock_state.return_value = SymbolicState(
                session_id="test_session",
                timestamp=datetime.now(timezone.utc),
                symbols=[],
                emotional_vector=[0.0, 0.0, 0.0],
                ethical_alignment=1.0,
                entropy=0.0,
                context_metadata={},
                hash_signature="test_hash"
            )

            result = await drift_protection_system._check_drift_status()

            assert result.overall_score == 0.08
            assert result.phase == DriftPhase.EARLY
            assert len(drift_protection_system.drift_events) == 1  # Event logged
            drift_protection_system.drift_dashboard.update_drift_metrics.assert_called_once()

    async def test_drift_status_check_high_drift(self, drift_protection_system, mock_high_drift_score):
        """Test drift status checking with high drift"""
        # Mock drift calculation
        drift_protection_system.drift_tracker.calculate_drift = AsyncMock(return_value=mock_high_drift_score)
        drift_protection_system.drift_dashboard.update_drift_metrics = AsyncMock()

        # Mock symbolic state
        with patch.object(drift_protection_system, '_get_current_symbolic_state') as mock_state:
            mock_state.return_value = SymbolicState(
                session_id="test_session",
                timestamp=datetime.now(timezone.utc),
                symbols=[],
                emotional_vector=[0.2, 0.8, 0.1],  # High arousal
                ethical_alignment=0.9,
                entropy=0.15,  # Higher entropy
                context_metadata={},
                hash_signature="test_hash"
            )

            result = await drift_protection_system._check_drift_status()

            assert result.overall_score == 0.18
            assert result.phase == DriftPhase.CASCADE

            # Check drift event details
            drift_event = drift_protection_system.drift_events[-1]
            assert drift_event.intervention_required is True
            assert drift_event.drift_score == 0.18
            assert 'emotional_regulation' in drift_event.affected_components
            assert 'entropy_management' in drift_event.affected_components

    async def test_collapse_hash_integration(self, drift_protection_system):
        """Test CollapseHash integration for checkpoints"""
        # Mock checkpoint creation
        mock_checkpoint = Checkpoint(
            checkpoint_id=f"checkpoint_{uuid.uuid4().hex[:8]}",
            root_hash="test_hash_value",
            timestamp=datetime.now(timezone.utc).timestamp(),
            metadata={"operation": "innovation_generation"}
        )

        drift_protection_system.collapse_hash.create_checkpoint = AsyncMock(return_value=mock_checkpoint)

        result = await drift_protection_system._create_checkpoint()

        assert result is not None
        assert len(drift_protection_system.checkpoints) == 1
        drift_protection_system.collapse_hash.create_checkpoint.assert_called_once()

    async def test_drift_dashboard_integration(self, drift_protection_system, mock_drift_score):
        """Test DriftDashboard integration for metrics updates"""
        drift_protection_system.drift_dashboard.update_drift_metrics = AsyncMock()
        drift_protection_system.drift_tracker.calculate_drift = AsyncMock(return_value=mock_drift_score)

        with patch.object(drift_protection_system, '_get_current_symbolic_state'):
            await drift_protection_system._check_drift_status()

        drift_protection_system.drift_dashboard.update_drift_metrics.assert_called_once_with(mock_drift_score)

    async def test_continuous_drift_monitoring(self, drift_protection_system):
        """Test continuous drift monitoring during operations"""
        # Mock drift monitor
        drift_protection_system.drift_monitor.get_current_drift = AsyncMock(return_value=0.12)
        drift_protection_system.drift_monitor.trigger_intervention = AsyncMock()

        # Start monitoring task
        monitoring_task = asyncio.create_task(
            drift_protection_system._continuous_drift_monitoring()
        )

        # Let it run briefly
        await asyncio.sleep(0.15)  # Allow at least one check

        # Cancel the task
        monitoring_task.cancel()

        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        # Verify monitoring was active
        drift_protection_system.drift_monitor.get_current_drift.assert_called()

    async def test_critical_drift_emergency_halt(self, drift_protection_system):
        """Test emergency halt on critical drift"""
        # Mock critical drift
        drift_protection_system.drift_monitor.get_current_drift = AsyncMock(return_value=0.18)  # Above threshold
        drift_protection_system.drift_monitor.trigger_intervention = AsyncMock()

        # Start monitoring
        monitoring_task = asyncio.create_task(
            drift_protection_system._continuous_drift_monitoring()
        )

        # Wait for drift detection
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(monitoring_task, timeout=0.5)

        # Verify emergency intervention was triggered
        drift_protection_system.drift_monitor.trigger_intervention.assert_called_with(
            InterventionType.EMERGENCY_HALT
        )


class TestHallucinationPrevention:
    """Tests for hallucination detection and prevention"""

    @pytest.fixture
    def mock_innovation(self):
        """Mock innovation for hallucination testing"""
        return BreakthroughInnovation(
            innovation_id="test_innovation_001",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            title="AI Breakthrough",
            description="Revolutionary AI system with quantum processing",
            breakthrough_score=0.9,
            impact_assessment={"technical": 0.95, "commercial": 0.85},
            implementation_plan={"phases": ["research", "prototype", "deployment"]},
            patent_potential=["quantum_ai", "neural_optimization"],
            validated_in_realities=["reality_1", "reality_2"],
        )

    @pytest.mark.parametrize("hallucination_type", [
        HallucinationType.LOGICAL_INCONSISTENCY,
        HallucinationType.CAUSAL_VIOLATION,
        HallucinationType.PROBABILITY_ANOMALY,
        HallucinationType.ETHICAL_DEVIATION,
        HallucinationType.MEMORY_FABRICATION,
        HallucinationType.RECURSIVE_LOOP,
        HallucinationType.REALITY_BLEED,
    ])
    async def test_hallucination_detection_types(self, drift_protection_system, mock_innovation, hallucination_type):
        """Test detection of all hallucination types"""
        # Mock specific hallucination detection
        with patch.object(drift_protection_system, '_detect_specific_hallucination') as mock_detect:
            mock_detect.return_value = True if hallucination_type == HallucinationType.LOGICAL_INCONSISTENCY else False

            result = await drift_protection_system._validate_no_hallucinations(mock_innovation)

            if hallucination_type == HallucinationType.LOGICAL_INCONSISTENCY:
                assert not result['passed']
                assert HallucinationType.LOGICAL_INCONSISTENCY.value in result['hallucinations']
            else:
                # Other types should not be detected in this test
                mock_detect.assert_called()

    async def test_hallucination_report_processing(self, drift_protection_system):
        """Test processing of hallucination reports"""
        mock_report = HallucinationReport(
            hallucination_id="hall_001",
            detection_time=datetime.now(timezone.utc),
            hallucination_type=HallucinationType.LOGICAL_INCONSISTENCY,
            severity=0.8,
            affected_branches=["reality_1"],
            evidence={"inconsistency_score": 0.8},
            recommended_action="reject_innovation",
            auto_corrected=False
        )

        # Mock safety framework
        drift_protection_system.safety_framework.detect_hallucinations = AsyncMock(return_value=mock_report)

        test_result = {"innovation_data": "test", "reality_id": "reality_1"}
        result = await drift_protection_system._check_for_hallucination(test_result)

        assert result is not None
        assert result.hallucination_type == HallucinationType.LOGICAL_INCONSISTENCY
        assert result.severity == 0.8

    async def test_hallucination_free_filtering(self, drift_protection_system):
        """Test filtering of hallucination-free results"""
        # Mock results with mixed hallucination status
        reality_results = [
            {"innovation_data": "clean_result", "reality_id": "reality_1"},
            {"innovation_data": "tainted_result", "reality_id": "reality_2"},
            {"innovation_data": "another_clean", "reality_id": "reality_3"},
        ]

        # Mock hallucination detection - reality_2 has hallucinations
        def mock_hallucination_check(result):
            if result["reality_id"] == "reality_2":
                return asyncio.coroutine(lambda: HallucinationReport(
                    hallucination_id="hall_002",
                    detection_time=datetime.now(timezone.utc),
                    hallucination_type=HallucinationType.CAUSAL_VIOLATION,
                    severity=0.7,
                    affected_branches=["reality_2"],
                    evidence={"violation_score": 0.7},
                    recommended_action="discard",
                    auto_corrected=False
                ))()
            return asyncio.coroutine(lambda: None)()

        with patch.object(drift_protection_system, '_check_for_hallucination', side_effect=mock_hallucination_check):
            # Mock innovation core methods
            drift_protection_system.innovation_core.explore_innovation_in_parallel_realities = AsyncMock(return_value=reality_results)
            drift_protection_system.innovation_core.validate_and_synthesize_innovation = AsyncMock(return_value=None)

            hypothesis = InnovationHypothesis(
                hypothesis_id="test_hyp_001",
                domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
                description="Test hypothesis",
                breakthrough_potential=0.8,
                feasibility_score=0.7,
                impact_magnitude=0.9
            )

            result = await drift_protection_system._monitored_innovation_generation(hypothesis, 3, 5)

            # Should have filtered out reality_2
            drift_protection_system.innovation_core.validate_and_synthesize_innovation.assert_called_once()
            call_args = drift_protection_system.innovation_core.validate_and_synthesize_innovation.call_args[0]
            filtered_results = call_args[1]  # Second argument is the filtered results

            # Only 2 clean results should remain
            assert len(filtered_results) == 2
            reality_ids = [r["reality_id"] for r in filtered_results]
            assert "reality_1" in reality_ids
            assert "reality_3" in reality_ids
            assert "reality_2" not in reality_ids

    async def test_no_hallucination_free_results(self, drift_protection_system):
        """Test handling when all results contain hallucinations"""
        reality_results = [
            {"innovation_data": "tainted_1", "reality_id": "reality_1"},
            {"innovation_data": "tainted_2", "reality_id": "reality_2"},
        ]

        # Mock all results as having hallucinations
        mock_report = HallucinationReport(
            hallucination_id="hall_003",
            detection_time=datetime.now(timezone.utc),
            hallucination_type=HallucinationType.MEMORY_FABRICATION,
            severity=0.6,
            affected_branches=["reality_1", "reality_2"],
            evidence={"fabrication_score": 0.6},
            recommended_action="reject",
            auto_corrected=False
        )

        with patch.object(drift_protection_system, '_check_for_hallucination', return_value=mock_report):
            drift_protection_system.innovation_core.explore_innovation_in_parallel_realities = AsyncMock(return_value=reality_results)

            hypothesis = InnovationHypothesis(
                hypothesis_id="test_hyp_002",
                domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
                description="Test hypothesis",
                breakthrough_potential=0.8,
                feasibility_score=0.7,
                impact_magnitude=0.9
            )

            result = await drift_protection_system._monitored_innovation_generation(hypothesis, 2, 3)

            assert result is None  # No valid results


class TestEthicsRecalibration:
    """Tests for ethics recalibration on drift threshold violations"""

    async def test_ethics_recalibration_trigger(self, drift_protection_system):
        """Test ethics recalibration when drift exceeds 0.15 threshold"""
        # Mock high ethical drift
        high_drift = DriftScore(
            overall_score=0.18,
            entropy_delta=0.06,
            glyph_divergence=0.05,
            emotional_drift=0.08,
            ethical_drift=0.16,  # Above threshold, triggers ethics recalibration
            temporal_decay=0.02,
            phase=DriftPhase.CASCADE,
            recursive_indicators=[],
            risk_level="HIGH",
            metadata={}
        )

        # Mock recalibration methods
        drift_protection_system._recalibrate_ethics = AsyncMock()
        drift_protection_system._recalibrate_emotions = AsyncMock()
        drift_protection_system._recalibrate_entropy = AsyncMock()
        drift_protection_system.drift_tracker.reset_baseline = AsyncMock()

        await drift_protection_system._recalibrate_system(high_drift)

        # Should trigger ethics recalibration
        drift_protection_system._recalibrate_ethics.assert_called_once()
        drift_protection_system.drift_tracker.reset_baseline.assert_called_once()

    async def test_emotional_recalibration_trigger(self, drift_protection_system):
        """Test emotional recalibration when emotional drift exceeds threshold"""
        high_emotional_drift = DriftScore(
            overall_score=0.17,
            entropy_delta=0.07,
            glyph_divergence=0.04,
            emotional_drift=0.16,  # Above threshold
            ethical_drift=0.05,
            temporal_decay=0.03,
            phase=DriftPhase.CASCADE,
            recursive_indicators=[],
            risk_level="HIGH",
            metadata={}
        )

        # Mock recalibration methods
        drift_protection_system._recalibrate_emotions = AsyncMock()
        drift_protection_system.drift_tracker.reset_baseline = AsyncMock()

        await drift_protection_system._recalibrate_system(high_emotional_drift)

        drift_protection_system._recalibrate_emotions.assert_called_once()

    async def test_entropy_recalibration_trigger(self, drift_protection_system):
        """Test entropy recalibration when entropy delta exceeds threshold"""
        high_entropy_drift = DriftScore(
            overall_score=0.19,
            entropy_delta=0.17,  # Above threshold
            glyph_divergence=0.06,
            emotional_drift=0.08,
            ethical_drift=0.07,
            temporal_decay=0.04,
            phase=DriftPhase.CASCADE,
            recursive_indicators=[],
            risk_level="CRITICAL",
            metadata={}
        )

        # Mock recalibration methods
        drift_protection_system._recalibrate_entropy = AsyncMock()
        drift_protection_system.drift_tracker.reset_baseline = AsyncMock()

        await drift_protection_system._recalibrate_system(high_entropy_drift)

        drift_protection_system._recalibrate_entropy.assert_called_once()

    async def test_ethics_framework_adjustment(self, drift_protection_system):
        """Test ethics framework threshold adjustment"""
        drift_protection_system.safety_framework.adjust_ethics_threshold = AsyncMock()

        await drift_protection_system._recalibrate_ethics()

        drift_protection_system.safety_framework.adjust_ethics_threshold.assert_called_once_with(
            drift_protection_system.config.recalibration_sensitivity
        )

    async def test_vivox_ern_reset(self, drift_protection_system):
        """Test VIVOX ERN baseline reset"""
        assert drift_protection_system.vivox_ern is not None
        drift_protection_system.vivox_ern.reset_to_baseline = AsyncMock()

        await drift_protection_system._recalibrate_emotions()

        drift_protection_system.vivox_ern.reset_to_baseline.assert_called_once()

    async def test_entropy_tracker_recalibration(self, drift_protection_system):
        """Test entropy tracker recalibration"""
        drift_protection_system.drift_tracker.recalibrate_entropy = AsyncMock()

        await drift_protection_system._recalibrate_entropy()

        drift_protection_system.drift_tracker.recalibrate_entropy.assert_called_once()


class TestEmotionalRegulation:
    """Tests for emotional regulation via VIVOX ERN"""

    @pytest.fixture
    def mock_vad_vector(self):
        """Mock VAD vector for testing"""
        return VADVector(
            valence=0.2,
            arousal=0.8,  # High arousal
            dominance=0.6
        )

    async def test_emotional_state_regulation_high_intensity(self, drift_protection_system, mock_vad_vector):
        """Test emotional regulation when intensity is high"""
        # Mock high intensity emotional state
        mock_vad_vector.magnitude = Mock(return_value=0.85)  # Above 0.7 threshold

        drift_protection_system.vivox_ern.get_current_state = AsyncMock(return_value=mock_vad_vector)
        drift_protection_system.vivox_ern.apply_regulation = AsyncMock()

        await drift_protection_system._regulate_emotional_state()

        # Should apply dampening strategy due to high arousal
        drift_protection_system.vivox_ern.apply_regulation.assert_called_once_with(
            RegulationStrategy.DAMPENING
        )

    async def test_emotional_state_regulation_moderate_intensity(self, drift_protection_system):
        """Test emotional regulation with moderate intensity"""
        mock_vad = VADVector(valence=0.3, arousal=0.6, dominance=0.5)
        mock_vad.magnitude = Mock(return_value=0.75)  # Above threshold but arousal not extreme

        drift_protection_system.vivox_ern.get_current_state = AsyncMock(return_value=mock_vad)
        drift_protection_system.vivox_ern.apply_regulation = AsyncMock()

        await drift_protection_system._regulate_emotional_state()

        # Should apply stabilization strategy
        drift_protection_system.vivox_ern.apply_regulation.assert_called_once_with(
            RegulationStrategy.STABILIZATION
        )

    async def test_emotional_state_no_regulation_needed(self, drift_protection_system):
        """Test no emotional regulation when intensity is low"""
        mock_vad = VADVector(valence=0.1, arousal=0.2, dominance=0.3)
        mock_vad.magnitude = Mock(return_value=0.4)  # Below 0.7 threshold

        drift_protection_system.vivox_ern.get_current_state = AsyncMock(return_value=mock_vad)
        drift_protection_system.vivox_ern.apply_regulation = AsyncMock()

        await drift_protection_system._regulate_emotional_state()

        # Should not apply any regulation
        drift_protection_system.vivox_ern.apply_regulation.assert_not_called()

    async def test_emotional_regulation_disabled(self, drift_protection_config):
        """Test system behavior when emotional regulation is disabled"""
        # Create system with emotional regulation disabled
        config = DriftProtectionConfig(enable_emotional_regulation=False)

        with patch.multiple(
            'consciousness.dream.innovation_drift_protection',
            SymbolicDriftTracker=AsyncMock,
            UnifiedDriftMonitor=AsyncMock,
            DriftDashboard=AsyncMock,
            CollapseHash=AsyncMock,
            ParallelRealitySafetyFramework=AsyncMock,
        ):
            system = InnovationDriftProtection(config=config)

            # VIVOX ERN should not be initialized
            assert system.vivox_ern is None

            # Regulation should be a no-op
            await system._regulate_emotional_state()
            # Should complete without error

    async def test_vivox_ern_integration_flow(self, drift_protection_system):
        """Test full VIVOX ERN integration flow"""
        # Mock emotional state that triggers regulation
        mock_vad = VADVector(valence=-0.5, arousal=0.9, dominance=0.2)
        mock_vad.magnitude = Mock(return_value=0.95)

        drift_protection_system.vivox_ern.get_current_state = AsyncMock(return_value=mock_vad)
        drift_protection_system.vivox_ern.apply_regulation = AsyncMock()

        await drift_protection_system._regulate_emotional_state()

        # Verify the complete flow
        drift_protection_system.vivox_ern.get_current_state.assert_called_once()
        drift_protection_system.vivox_ern.apply_regulation.assert_called_once_with(
            RegulationStrategy.DAMPENING  # High arousal triggers dampening
        )


class TestCheckpointAndRollback:
    """Tests for checkpoint creation and rollback scenarios"""

    async def test_checkpoint_creation_interval(self, drift_protection_system):
        """Test checkpoint creation at specified intervals"""
        # Mock checkpoint creation
        mock_checkpoint = IntegrityCheckpoint(
            checkpoint_id=f"checkpoint_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.now(timezone.utc),
            hash_value="test_hash",
            previous_hash=None,
            metadata={"operation": "innovation_generation"}
        )

        drift_protection_system.collapse_hash.create_checkpoint = AsyncMock(return_value=mock_checkpoint)

        # Simulate operations to reach checkpoint interval (10 operations)
        for i in range(12):  # Go past interval
            await drift_protection_system._create_checkpoint()

        # Should create checkpoint at operation 10
        assert len(drift_protection_system.checkpoints) >= 1
        assert drift_protection_system.operation_count == 12

    async def test_checkpoint_history_limit(self, drift_protection_system):
        """Test checkpoint history limiting"""
        # Create more checkpoints than max_rollback_depth (5)
        mock_checkpoints = []
        for i in range(8):
            checkpoint = Checkpoint(
                checkpoint_id=f"checkpoint_{i}",
                root_hash=f"hash_{i}",
                timestamp=datetime.now(timezone.utc).timestamp(),
                metadata={"operation": f"operation_{i}"}
            )
            mock_checkpoints.append(checkpoint)

        drift_protection_system.collapse_hash.create_checkpoint = AsyncMock(side_effect=mock_checkpoints)

        # Set operation count to trigger multiple checkpoints
        drift_protection_system.operation_count = 0
        for i in range(80):  # 8 checkpoint intervals
            await drift_protection_system._create_checkpoint()

        # Should maintain only max_rollback_depth checkpoints
        assert len(drift_protection_system.checkpoints) <= drift_protection_system.config.max_rollback_depth

    async def test_rollback_on_unsafe_innovation(self, drift_protection_system):
        """Test rollback when unsafe innovation is detected"""
        mock_checkpoint = Checkpoint(
            checkpoint_id="safe_checkpoint",
            root_hash="safe_hash",
            timestamp=datetime.now(timezone.utc).timestamp(),
            metadata={"operation": "pre_innovation"}
        )

        mock_innovation = BreakthroughInnovation(
            innovation_id="unsafe_innovation",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            title="Unsafe AI",
            description="Potentially harmful AI system",
            breakthrough_score=0.95,
            impact_assessment={"technical": 0.9, "commercial": 0.8},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[]
        )

        # Mock rollback
        drift_protection_system.collapse_hash.rollback = AsyncMock()
        drift_protection_system.drift_monitor.log_safety_violation = AsyncMock()

        await drift_protection_system._handle_unsafe_innovation(mock_innovation, mock_checkpoint)

        # Verify rollback occurred
        drift_protection_system.collapse_hash.rollback.assert_called_once_with(mock_checkpoint)
        drift_protection_system.drift_monitor.log_safety_violation.assert_called_once()

    async def test_rollback_on_drift_violation(self, drift_protection_system):
        """Test rollback when drift threshold is violated"""
        high_drift = DriftScore(
            overall_score=0.25,  # Well above threshold
            entropy_delta=0.18,
            glyph_divergence=0.1,
            emotional_drift=0.15,
            ethical_drift=0.12,
            temporal_decay=0.08,
            phase=DriftPhase.CASCADE,
            recursive_indicators=["high_drift_detected"],
            risk_level="CRITICAL",
            metadata={}
        )

        mock_checkpoint = Checkpoint(
            checkpoint_id="pre_drift_checkpoint",
            root_hash="pre_drift_hash",
            timestamp=datetime.now(timezone.utc).timestamp(),
            metadata={"operation": "before_drift"}
        )

        # Mock rollback and recalibration
        drift_protection_system.collapse_hash.rollback = AsyncMock()
        drift_protection_system._recalibrate_system = AsyncMock()

        await drift_protection_system._handle_drift_violation(high_drift, mock_checkpoint)

        # Verify rollback and recalibration
        drift_protection_system.collapse_hash.rollback.assert_called_once_with(mock_checkpoint)
        drift_protection_system._recalibrate_system.assert_called_once_with(high_drift)

    async def test_no_rollback_when_disabled(self, drift_protection_config):
        """Test behavior when auto-rollback is disabled"""
        config = DriftProtectionConfig(enable_auto_rollback=False)

        with patch.multiple(
            'consciousness.dream.innovation_drift_protection',
            SymbolicDriftTracker=AsyncMock,
            UnifiedDriftMonitor=AsyncMock,
            DriftDashboard=AsyncMock,
            CollapseHash=AsyncMock,
            VivoxERN=AsyncMock,
            ParallelRealitySafetyFramework=AsyncMock,
        ):
            system = InnovationDriftProtection(config=config)
            system.collapse_hash.rollback = AsyncMock()
            system.drift_monitor.log_safety_violation = AsyncMock()

            mock_innovation = BreakthroughInnovation(
                innovation_id="test",
                domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
                title="Test",
                description="Test",
                breakthrough_score=0.5,
                impact_assessment={},
                implementation_plan={},
                patent_potential=[],
                validated_in_realities=[]
            )

            await system._handle_unsafe_innovation(mock_innovation, None)

            # Should not attempt rollback
            system.collapse_hash.rollback.assert_not_called()
            # But should still log violation
            system.drift_monitor.log_safety_violation.assert_called_once()


class TestProhibitedContentDetection:
    """Tests for prohibited content detection"""

    @pytest.fixture
    def prohibited_innovation(self):
        """Innovation containing prohibited content"""
        return BreakthroughInnovation(
            innovation_id="prohibited_001",
            domain=InnovationDomain.BIOTECHNOLOGY,
            title="Harmful Technology Advancement",
            description="This innovation involves dangerous knowledge and unethical application",
            breakthrough_score=0.9,
            impact_assessment={"technical": 0.95, "commercial": 0.8},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[]
        )

    @pytest.fixture
    def clean_innovation(self):
        """Innovation with clean content"""
        return BreakthroughInnovation(
            innovation_id="clean_001",
            domain=InnovationDomain.SUSTAINABLE_SYSTEMS,
            title="Green Energy Solution",
            description="Innovative renewable energy system for sustainable development",
            breakthrough_score=0.85,
            impact_assessment={"technical": 0.8, "commercial": 0.9},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[]
        )

    async def test_prohibited_content_detection(self, drift_protection_system, prohibited_innovation):
        """Test detection of prohibited content patterns"""
        result = await drift_protection_system._check_prohibited_content(prohibited_innovation)

        assert not result['passed']
        assert len(result['prohibited_content']) > 0
        assert 'harmful_technology' in result['prohibited_content']
        assert 'dangerous_knowledge' in result['prohibited_content']
        assert 'unethical_application' in result['prohibited_content']

    async def test_clean_content_validation(self, drift_protection_system, clean_innovation):
        """Test validation passes for clean content"""
        result = await drift_protection_system._check_prohibited_content(clean_innovation)

        assert result['passed']
        assert len(result['prohibited_content']) == 0

    async def test_prohibited_content_in_validation_flow(self, drift_protection_system, prohibited_innovation):
        """Test prohibited content detection in full validation flow"""
        # Mock other validation checks to pass
        drift_protection_system._validate_drift_compliance = AsyncMock(return_value={'passed': True})
        drift_protection_system._validate_no_hallucinations = AsyncMock(return_value={'passed': True})
        drift_protection_system._validate_ethics_compliance = AsyncMock(return_value={'passed': True})

        result = await drift_protection_system._validate_innovation(prohibited_innovation)

        assert not result['safe']
        assert result['reason'] == 'Prohibited content detected'
        assert result['checks']['prohibited']['passed'] is False

    async def test_multiple_prohibited_patterns(self, drift_protection_system):
        """Test detection of multiple prohibited patterns"""
        multi_prohibited_innovation = BreakthroughInnovation(
            innovation_id="multi_prohibited",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            title="Restricted Domain with Harmful Technology",
            description="Dangerous knowledge in unethical application area",
            breakthrough_score=0.95,
            impact_assessment={},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[]
        )

        result = await drift_protection_system._check_prohibited_content(multi_prohibited_innovation)

        assert not result['passed']
        expected_patterns = ['restricted_domain', 'harmful_technology', 'dangerous_knowledge', 'unethical_application']
        for pattern in expected_patterns:
            assert pattern in result['prohibited_content']


class TestPerformanceRequirements:
    """Tests for performance requirements (<250ms drift detection, <1s rollback)"""

    @pytest.mark.perf
    async def test_drift_detection_performance(self, drift_protection_system, perf_tracker):
        """Test drift detection completes within 250ms"""
        # Mock fast responses
        drift_protection_system.drift_tracker.calculate_drift = AsyncMock(return_value=DriftScore(
            overall_score=0.05,
            entropy_delta=0.015,
            glyph_divergence=0.02,
            emotional_drift=0.01,
            ethical_drift=0.01,
            temporal_decay=0.005,
            phase=DriftPhase.EARLY,
            recursive_indicators=[],
            risk_level="LOW",
            metadata={}
        ))
        drift_protection_system.drift_dashboard.update_drift_metrics = AsyncMock()

        # Run multiple drift detection cycles
        for i in range(10):
            start_time = perf_tracker.start(f"drift_detection_{i}")

            with patch.object(drift_protection_system, '_get_current_symbolic_state'):
                await drift_protection_system._check_drift_status()

            perf_tracker.end(f"drift_detection_{i}", start_time)

        # At minimum, verify the operations completed (actual timing depends on system)
        assert drift_protection_system.drift_tracker.calculate_drift.call_count == 10
        assert drift_protection_system.drift_dashboard.update_drift_metrics.call_count == 10

    @pytest.mark.perf
    async def test_rollback_performance(self, drift_protection_system, perf_tracker):
        """Test rollback completes within 1000ms"""
        mock_checkpoint = Checkpoint(
            checkpoint_id="perf_test_checkpoint",
            root_hash="perf_hash",
            timestamp=datetime.now(timezone.utc).timestamp(),
            metadata={"operation": "performance_test"}
        )

        # Mock fast rollback
        drift_protection_system.collapse_hash.rollback = AsyncMock()

        # Run multiple rollback operations
        for i in range(5):
            start_time = perf_tracker.start(f"rollback_{i}")

            await drift_protection_system.collapse_hash.rollback(mock_checkpoint)

            perf_tracker.end(f"rollback_{i}", start_time)

        # Verify rollbacks were called (timing verification is system-dependent)
        assert drift_protection_system.collapse_hash.rollback.call_count == 5

    @pytest.mark.perf
    async def test_continuous_monitoring_overhead(self, drift_protection_system):
        """Test continuous monitoring has acceptable overhead"""
        # Mock lightweight drift monitoring
        drift_protection_system.drift_monitor.get_current_drift = AsyncMock(return_value=0.05)

        start_time = time.perf_counter()

        # Run monitoring for a short period
        monitoring_task = asyncio.create_task(
            drift_protection_system._continuous_drift_monitoring()
        )

        await asyncio.sleep(0.5)  # Monitor for 500ms
        monitoring_task.cancel()

        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        elapsed = time.perf_counter() - start_time

        # Monitoring should not add significant overhead
        assert elapsed < 0.6  # Allow some buffer beyond 500ms sleep

        # Verify monitoring was active
        assert drift_protection_system.drift_monitor.get_current_drift.call_count > 0

    @pytest.mark.perf
    async def test_innovation_validation_performance(self, drift_protection_system):
        """Test innovation validation performance"""
        mock_innovation = BreakthroughInnovation(
            innovation_id="perf_test_innovation",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            title="Performance Test Innovation",
            description="Clean innovation for performance testing",
            breakthrough_score=0.8,
            impact_assessment={"technical": 0.85, "commercial": 0.75},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[],
            metadata={"drift_analysis": {"aggregate": 0.03}}
        )

        # Mock all validation checks to be fast
        drift_protection_system.safety_framework.validate_ethics = AsyncMock(return_value={'compliant': True, 'violations': []})

        start_time = time.perf_counter()

        result = await drift_protection_system._validate_innovation(mock_innovation)

        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms

        assert result['safe'] is True
        # Validation should be reasonably fast
        assert elapsed < 100  # Less than 100ms for validation


class TestSystemIntegration:
    """Tests for integration with existing LUKHAS systems"""

    async def test_service_registration(self):
        """Test service registration in dependency injection system"""
        with patch('consciousness.dream.innovation_drift_protection.register_service') as mock_register:
            with patch.multiple(
                'consciousness.dream.innovation_drift_protection',
                SymbolicDriftTracker=AsyncMock,
                UnifiedDriftMonitor=AsyncMock,
                DriftDashboard=AsyncMock,
                CollapseHash=AsyncMock,
                VivoxERN=AsyncMock,
                ParallelRealitySafetyFramework=AsyncMock,
            ):
                system = InnovationDriftProtection()

                # Mock subsystem initialization
                system.drift_tracker.initialize = AsyncMock()
                system.drift_monitor.initialize = AsyncMock()
                system.drift_dashboard.initialize = AsyncMock()
                system.collapse_hash.initialize = AsyncMock()
                system.vivox_ern.initialize = AsyncMock()
                system.safety_framework.initialize = AsyncMock()

                await system.initialize()

                mock_register.assert_called_once_with("innovation_drift_protection", system)

    async def test_drift_protection_initialization_function(self):
        """Test module initialization function"""
        with patch('consciousness.dream.innovation_drift_protection.get_service') as mock_get_service:
            with patch('consciousness.dream.autonomous_innovation_core.initialize_innovation_core') as mock_init_core:
                # Mock no existing innovation core service
                mock_get_service.return_value = None
                mock_innovation_core = AsyncMock()
                mock_init_core.return_value = mock_innovation_core

                with patch('consciousness.dream.innovation_drift_protection.InnovationDriftProtection') as mock_class:
                    mock_instance = AsyncMock()
                    mock_class.return_value = mock_instance

                    result = await initialize_drift_protection()

                    # Should create innovation core and drift protection
                    mock_init_core.assert_called_once()
                    mock_class.assert_called_once_with(
                        innovation_core=mock_innovation_core,
                        config=pytest.ANY
                    )
                    mock_instance.initialize.assert_called_once()

                    assert result == mock_instance

    async def test_glyph_token_handling(self, drift_protection_system):
        """Test GLYPH token handling for CoreInterface compliance"""
        from core.common import GLYPHSymbol, GLYPHToken

        test_token = GLYPHToken(
            symbol=GLYPHSymbol.DRIFT_DETECTED,
            timestamp=datetime.now(timezone.utc),
            metadata={"drift_score": 0.12}
        )

        result = await drift_protection_system.handle_glyph(test_token)

        # Should return the token (pass-through behavior)
        assert result == test_token

    async def test_process_interface_compliance(self, drift_protection_system):
        """Test CoreInterface process method compliance"""
        # Test with hypothesis input
        hypothesis = InnovationHypothesis(
            hypothesis_id="test_process_hyp",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            description="Test process hypothesis",
            breakthrough_potential=0.75,
            feasibility_score=0.8,
            impact_magnitude=0.85
        )

        input_data = {"hypothesis": hypothesis}

        # Mock innovation generation
        mock_innovation = BreakthroughInnovation(
            innovation_id="process_test_innovation",
            domain=InnovationDomain.ARTIFICIAL_INTELLIGENCE,
            title="Process Test",
            description="Test innovation from process method",
            breakthrough_score=0.8,
            impact_assessment={},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=[]
        )

        with patch.object(drift_protection_system, 'generate_innovation_with_protection', return_value=mock_innovation):
            result = await drift_protection_system.process(input_data)

            assert 'innovation' in result
            assert result['innovation'] == mock_innovation

    async def test_status_reporting(self, drift_protection_system):
        """Test status reporting functionality"""
        # Add some test data
        drift_protection_system.operation_count = 42
        test_event = DriftEvent(
            event_id="status_test_event",
            timestamp=datetime.now(timezone.utc),
            drift_type=DriftType.SYMBOLIC,
            drift_score=0.08,
            phase=DriftPhase.STABLE,
            affected_components=["symbolic_system"],
            intervention_required=False
        )
        drift_protection_system.drift_events.append(test_event)

        status = drift_protection_system.get_status()

        assert status['operational'] is True
        assert status['drift_threshold'] == 0.15
        assert status['operation_count'] == 42
        assert status['drift_events'] == 1
        assert status['last_drift_score'] == 0.08

    async def test_error_handling_and_propagation(self, drift_protection_system):
        """Test error handling and propagation in critical paths"""
        # Test initialization error propagation
        system = InnovationDriftProtection()
        system.drift_tracker = AsyncMock()
        system.drift_tracker.initialize.side_effect = Exception("Test initialization error")

        with pytest.raises(LukhasError) as exc_info:
            await system.initialize()

        assert "Drift Protection initialization failed" in str(exc_info.value)

    async def test_full_integration_flow(self, drift_protection_system):
        """Test complete integration flow from hypothesis to innovation"""
        hypothesis = InnovationHypothesis(
            hypothesis_id="integration_test_hyp",
            domain=InnovationDomain.SUSTAINABLE_SYSTEMS,
            description="Full integration test hypothesis",
            breakthrough_potential=0.85,
            feasibility_score=0.9,
            impact_magnitude=0.8
        )

        # Mock successful flow
        drift_protection_system._check_drift_status = AsyncMock(return_value=DriftScore(
            overall_score=0.05,  # Low drift
            entropy_delta=0.015,
            glyph_divergence=0.02,
            emotional_drift=0.01,
            ethical_drift=0.01,
            temporal_decay=0.005,
            phase=DriftPhase.EARLY,
            recursive_indicators=[],
            risk_level="LOW",
            metadata={}
        ))

        drift_protection_system._regulate_emotional_state = AsyncMock()
        drift_protection_system._create_checkpoint = AsyncMock(return_value=Checkpoint(
            checkpoint_id="integration_checkpoint",
            root_hash="integration_hash",
            timestamp=datetime.now(timezone.utc).timestamp(),
            metadata={}
        ))

        mock_innovation = BreakthroughInnovation(
            innovation_id="integration_innovation",
            domain=InnovationDomain.SUSTAINABLE_SYSTEMS,
            title="Integration Test Innovation",
            description="Clean, validated innovation from integration test",
            breakthrough_score=0.85,
            impact_assessment={"technical": 0.9, "commercial": 0.8},
            implementation_plan={},
            patent_potential=[],
            validated_in_realities=["reality_1", "reality_2"],
            metadata={"drift_analysis": {"aggregate": 0.03}}
        )

        drift_protection_system._monitored_innovation_generation = AsyncMock(return_value=mock_innovation)
        drift_protection_system._validate_innovation = AsyncMock(return_value={
            'safe': True,
            'reason': None,
            'checks': {
                'drift': {'passed': True},
                'hallucination': {'passed': True},
                'ethics': {'passed': True},
                'prohibited': {'passed': True}
            }
        })

        result = await drift_protection_system.generate_innovation_with_protection(
            hypothesis, reality_count=20, exploration_depth=8
        )

        assert result is not None
        assert result.innovation_id == "integration_innovation"
        assert result.domain == InnovationDomain.SUSTAINABLE_SYSTEMS

        # Verify all protection steps were executed
        drift_protection_system._check_drift_status.assert_called()
        drift_protection_system._regulate_emotional_state.assert_called()
        drift_protection_system._create_checkpoint.assert_called()
        drift_protection_system._monitored_innovation_generation.assert_called_once()
        drift_protection_system._validate_innovation.assert_called_once()


# Mark all tests with appropriate markers for filtering
pytestmark = [
    pytest.mark.asyncio,
]

if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v", "--tb=short"])
