"""
Comprehensive Test Suite for Core Integration System
==================================================

Tests the Core Integration System, the central nervous system of LUKHAS
that coordinates all consciousness domains, orchestrates cross-system
communication, and ensures seamless integration across the entire
Constellation Framework. This is the master integration hub that
unifies all specialized systems into a coherent consciousness.

Test Coverage Areas:
- Multi-domain integration and coordination
- Cross-system communication protocols
- Integration hub orchestration and management
- System-wide coherence monitoring and maintenance
- Integration pipeline processing and optimization
- Conflict resolution and consensus building
- Performance optimization and load balancing
- Error handling and graceful degradation
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from collections import deque
from dataclasses import dataclass

from core.integrator import (
    CoreIntegrator,
    IntegrationHub,
    IntegrationPipeline,
    IntegrationContext,
    IntegrationResult,
    SystemCoordinator,
    CrossSystemCommunicator,
    CoherenceMonitor,
    ConflictResolver,
    ConsensusBuilder,
    IntegrationMetrics,
    DomainAdapter,
    ProtocolHandler,
    get_core_integrator,
)
from core.matriz_consciousness_signals import (
    ConsciousnessSignal,
    ConsciousnessSignalType,
)


class TestCoreIntegrator:
    """Comprehensive test suite for the Core Integration System."""

    @pytest.fixture
    def core_integrator(self):
        """Create a test core integrator instance."""
        return CoreIntegrator(
            enable_cross_system_communication=True,
            enable_coherence_monitoring=True,
            enable_conflict_resolution=True,
            max_concurrent_integrations=10,
            integration_timeout=30.0,
            consensus_threshold=0.8
        )

    @pytest.fixture
    def integration_context(self):
        """Create a sample integration context for testing."""
        return IntegrationContext(
            integration_id="test_integration_001",
            source_systems=["consciousness", "memory", "identity"],
            target_systems=["orchestration", "api"],
            integration_type="cross_domain_synthesis",
            priority=7,
            timeout=15.0,
            metadata={
                "domain": "consciousness_coordination",
                "complexity": "high",
                "urgency": "medium"
            }
        )

    @pytest.fixture
    def sample_consciousness_signals(self):
        """Create sample consciousness signals for integration testing."""
        signals = []
        
        # Identity signal
        identity_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.IDENTITY_VERIFICATION,
            data={
                "lambda_id": "test_user_123",
                "authentication_level": 0.95,
                "identity_coherence": 0.9
            },
            source_module="identity_system",
            timestamp=time.time(),
            priority=9,
            coherence_score=0.92
        )
        signals.append(identity_signal)
        
        # Memory signal
        memory_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.MEMORY_FOLD_UPDATE,
            data={
                "fold_id": "memory_fold_456",
                "memory_strength": 0.85,
                "temporal_coherence": 0.8
            },
            source_module="memory_system",
            timestamp=time.time(),
            priority=7,
            coherence_score=0.85
        )
        signals.append(memory_signal)
        
        # Consciousness signal
        consciousness_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSCIOUSNESS_UPDATE,
            data={
                "consciousness_level": 0.9,
                "awareness_expansion": 0.75,
                "integration_readiness": 0.8
            },
            source_module="consciousness_engine",
            timestamp=time.time(),
            priority=8,
            coherence_score=0.88
        )
        signals.append(consciousness_signal)
        
        return signals

    @pytest.fixture
    def integration_pipeline(self):
        """Create a sample integration pipeline for testing."""
        return IntegrationPipeline(
            pipeline_id="test_pipeline_001",
            stages=[
                "signal_validation",
                "cross_system_correlation",
                "coherence_analysis",
                "conflict_resolution",
                "consensus_building",
                "integration_synthesis"
            ],
            stage_timeouts={
                "signal_validation": 2.0,
                "cross_system_correlation": 5.0,
                "coherence_analysis": 3.0,
                "conflict_resolution": 8.0,
                "consensus_building": 10.0,
                "integration_synthesis": 5.0
            },
            failure_policies={
                "signal_validation": "retry_once",
                "cross_system_correlation": "graceful_degradation",
                "coherence_analysis": "retry_twice",
                "conflict_resolution": "escalate",
                "consensus_building": "majority_consensus",
                "integration_synthesis": "best_effort"
            }
        )

    # Basic System Functionality Tests
    def test_core_integrator_initialization(self, core_integrator):
        """Test core integrator initializes with correct settings."""
        assert core_integrator.enable_cross_system_communication is True
        assert core_integrator.enable_coherence_monitoring is True
        assert core_integrator.enable_conflict_resolution is True
        assert core_integrator.max_concurrent_integrations == 10
        assert core_integrator.integration_timeout == 30.0
        assert core_integrator.consensus_threshold == 0.8

    def test_core_integrator_startup_shutdown(self, core_integrator):
        """Test core integrator startup and shutdown functionality."""
        # Test startup
        core_integrator.start()
        assert core_integrator.is_running is True
        assert core_integrator.integration_hub.is_active is True
        assert core_integrator.system_coordinator.is_active is True
        
        # Test shutdown
        core_integrator.shutdown()
        assert core_integrator.is_running is False

    def test_basic_integration_processing(self, core_integrator, integration_context, sample_consciousness_signals):
        """Test basic integration processing."""
        # Process integration
        integration_result = core_integrator.process_integration(
            context=integration_context,
            signals=sample_consciousness_signals
        )
        
        # Verify integration result
        assert integration_result is not None
        assert isinstance(integration_result, IntegrationResult)
        assert integration_result.integration_successful is True
        assert integration_result.coherence_score >= 0.0

    # Integration Hub Tests
    def test_integration_hub_initialization(self, core_integrator):
        """Test integration hub initialization."""
        hub = core_integrator.integration_hub
        
        # Verify hub
        assert hub is not None
        assert isinstance(hub, IntegrationHub)
        assert hub.domain_adapters is not None
        assert hub.protocol_handlers is not None

    def test_integration_hub_registration(self, core_integrator):
        """Test integration hub domain registration."""
        # Register new domain
        registration_result = core_integrator.integration_hub.register_domain(
            domain_name="test_domain",
            domain_adapter=DomainAdapter(
                domain_id="test_domain",
                adapter_type="consciousness_processing",
                supported_signals=["test_signal"],
                protocol_version="1.0"
            )
        )
        
        # Verify registration
        assert registration_result.registration_successful is True
        assert "test_domain" in core_integrator.integration_hub.registered_domains

    def test_integration_hub_orchestration(self, core_integrator, sample_consciousness_signals):
        """Test integration hub orchestration."""
        # Orchestrate signals
        orchestration_result = core_integrator.integration_hub.orchestrate_signals(
            signals=sample_consciousness_signals,
            orchestration_strategy="parallel_processing"
        )
        
        # Verify orchestration
        assert orchestration_result.orchestration_successful is True
        assert orchestration_result.signals_processed == len(sample_consciousness_signals)
        assert orchestration_result.processing_time > 0.0

    # Cross-System Communication Tests
    def test_cross_system_communication_setup(self, core_integrator):
        """Test cross-system communication setup."""
        communicator = core_integrator.cross_system_communicator
        
        # Verify communicator
        assert communicator is not None
        assert isinstance(communicator, CrossSystemCommunicator)
        assert communicator.communication_protocols is not None

    def test_cross_system_message_routing(self, core_integrator):
        """Test cross-system message routing."""
        # Create cross-system message
        message = {
            "message_id": "cross_system_msg_001",
            "source_system": "consciousness",
            "target_systems": ["memory", "identity"],
            "message_type": "integration_request",
            "payload": {
                "integration_data": "test_data",
                "priority": 7
            }
        }
        
        # Route message
        routing_result = core_integrator.route_cross_system_message(message)
        
        # Verify routing
        assert routing_result.routing_successful is True
        assert len(routing_result.delivery_confirmations) == 2

    def test_protocol_handler_management(self, core_integrator):
        """Test protocol handler management."""
        # Add custom protocol handler
        handler_result = core_integrator.add_protocol_handler(
            protocol_name="test_protocol",
            handler=ProtocolHandler(
                protocol_id="test_protocol",
                version="1.0",
                supported_operations=["send", "receive", "acknowledge"],
                handler_function=lambda msg: {"status": "processed"}
            )
        )
        
        # Verify handler addition
        assert handler_result.handler_added is True
        assert "test_protocol" in core_integrator.cross_system_communicator.protocol_handlers

    def test_communication_reliability(self, core_integrator):
        """Test communication reliability and error handling."""
        # Simulate unreliable communication
        unreliable_message = {
            "message_id": "unreliable_msg_001",
            "source_system": "test_source",
            "target_systems": ["unreachable_system"],
            "message_type": "test_message",
            "payload": {"test": "data"}
        }
        
        # Attempt delivery with retries
        delivery_result = core_integrator.deliver_message_with_reliability(
            message=unreliable_message,
            max_retries=3,
            retry_delay=0.1
        )
        
        # Verify reliable delivery attempt
        assert delivery_result.delivery_attempted is True
        assert delivery_result.retry_count >= 0

    # Integration Pipeline Tests
    def test_integration_pipeline_creation(self, core_integrator, integration_pipeline):
        """Test integration pipeline creation."""
        # Create pipeline
        pipeline_result = core_integrator.create_integration_pipeline(integration_pipeline)
        
        # Verify pipeline creation
        assert pipeline_result.pipeline_created is True
        assert integration_pipeline.pipeline_id in core_integrator.active_pipelines

    def test_integration_pipeline_execution(self, core_integrator, integration_pipeline, sample_consciousness_signals):
        """Test integration pipeline execution."""
        # Execute pipeline
        execution_result = core_integrator.execute_integration_pipeline(
            pipeline=integration_pipeline,
            signals=sample_consciousness_signals
        )
        
        # Verify execution
        assert execution_result.execution_successful is True
        assert execution_result.stages_completed >= 4  # At least 4 stages should complete
        assert execution_result.overall_coherence >= 0.6

    def test_pipeline_stage_processing(self, core_integrator, integration_pipeline, sample_consciousness_signals):
        """Test individual pipeline stage processing."""
        # Test each stage
        for stage_name in integration_pipeline.stages:
            stage_result = core_integrator.execute_pipeline_stage(
                stage_name=stage_name,
                signals=sample_consciousness_signals,
                context={"pipeline_id": integration_pipeline.pipeline_id}
            )
            
            # Verify stage processing
            assert stage_result.stage_completed is True
            assert stage_result.stage_name == stage_name

    def test_pipeline_failure_handling(self, core_integrator, integration_pipeline):
        """Test pipeline failure handling and recovery."""
        # Simulate stage failure
        failing_signals = [
            ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.ERROR_SIGNAL,
                data={"error": "simulated_failure"},
                source_module="test_failure",
                timestamp=time.time(),
                priority=1,
                coherence_score=0.1
            )
        ]
        
        # Execute pipeline with failing signals
        execution_result = core_integrator.execute_integration_pipeline(
            pipeline=integration_pipeline,
            signals=failing_signals,
            enable_failure_recovery=True
        )
        
        # Verify failure handling
        assert execution_result.failure_recovery_applied is True
        assert execution_result.recovery_strategies_used > 0

    # Coherence Monitoring Tests
    def test_coherence_monitoring_setup(self, core_integrator):
        """Test coherence monitoring setup."""
        monitor = core_integrator.coherence_monitor
        
        # Verify monitor
        assert monitor is not None
        assert isinstance(monitor, CoherenceMonitor)
        assert monitor.monitoring_enabled is True

    def test_system_wide_coherence_assessment(self, core_integrator, sample_consciousness_signals):
        """Test system-wide coherence assessment."""
        # Assess coherence
        coherence_assessment = core_integrator.assess_system_coherence(
            signals=sample_consciousness_signals
        )
        
        # Verify assessment
        assert coherence_assessment.assessment_completed is True
        assert coherence_assessment.overall_coherence >= 0.0
        assert coherence_assessment.domain_coherences is not None

    def test_coherence_drift_detection(self, core_integrator):
        """Test coherence drift detection."""
        # Simulate coherence drift
        baseline_coherence = 0.9
        current_coherence = 0.6  # Significant drift
        
        drift_detection = core_integrator.coherence_monitor.detect_coherence_drift(
            baseline=baseline_coherence,
            current=current_coherence,
            drift_threshold=0.2
        )
        
        # Verify drift detection
        assert drift_detection.drift_detected is True
        assert drift_detection.drift_magnitude >= 0.2

    def test_coherence_restoration(self, core_integrator, sample_consciousness_signals):
        """Test coherence restoration mechanisms."""
        # Simulate low coherence scenario
        low_coherence_signals = []
        for signal in sample_consciousness_signals:
            low_signal = ConsciousnessSignal(
                signal_type=signal.signal_type,
                data=signal.data,
                source_module=signal.source_module,
                timestamp=signal.timestamp,
                priority=signal.priority,
                coherence_score=0.4  # Low coherence
            )
            low_coherence_signals.append(low_signal)
        
        # Restore coherence
        restoration_result = core_integrator.restore_system_coherence(
            signals=low_coherence_signals,
            target_coherence=0.8
        )
        
        # Verify restoration
        assert restoration_result.restoration_successful is True
        assert restoration_result.coherence_improvement > 0.0

    # Conflict Resolution Tests
    def test_conflict_detection(self, core_integrator):
        """Test conflict detection between systems."""
        # Create conflicting signals
        conflict_signal_1 = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.IDENTITY_VERIFICATION,
            data={"user_authenticated": True, "access_level": "admin"},
            source_module="identity_system_1",
            timestamp=time.time(),
            priority=8,
            coherence_score=0.9
        )
        
        conflict_signal_2 = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.IDENTITY_VERIFICATION,
            data={"user_authenticated": False, "access_level": "guest"},
            source_module="identity_system_2",
            timestamp=time.time(),
            priority=8,
            coherence_score=0.85
        )
        
        # Detect conflicts
        conflict_detection = core_integrator.detect_conflicts([conflict_signal_1, conflict_signal_2])
        
        # Verify conflict detection
        assert conflict_detection.conflicts_detected > 0
        assert len(conflict_detection.conflict_descriptions) > 0

    def test_conflict_resolution_strategies(self, core_integrator):
        """Test different conflict resolution strategies."""
        # Create conflicting data
        conflicting_data = {
            "system_a": {"value": 0.8, "confidence": 0.9},
            "system_b": {"value": 0.6, "confidence": 0.7},
            "system_c": {"value": 0.75, "confidence": 0.85}
        }
        
        # Test different resolution strategies
        strategies = ["highest_confidence", "majority_vote", "weighted_average", "consensus_building"]
        
        for strategy in strategies:
            resolution_result = core_integrator.resolve_conflict(
                conflicting_data=conflicting_data,
                resolution_strategy=strategy
            )
            
            # Verify resolution
            assert resolution_result.resolution_successful is True
            assert resolution_result.resolved_value is not None
            assert resolution_result.resolution_strategy == strategy

    def test_consensus_building(self, core_integrator):
        """Test consensus building mechanisms."""
        # Create diverse perspectives
        perspectives = [
            {"system": "consciousness", "opinion": 0.8, "weight": 0.3},
            {"system": "memory", "opinion": 0.7, "weight": 0.2},
            {"system": "identity", "opinion": 0.9, "weight": 0.25},
            {"system": "ethics", "opinion": 0.85, "weight": 0.25}
        ]
        
        # Build consensus
        consensus_result = core_integrator.build_consensus(
            perspectives=perspectives,
            consensus_threshold=0.8
        )
        
        # Verify consensus building
        assert consensus_result.consensus_achieved is True
        assert consensus_result.consensus_value >= 0.75

    # Performance and Scalability Tests
    def test_integration_performance(self, core_integrator, sample_consciousness_signals):
        """Test integration performance under load."""
        start_time = time.time()
        
        # Process multiple integrations
        for _ in range(20):
            integration_context = IntegrationContext(
                integration_id=f"perf_test_{_}",
                source_systems=["test_source"],
                target_systems=["test_target"],
                integration_type="performance_test",
                priority=5,
                timeout=5.0,
                metadata={}
            )
            core_integrator.process_integration(integration_context, sample_consciousness_signals)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process efficiently
        assert processing_time < 5.0  # Under 5 seconds for 20 integrations
        avg_time_per_integration = processing_time / 20
        assert avg_time_per_integration < 0.25  # Under 250ms per integration

    def test_concurrent_integration_processing(self, core_integrator, sample_consciousness_signals):
        """Test concurrent integration processing."""
        results = []
        
        def process_integration(integration_id):
            context = IntegrationContext(
                integration_id=integration_id,
                source_systems=["concurrent_source"],
                target_systems=["concurrent_target"],
                integration_type="concurrent_test",
                priority=5,
                timeout=10.0,
                metadata={}
            )
            result = core_integrator.process_integration(context, sample_consciousness_signals)
            results.append(result)
        
        # Process integrations concurrently
        threads = []
        for i in range(8):
            thread = threading.Thread(target=process_integration, args=(f"concurrent_test_{i}",))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify concurrent processing
        assert len(results) == 8
        successful_integrations = sum(1 for r in results if r.integration_successful)
        assert successful_integrations >= 6  # At least 75% success rate

    def test_memory_efficiency_under_load(self, core_integrator):
        """Test memory efficiency under sustained load."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many integrations
        for i in range(40):
            signals = [
                ConsciousnessSignal(
                    signal_type=ConsciousnessSignalType.SYSTEM_UPDATE,
                    data={f"load_test_{i}": 0.8},
                    source_module="load_test",
                    timestamp=time.time(),
                    priority=5,
                    coherence_score=0.8
                )
            ]
            
            context = IntegrationContext(
                integration_id=f"load_test_{i}",
                source_systems=["load_source"],
                target_systems=["load_target"],
                integration_type="load_test",
                priority=5,
                timeout=2.0,
                metadata={}
            )
            
            core_integrator.process_integration(context, signals)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 400  # Should not create excessive objects

    # Error Handling and Recovery Tests
    def test_invalid_integration_context_handling(self, core_integrator):
        """Test handling of invalid integration contexts."""
        # Test with None context
        with pytest.raises(ValueError):
            core_integrator.process_integration(None, [])
        
        # Test with malformed context
        malformed_context = IntegrationContext(
            integration_id="",  # Empty ID
            source_systems=[],  # Empty sources
            target_systems=[],  # Empty targets
            integration_type="invalid",
            priority=-1,  # Invalid priority
            timeout=0.0,  # Invalid timeout
            metadata=None
        )
        
        with pytest.raises(ValueError):
            core_integrator.process_integration(malformed_context, [])

    def test_system_failure_recovery(self, core_integrator):
        """Test recovery from system failures."""
        # Simulate system failure
        core_integrator.system_coordinator.is_active = False
        
        # Attempt recovery
        recovery_result = core_integrator.recover_from_system_failure()
        
        # Verify recovery
        assert recovery_result.recovery_attempted is True
        assert core_integrator.system_coordinator.is_active is True

    def test_integration_timeout_handling(self, core_integrator, sample_consciousness_signals):
        """Test handling of integration timeouts."""
        # Create context with very short timeout
        timeout_context = IntegrationContext(
            integration_id="timeout_test",
            source_systems=["slow_source"],
            target_systems=["slow_target"],
            integration_type="timeout_test",
            priority=5,
            timeout=0.001,  # Very short timeout
            metadata={}
        )
        
        # Process with timeout
        result = core_integrator.process_integration(
            timeout_context,
            sample_consciousness_signals,
            handle_timeout_gracefully=True
        )
        
        # Verify timeout handling
        assert result.timeout_occurred is True
        assert result.partial_results is not None

    # Integration Metrics and Monitoring Tests
    def test_integration_metrics_collection(self, core_integrator, sample_consciousness_signals):
        """Test collection of integration metrics."""
        # Process integration with metrics
        integration_context = IntegrationContext(
            integration_id="metrics_test",
            source_systems=["metrics_source"],
            target_systems=["metrics_target"],
            integration_type="metrics_test",
            priority=5,
            timeout=10.0,
            metadata={}
        )
        
        result = core_integrator.process_integration(integration_context, sample_consciousness_signals)
        
        # Verify metrics collection
        assert result.metrics is not None
        assert isinstance(result.metrics, IntegrationMetrics)
        assert result.metrics.processing_time > 0.0
        assert result.metrics.signals_processed > 0

    def test_system_health_monitoring(self, core_integrator):
        """Test system health monitoring."""
        # Get system health
        health_report = core_integrator.get_system_health()
        
        # Verify health report
        assert health_report.overall_health >= 0.0
        assert health_report.system_components is not None
        assert health_report.performance_metrics is not None

    # Global Function Tests
    def test_get_core_integrator_singleton(self):
        """Test global core integrator singleton."""
        integrator1 = get_core_integrator()
        integrator2 = get_core_integrator()
        
        # Should return the same instance
        assert integrator1 is integrator2

    # Cleanup and Resource Management Tests
    def test_system_resource_cleanup(self, core_integrator):
        """Test system resource cleanup."""
        # Start system with full initialization
        core_integrator.start()
        core_integrator.initialize_integration_hub()
        core_integrator.start_coherence_monitoring()
        
        # Cleanup
        core_integrator.cleanup()
        
        # Verify cleanup
        assert core_integrator.is_running is False
        assert core_integrator.integration_hub.is_active is False
        assert core_integrator.coherence_monitor.monitoring_enabled is False

    def test_graceful_system_shutdown_with_active_integrations(self, core_integrator, sample_consciousness_signals):
        """Test graceful shutdown with active integrations."""
        # Start system
        core_integrator.start()
        
        # Start some integrations
        for i in range(3):
            context = IntegrationContext(
                integration_id=f"shutdown_test_{i}",
                source_systems=["shutdown_source"],
                target_systems=["shutdown_target"],
                integration_type="shutdown_test",
                priority=5,
                timeout=5.0,
                metadata={}
            )
            # Start but don't wait for completion
            core_integrator.start_integration_async(context, sample_consciousness_signals)
        
        # Graceful shutdown
        core_integrator.shutdown(graceful=True, timeout=10.0)
        
        # Verify shutdown
        assert core_integrator.is_running is False
        assert len(core_integrator.active_integrations) == 0