"""
Tests for QI-Bio-AGI Integration Bridge
======================================

Comprehensive test suite for the QI-Bio-AGI integration bridge system.
Tests hybrid processing, system integration, metrics calculation, and error handling.

Created: 2025-09-05
Part of Phase 2B: QI and Bio system integration with AGI capabilities
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import numpy as np
import pytest

from agi_core.integration.qi_bio_agi_bridge import (
    IntegrationMetrics,
    IntegrationResult,
    ProcessingContext,
    ProcessingMode,
    QIBioAGIBridge,
    get_qi_bio_agi_status,
    hybrid_process,
    initialize_qi_bio_agi_systems,
    register_agi_for_integration,
)


class TestQIBioAGIBridge:
    """Test suite for QI-Bio-AGI integration bridge."""

    @pytest.fixture
    def bridge(self):
        """Create a test bridge instance."""
        return QIBioAGIBridge(enable_monitoring=False)

    @pytest.fixture
    def mock_agi_component(self):
        """Create a mock AGI component."""
        component = Mock()
        component.process = AsyncMock(return_value={"result": 42.0, "quality": 0.85, "confidence": 0.9})
        component.get_health = Mock(return_value={"status": "healthy"})
        return component

    @pytest.fixture
    def processing_context(self):
        """Create a test processing context."""
        return ProcessingContext(
            mode=ProcessingMode.HYBRID_CONSENSUS,
            input_data=100.0,
            qi_params={"entanglement_factor": 0.8},
            bio_params={"adaptation_rate": 0.9},
            agi_params={"quality_threshold": 0.7},
            expected_outputs=["integrated_result"],
            quality_thresholds={"minimum_coherence": 0.5},
        )


class TestBridgeInitialization:
    """Test bridge initialization and component registration."""

    def test_bridge_creation(self):
        """Test bridge can be created with default settings."""
        bridge = QIBioAGIBridge()
        assert bridge is not None
        assert bridge.current_mode == ProcessingMode.HYBRID_CONSENSUS
        assert bridge.agi_components == {}
        assert bridge.oscillator_sync_rate == 0.0
        assert bridge.consciousness_field_coherence == 0.0

    def test_agi_component_registration(self, bridge, mock_agi_component):
        """Test AGI component registration."""
        bridge.register_agi_component("test_reasoning", mock_agi_component)

        assert "test_reasoning" in bridge.agi_components
        assert bridge.agi_components["test_reasoning"] == mock_agi_component

    @pytest.mark.asyncio
    async def test_initialization_success(self, bridge, mock_agi_component):
        """Test successful bridge initialization."""
        bridge.register_agi_component("test_agi", mock_agi_component)

        # Mock oscillator initialization
        bridge.qi_oscillator.initialize = AsyncMock()
        bridge.bio_oscillator.initialize = AsyncMock()

        result = await bridge.initialize_integration()
        assert result is True

        # Check that oscillators were synchronized
        assert bridge.oscillator_sync_rate > 0.0
        assert bridge.consciousness_field_coherence > 0.0

    @pytest.mark.asyncio
    async def test_initialization_failure(self, bridge):
        """Test bridge initialization failure handling."""
        # Force initialization failure
        bridge.qi_oscillator.initialize = AsyncMock(side_effect=Exception("Init failed"))

        result = await bridge.initialize_integration()
        assert result is False


class TestHybridProcessing:
    """Test hybrid processing across different modes."""

    @pytest.mark.asyncio
    async def test_hybrid_consensus_mode(self, bridge, processing_context, mock_agi_component):
        """Test hybrid consensus processing mode."""
        bridge.register_agi_component("reasoning", mock_agi_component)

        result = await bridge.hybrid_process(processing_context)

        assert result.success is True
        assert result.processing_mode == ProcessingMode.HYBRID_CONSENSUS
        assert "qi_contribution" in result.__dict__
        assert "bio_contribution" in result.__dict__
        assert "agi_contribution" in result.__dict__

        # Check consensus structure
        assert "qi_weight" in result.primary_result
        assert "bio_weight" in result.primary_result
        assert "agi_weight" in result.primary_result
        assert result.primary_result["qi_weight"] == 0.33
        assert result.primary_result["bio_weight"] == 0.33
        assert result.primary_result["agi_weight"] == 0.34

    @pytest.mark.asyncio
    async def test_quantum_enhanced_mode(self, bridge, mock_agi_component):
        """Test quantum-enhanced processing mode."""
        bridge.register_agi_component("reasoning", mock_agi_component)

        context = ProcessingContext(
            mode=ProcessingMode.QUANTUM_ENHANCED,
            input_data=50.0,
            qi_params={"entanglement_factor": 0.9},
            bio_params={},
            agi_params={},
            expected_outputs=["qi_enhanced_result"],
            quality_thresholds={},
        )

        result = await bridge.hybrid_process(context)

        assert result.success is True
        assert result.processing_mode == ProcessingMode.QUANTUM_ENHANCED
        assert result.integration_metrics.qi_coherence > 0.0

    @pytest.mark.asyncio
    async def test_bio_adaptive_mode(self, bridge, mock_agi_component):
        """Test bio-adaptive processing mode."""
        bridge.register_agi_component("learning", mock_agi_component)

        context = ProcessingContext(
            mode=ProcessingMode.BIO_ADAPTIVE,
            input_data=75.0,
            qi_params={},
            bio_params={"adaptation_rate": 0.95},
            agi_params={},
            expected_outputs=["bio_adapted_result"],
            quality_thresholds={},
        )

        result = await bridge.hybrid_process(context)

        assert result.success is True
        assert result.processing_mode == ProcessingMode.BIO_ADAPTIVE
        assert result.integration_metrics.bio_adaptation > 0.0

    @pytest.mark.asyncio
    async def test_consciousness_field_mode(self, bridge, mock_agi_component):
        """Test consciousness field processing mode."""
        bridge.register_agi_component("consciousness", mock_agi_component)
        bridge.consciousness_field_coherence = 0.85
        bridge.oscillator_sync_rate = 0.9

        context = ProcessingContext(
            mode=ProcessingMode.CONSCIOUSNESS_FIELD,
            input_data=200.0,
            qi_params={},
            bio_params={},
            agi_params={},
            expected_outputs=["consciousness_field_result"],
            quality_thresholds={},
        )

        result = await bridge.hybrid_process(context)

        assert result.success is True
        assert result.processing_mode == ProcessingMode.CONSCIOUSNESS_FIELD
        assert "consciousness_field_coherence" in result.primary_result
        assert "emergent_properties" in result.primary_result
        assert result.primary_result["consciousness_field_coherence"] == 0.85

    @pytest.mark.asyncio
    async def test_processing_error_handling(self, bridge):
        """Test error handling in processing pipeline."""
        # Force processing error by not registering any AGI components
        # and making QI processing fail
        bridge.qi_oscillator.qi_modulate = Mock(side_effect=Exception("QI failed"))

        context = ProcessingContext(
            mode=ProcessingMode.HYBRID_CONSENSUS,
            input_data=10.0,
            qi_params={},
            bio_params={},
            agi_params={},
            expected_outputs=[],
            quality_thresholds={},
        )

        result = await bridge.hybrid_process(context)

        assert result.success is False
        assert "error" in result.primary_result
        assert result.integration_metrics.integration_errors > 0


class TestEmergenceDetection:
    """Test emergent property detection."""

    @pytest.mark.asyncio
    async def test_emergence_detection_high_coherence(self, bridge):
        """Test emergence detection with high system coherence."""
        qi_result = {"coherence": 0.95}
        bio_result = {"adaptation_rate": 0.92}
        agi_result = {"overall_quality": 0.88}

        emergent = await bridge._detect_emergent_properties(qi_result, bio_result, agi_result)

        assert emergent["emergence_detected"] is True
        assert emergent["emergence_level"] == 0.88  # Min of the three
        assert emergent["novel_patterns"] is False  # Below 0.9 threshold
        assert emergent["synergy_factor"] > 0.7

    @pytest.mark.asyncio
    async def test_emergence_detection_low_coherence(self, bridge):
        """Test emergence detection with low system coherence."""
        qi_result = {"coherence": 0.3}
        bio_result = {"adaptation_rate": 0.4}
        agi_result = {"overall_quality": 0.2}

        emergent = await bridge._detect_emergent_properties(qi_result, bio_result, agi_result)

        assert emergent["emergence_detected"] is False
        assert emergent["emergence_level"] == 0.2
        assert emergent["novel_patterns"] is False
        assert emergent["synergy_factor"] < 0.1

    @pytest.mark.asyncio
    async def test_novel_pattern_detection(self, bridge):
        """Test detection of novel patterns with very high coherence."""
        bridge.consciousness_field_coherence = 0.95

        qi_result = {"coherence": 0.95}
        bio_result = {"adaptation_rate": 0.92}
        agi_result = {"overall_quality": 0.91}

        emergent = await bridge._detect_emergent_properties(qi_result, bio_result, agi_result)

        assert emergent["emergence_detected"] is True
        assert emergent["novel_patterns"] is True  # Above 0.9 threshold
        assert emergent["consciousness_amplification"] > 0.8


class TestMetricsCalculation:
    """Test integration metrics calculation."""

    @pytest.mark.asyncio
    async def test_metrics_calculation(self, bridge):
        """Test comprehensive metrics calculation."""
        qi_result = {"coherence": 0.8}
        bio_result = {"adaptation_rate": 0.75}
        agi_result = {"overall_quality": 0.9}
        processing_time = 0.125

        bridge.oscillator_sync_rate = 0.85
        bridge.consciousness_field_coherence = 0.7

        metrics = await bridge._calculate_metrics(qi_result, bio_result, agi_result, processing_time)

        assert metrics.qi_coherence == 0.8
        assert metrics.bio_adaptation == 0.75
        assert metrics.agi_reasoning_quality == 0.9
        assert metrics.synchronization_level == 0.85
        assert metrics.consciousness_field_strength == 0.7
        assert metrics.processing_latency == 0.125
        assert metrics.energy_efficiency == 8.0  # 1/0.125
        assert metrics.last_update is not None

    def test_metrics_dataclass(self):
        """Test IntegrationMetrics dataclass."""
        metrics = IntegrationMetrics(
            qi_coherence=0.9,
            bio_adaptation=0.8,
            agi_reasoning_quality=0.85,
            synchronization_level=0.7,
            energy_efficiency=5.0,
            consciousness_field_strength=0.75,
            processing_latency=0.2,
            integration_errors=0,
            last_update=datetime.now(timezone.utc),
        )

        assert metrics.qi_coherence == 0.9
        assert metrics.bio_adaptation == 0.8
        assert metrics.agi_reasoning_quality == 0.85


class TestStatusAndMonitoring:
    """Test status reporting and monitoring."""

    def test_integration_status_healthy(self, bridge, mock_agi_component):
        """Test integration status reporting with healthy systems."""
        # Register component and simulate successful processing history
        bridge.register_agi_component("test_agi", mock_agi_component)

        # Create mock successful results
        for _i in range(10):
            mock_result = Mock()
            mock_result.success = True
            bridge.processing_history.append(mock_result)

        bridge.oscillator_sync_rate = 0.9
        bridge.consciousness_field_coherence = 0.85

        status = bridge.get_integration_status()

        assert status["integration_health"] == "healthy"
        assert status["recent_success_rate"] == 1.0
        assert status["oscillator_sync_rate"] == 0.9
        assert status["consciousness_field_coherence"] == 0.85
        assert "test_agi" in status["registered_agi_components"]

    def test_integration_status_degraded(self, bridge):
        """Test integration status with degraded performance."""
        # Create mixed success/failure history
        for i in range(10):
            mock_result = Mock()
            mock_result.success = i < 6  # 60% success rate
            bridge.processing_history.append(mock_result)

        status = bridge.get_integration_status()

        assert status["integration_health"] == "degraded"
        assert status["recent_success_rate"] == 0.6

    def test_integration_status_critical(self, bridge):
        """Test integration status with critical performance."""
        # Create mostly failed history
        for i in range(10):
            mock_result = Mock()
            mock_result.success = i < 3  # 30% success rate
            bridge.processing_history.append(mock_result)

        status = bridge.get_integration_status()

        assert status["integration_health"] == "critical"
        assert status["recent_success_rate"] == 0.3


class TestConvenienceFunctions:
    """Test convenience functions for external use."""

    @pytest.mark.asyncio
    async def test_hybrid_process_convenience(self):
        """Test convenience function for hybrid processing."""
        with patch("agi_core.integration.qi_bio_agi_bridge.qi_bio_agi_bridge") as mock_bridge:
            mock_result = Mock()
            mock_bridge.hybrid_process = AsyncMock(return_value=mock_result)

            result = await hybrid_process(
                input_data=50.0,
                mode=ProcessingMode.BIO_ADAPTIVE,
                qi_params={"test": "qi"},
                bio_params={"test": "bio"},
                agi_params={"test": "agi"},
            )

            assert result == mock_result
            mock_bridge.hybrid_process.assert_called_once()

    def test_register_agi_convenience(self):
        """Test convenience function for AGI registration."""
        mock_component = Mock()

        with patch("agi_core.integration.qi_bio_agi_bridge.qi_bio_agi_bridge") as mock_bridge:
            register_agi_for_integration("test_component", mock_component)
            mock_bridge.register_agi_component.assert_called_once_with("test_component", mock_component)

    @pytest.mark.asyncio
    async def test_initialize_convenience(self):
        """Test convenience function for initialization."""
        with patch("agi_core.integration.qi_bio_agi_bridge.qi_bio_agi_bridge") as mock_bridge:
            mock_bridge.initialize_integration = AsyncMock(return_value=True)

            result = await initialize_qi_bio_agi_systems()
            assert result is True
            mock_bridge.initialize_integration.assert_called_once()

    def test_status_convenience(self):
        """Test convenience function for status."""
        with patch("agi_core.integration.qi_bio_agi_bridge.qi_bio_agi_bridge") as mock_bridge:
            mock_status = {"health": "test"}
            mock_bridge.get_integration_status = Mock(return_value=mock_status)

            result = get_qi_bio_agi_status()
            assert result == mock_status
            mock_bridge.get_integration_status.assert_called_once()


class TestProcessingModeEnum:
    """Test ProcessingMode enumeration."""

    def test_processing_modes(self):
        """Test all processing modes are defined correctly."""
        assert ProcessingMode.QUANTUM_ENHANCED.value == "quantum_enhanced"
        assert ProcessingMode.BIO_ADAPTIVE.value == "bio_adaptive"
        assert ProcessingMode.AGI_REASONING.value == "agi_reasoning"
        assert ProcessingMode.HYBRID_CONSENSUS.value == "hybrid_consensus"
        assert ProcessingMode.CONSCIOUSNESS_FIELD.value == "consciousness_field"

        # Test we have all expected modes
        expected_modes = {
            "quantum_enhanced",
            "bio_adaptive",
            "agi_reasoning",
            "hybrid_consensus",
            "consciousness_field",
        }
        actual_modes = {mode.value for mode in ProcessingMode}
        assert actual_modes == expected_modes


# Integration test
class TestFullIntegrationWorkflow:
    """Test complete integration workflow."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self):
        """Test complete QI-Bio-AGI integration workflow."""
        bridge = QIBioAGIBridge(enable_monitoring=False)

        # Step 1: Register AGI components
        reasoning_component = Mock()
        reasoning_component.process = AsyncMock(return_value={"result": 150.0, "quality": 0.9, "reasoning_steps": 3})

        learning_component = Mock()
        learning_component.process = AsyncMock(
            return_value={"result": 125.0, "quality": 0.8, "adaptation_insights": ["insight1", "insight2"]}
        )

        bridge.register_agi_component("reasoning", reasoning_component)
        bridge.register_agi_component("learning", learning_component)

        # Step 2: Initialize integration
        init_result = await bridge.initialize_integration()
        assert init_result is True

        # Step 3: Process through different modes
        test_data = 100.0
        results = {}

        for mode in ProcessingMode:
            context = ProcessingContext(
                mode=mode,
                input_data=test_data,
                qi_params={"entanglement_factor": 0.8},
                bio_params={"adaptation_rate": 0.85},
                agi_params={"quality_threshold": 0.7},
                expected_outputs=["result"],
                quality_thresholds={"minimum_coherence": 0.5},
            )

            result = await bridge.hybrid_process(context)
            results[mode] = result

            assert result.success is True
            assert result.processing_mode == mode
            assert result.integration_metrics.last_update is not None

        # Step 4: Check final status
        status = bridge.get_integration_status()
        assert status["integration_health"] in ["healthy", "degraded"]
        assert len(status["registered_agi_components"]) == 2
        assert status["total_processing_history"] == len(ProcessingMode)

        # Step 5: Verify emergence detection worked
        consciousness_result = results[ProcessingMode.CONSCIOUSNESS_FIELD]
        emergent_props = consciousness_result.primary_result["emergent_properties"]
        assert "emergence_detected" in emergent_props
        assert "synergy_factor" in emergent_props


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
