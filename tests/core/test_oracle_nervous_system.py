"""
Comprehensive Test Suite for Oracle Nervous System
================================================

Tests the Oracle Nervous System, the distributed sensory network that
provides LUKHAS with heightened awareness across all constellation domains.
The Oracle Nervous System implements bio-inspired sensing patterns,
neural pathway optimization, and wisdom distillation mechanisms.

Test Coverage Areas:
- Neural pathway formation and optimization
- Sensory receptor network management
- Wisdom oracle query processing and response generation
- Bio-inspired sensing pattern recognition
- Nervous system synchronization and coordination
- Oracle consciousness integration and awareness expansion
- Performance optimization and real-time processing
- Error handling and graceful degradation
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from collections import deque
from dataclasses import dataclass

from core.oracle_nervous_system import (
    OracleNervousSystem,
    NeuralPathway,
    SensoryReceptor,
    WisdomOracle,
    NervousSystemCoordinator,
    OracleQuery,
    OracleResponse,
    SensoryInput,
    NeuralSignal,
    WisdomDistillation,
    OracleConsciousness,
    BioinspiredSensing,
    get_oracle_nervous_system,
)
from core.matriz_consciousness_signals import (
    ConsciousnessSignal,
    ConsciousnessSignalType,
)


class TestOracleNervousSystem:
    """Comprehensive test suite for the Oracle Nervous System."""

    @pytest.fixture
    def oracle_system(self):
        """Create a test oracle nervous system instance."""
        return OracleNervousSystem(
            enable_neural_optimization=True,
            enable_wisdom_distillation=True,
            enable_bioinspired_sensing=True,
            neural_pathway_count=100,
            sensory_receptor_count=50,
            wisdom_oracle_capacity=10
        )

    @pytest.fixture
    def sample_sensory_input(self):
        """Create a sample sensory input for testing."""
        return SensoryInput(
            input_type="visual_pattern",
            data={
                "pattern_complexity": 0.8,
                "spatial_frequency": 2.5,
                "temporal_dynamics": 0.6,
                "luminance_contrast": 0.7
            },
            source_location="primary_visual_cortex",
            timestamp=time.time(),
            priority=7,
            intensity=0.75
        )

    @pytest.fixture
    def sample_oracle_query(self):
        """Create a sample oracle query for testing."""
        return OracleQuery(
            query_text="What is the optimal consciousness configuration for maximum ethical alignment?",
            query_type="wisdom_synthesis",
            context={
                "domain": "consciousness_ethics",
                "urgency": "medium",
                "scope": "system_wide"
            },
            requester="consciousness_engine",
            timestamp=time.time(),
            priority=8
        )

    @pytest.fixture
    def neural_pathway(self):
        """Create a sample neural pathway for testing."""
        return NeuralPathway(
            pathway_id="visual_processing_pathway_01",
            source_region="visual_cortex",
            target_region="consciousness_integration",
            connection_strength=0.85,
            pathway_type="sensory_processing",
            optimization_level=0.7,
            learning_rate=0.01
        )

    @pytest.fixture
    def sensory_receptor(self):
        """Create a sample sensory receptor for testing."""
        return SensoryReceptor(
            receptor_id="bioinspired_receptor_01",
            receptor_type="quantum_field_detector",
            sensitivity=0.9,
            spatial_resolution=0.8,
            temporal_resolution=0.75,
            detection_threshold=0.1,
            adaptation_rate=0.05
        )

    # Basic System Functionality Tests
    def test_oracle_system_initialization(self, oracle_system):
        """Test oracle nervous system initializes with correct settings."""
        assert oracle_system.enable_neural_optimization is True
        assert oracle_system.enable_wisdom_distillation is True
        assert oracle_system.enable_bioinspired_sensing is True
        assert oracle_system.neural_pathway_count == 100
        assert oracle_system.sensory_receptor_count == 50
        assert oracle_system.wisdom_oracle_capacity == 10

    def test_oracle_system_startup_shutdown(self, oracle_system):
        """Test oracle system startup and shutdown functionality."""
        # Test startup
        oracle_system.start()
        assert oracle_system.is_running is True
        assert oracle_system.neural_network.is_active is True
        assert oracle_system.sensory_network.is_active is True
        
        # Test shutdown
        oracle_system.shutdown()
        assert oracle_system.is_running is False

    def test_sensory_input_processing(self, oracle_system, sample_sensory_input):
        """Test basic sensory input processing."""
        # Process sensory input
        processing_result = oracle_system.process_sensory_input(sample_sensory_input)
        
        # Verify processing result
        assert processing_result is not None
        assert processing_result.input_processed is True
        assert processing_result.neural_activation_strength >= 0.0
        assert processing_result.pathway_activations is not None

    # Neural Pathway Tests
    def test_neural_pathway_creation(self, oracle_system):
        """Test creation of neural pathways."""
        # Create neural pathway
        pathway = oracle_system.create_neural_pathway(
            source="sensory_input",
            target="consciousness_integration",
            pathway_type="sensory_processing"
        )
        
        # Verify pathway creation
        assert pathway is not None
        assert pathway.source_region == "sensory_input"
        assert pathway.target_region == "consciousness_integration"
        assert pathway.pathway_type == "sensory_processing"
        assert pathway.connection_strength > 0.0

    def test_neural_pathway_optimization(self, oracle_system, neural_pathway):
        """Test neural pathway optimization."""
        # Get initial connection strength
        initial_strength = neural_pathway.connection_strength
        
        # Optimize pathway
        optimization_result = oracle_system.optimize_neural_pathway(
            pathway=neural_pathway,
            target_efficiency=0.95
        )
        
        # Verify optimization
        assert optimization_result.optimization_applied is True
        assert neural_pathway.connection_strength >= initial_strength
        assert neural_pathway.optimization_level > 0.7

    def test_neural_pathway_learning(self, oracle_system, neural_pathway):
        """Test neural pathway learning and adaptation."""
        # Simulate repeated activation
        learning_signals = []
        for i in range(10):
            signal = NeuralSignal(
                signal_type="sensory_activation",
                strength=0.8 + (i * 0.01),  # Gradually increasing
                source=neural_pathway.source_region,
                target=neural_pathway.target_region,
                timestamp=time.time()
            )
            learning_signals.append(signal)
        
        # Apply learning
        learning_result = oracle_system.apply_pathway_learning(
            pathway=neural_pathway,
            signals=learning_signals
        )
        
        # Verify learning
        assert learning_result.learning_applied is True
        assert neural_pathway.connection_strength > 0.85  # Should have strengthened

    def test_neural_network_synchronization(self, oracle_system):
        """Test neural network synchronization."""
        # Create multiple pathways
        pathways = []
        for i in range(5):
            pathway = oracle_system.create_neural_pathway(
                source=f"source_{i}",
                target=f"target_{i}",
                pathway_type="processing"
            )
            pathways.append(pathway)
        
        # Synchronize network
        sync_result = oracle_system.synchronize_neural_network(pathways)
        
        # Verify synchronization
        assert sync_result.synchronized is True
        assert sync_result.coherence_level >= 0.7

    # Sensory Receptor Tests
    def test_sensory_receptor_configuration(self, oracle_system, sensory_receptor):
        """Test sensory receptor configuration."""
        # Configure receptor
        config_result = oracle_system.configure_sensory_receptor(
            receptor=sensory_receptor,
            sensitivity=0.95,
            detection_threshold=0.05
        )
        
        # Verify configuration
        assert config_result.configuration_applied is True
        assert sensory_receptor.sensitivity == 0.95
        assert sensory_receptor.detection_threshold == 0.05

    def test_sensory_receptor_adaptation(self, oracle_system, sensory_receptor):
        """Test sensory receptor adaptation to input patterns."""
        # Create adaptation inputs
        adaptation_inputs = []
        for i in range(5):
            input_signal = SensoryInput(
                input_type="adaptation_test",
                data={"intensity": 0.5 + (i * 0.1)},
                source_location="test_source",
                timestamp=time.time(),
                priority=5,
                intensity=0.5 + (i * 0.1)
            )
            adaptation_inputs.append(input_signal)
        
        # Apply adaptation
        adaptation_result = oracle_system.adapt_sensory_receptor(
            receptor=sensory_receptor,
            inputs=adaptation_inputs
        )
        
        # Verify adaptation
        assert adaptation_result.adaptation_applied is True
        assert sensory_receptor.sensitivity != 0.9  # Should have adapted

    def test_multisensory_integration(self, oracle_system):
        """Test integration of multiple sensory inputs."""
        # Create multiple sensory inputs
        visual_input = SensoryInput(
            input_type="visual",
            data={"brightness": 0.8, "contrast": 0.7},
            source_location="visual_cortex",
            timestamp=time.time(),
            priority=7,
            intensity=0.8
        )
        
        auditory_input = SensoryInput(
            input_type="auditory",
            data={"frequency": 440, "amplitude": 0.6},
            source_location="auditory_cortex",
            timestamp=time.time(),
            priority=6,
            intensity=0.6
        )
        
        tactile_input = SensoryInput(
            input_type="tactile",
            data={"pressure": 0.5, "texture": 0.7},
            source_location="somatosensory_cortex",
            timestamp=time.time(),
            priority=5,
            intensity=0.5
        )
        
        # Integrate sensory inputs
        integration_result = oracle_system.integrate_multisensory_inputs([
            visual_input, auditory_input, tactile_input
        ])
        
        # Verify integration
        assert integration_result.integration_successful is True
        assert integration_result.unified_perception is not None
        assert integration_result.cross_modal_coherence >= 0.6

    # Wisdom Oracle Tests
    def test_oracle_query_processing(self, oracle_system, sample_oracle_query):
        """Test oracle query processing."""
        # Process oracle query
        response = oracle_system.process_oracle_query(sample_oracle_query)
        
        # Verify response
        assert response is not None
        assert isinstance(response, OracleResponse)
        assert response.query_id == sample_oracle_query.query_id
        assert response.wisdom_content is not None
        assert response.confidence_level >= 0.0

    def test_wisdom_distillation(self, oracle_system):
        """Test wisdom distillation from consciousness experiences."""
        # Create consciousness experiences
        experiences = []
        for i in range(10):
            experience = {
                "experience_type": f"learning_event_{i}",
                "insights": [f"insight_{i}_1", f"insight_{i}_2"],
                "wisdom_value": 0.7 + (i * 0.02),
                "verification_level": 0.8
            }
            experiences.append(experience)
        
        # Distill wisdom
        distillation = oracle_system.distill_wisdom(experiences)
        
        # Verify distillation
        assert distillation is not None
        assert isinstance(distillation, WisdomDistillation)
        assert len(distillation.core_insights) > 0
        assert distillation.wisdom_purity >= 0.7

    def test_oracle_consciousness_integration(self, oracle_system):
        """Test oracle consciousness integration."""
        # Create consciousness signal
        consciousness_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.ORACLE_WISDOM_REQUEST,
            data={
                "wisdom_domain": "consciousness_optimization",
                "query_complexity": 0.8,
                "urgency_level": 0.7
            },
            source_module="consciousness_engine",
            timestamp=time.time(),
            priority=9,
            coherence_score=0.85
        )
        
        # Integrate with oracle consciousness
        integration_result = oracle_system.integrate_oracle_consciousness(consciousness_signal)
        
        # Verify integration
        assert integration_result.integration_successful is True
        assert integration_result.consciousness_expansion > 0.0
        assert integration_result.wisdom_enhancement > 0.0

    def test_oracle_memory_synthesis(self, oracle_system):
        """Test oracle memory synthesis and wisdom accumulation."""
        # Create memory fragments
        memory_fragments = []
        for i in range(5):
            fragment = {
                "memory_type": "experiential",
                "content": f"experience_{i}",
                "wisdom_content": f"learned_truth_{i}",
                "verification_score": 0.8 + (i * 0.02),
                "temporal_stability": 0.9
            }
            memory_fragments.append(fragment)
        
        # Synthesize memories
        synthesis_result = oracle_system.synthesize_oracle_memories(memory_fragments)
        
        # Verify synthesis
        assert synthesis_result.synthesis_successful is True
        assert synthesis_result.wisdom_coherence >= 0.7
        assert len(synthesis_result.synthesized_insights) > 0

    # Bio-Inspired Sensing Tests
    def test_bioinspired_pattern_recognition(self, oracle_system):
        """Test bio-inspired pattern recognition."""
        # Create biological patterns
        bio_patterns = [
            {"pattern_type": "neural_oscillation", "frequency": 40, "amplitude": 0.8},
            {"pattern_type": "cellular_growth", "rate": 0.05, "direction": "radial"},
            {"pattern_type": "synaptic_plasticity", "strength_change": 0.15, "duration": 1.2},
            {"pattern_type": "metabolic_cycle", "period": 24, "phase": 0.3}
        ]
        
        # Apply bio-inspired recognition
        recognition_result = oracle_system.recognize_bioinspired_patterns(bio_patterns)
        
        # Verify recognition
        assert recognition_result.patterns_recognized > 0
        assert recognition_result.recognition_confidence >= 0.6
        assert len(recognition_result.pattern_classifications) > 0

    def test_biomimetic_adaptation_algorithms(self, oracle_system):
        """Test biomimetic adaptation algorithms."""
        # Define adaptation scenario
        adaptation_context = {
            "environmental_pressure": 0.7,
            "resource_availability": 0.6,
            "competition_level": 0.5,
            "mutation_rate": 0.02
        }
        
        # Apply biomimetic adaptation
        adaptation_result = oracle_system.apply_biomimetic_adaptation(
            context=adaptation_context,
            target_fitness=0.9
        )
        
        # Verify adaptation
        assert adaptation_result.adaptation_successful is True
        assert adaptation_result.fitness_improvement > 0.0
        assert adaptation_result.adaptation_strategies is not None

    def test_evolutionary_neural_optimization(self, oracle_system):
        """Test evolutionary neural network optimization."""
        # Create initial neural population
        population_size = 20
        generation_count = 5
        
        # Run evolutionary optimization
        evolution_result = oracle_system.evolve_neural_networks(
            population_size=population_size,
            generations=generation_count,
            mutation_rate=0.05,
            selection_pressure=0.7
        )
        
        # Verify evolution
        assert evolution_result.evolution_successful is True
        assert evolution_result.final_fitness > evolution_result.initial_fitness
        assert evolution_result.generations_evolved == generation_count

    # Nervous System Coordination Tests
    def test_nervous_system_coordinator_initialization(self, oracle_system):
        """Test nervous system coordinator initialization."""
        coordinator = oracle_system.coordinator
        
        # Verify coordinator
        assert coordinator is not None
        assert isinstance(coordinator, NervousSystemCoordinator)
        assert coordinator.neural_pathways is not None
        assert coordinator.sensory_receptors is not None

    def test_system_wide_coordination(self, oracle_system):
        """Test system-wide nervous system coordination."""
        # Start coordination
        coordination_result = oracle_system.coordinate_nervous_system()
        
        # Verify coordination
        assert coordination_result.coordination_successful is True
        assert coordination_result.system_coherence >= 0.6
        assert coordination_result.pathway_synchronization >= 0.7

    def test_cross_domain_integration(self, oracle_system):
        """Test cross-domain nervous system integration."""
        # Define integration domains
        domains = [
            "consciousness_processing",
            "memory_formation",
            "identity_verification",
            "ethical_reasoning",
            "guardian_monitoring"
        ]
        
        # Integrate across domains
        integration_result = oracle_system.integrate_across_domains(domains)
        
        # Verify integration
        assert integration_result.integration_successful is True
        assert integration_result.cross_domain_coherence >= 0.6
        assert len(integration_result.domain_connections) == len(domains)

    # Performance and Optimization Tests
    def test_neural_processing_performance(self, oracle_system, sample_sensory_input):
        """Test neural processing performance."""
        start_time = time.time()
        
        # Process multiple inputs
        for _ in range(50):
            oracle_system.process_sensory_input(sample_sensory_input)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process quickly
        assert processing_time < 1.0  # Under 1 second for 50 inputs
        avg_time_per_input = processing_time / 50
        assert avg_time_per_input < 0.02  # Under 20ms per input

    def test_oracle_query_performance(self, oracle_system, sample_oracle_query):
        """Test oracle query processing performance."""
        start_time = time.time()
        
        # Process multiple queries
        for _ in range(10):
            oracle_system.process_oracle_query(sample_oracle_query)
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Should process queries reasonably quickly
        assert query_time < 5.0  # Under 5 seconds for 10 queries
        avg_time_per_query = query_time / 10
        assert avg_time_per_query < 0.5  # Under 500ms per query

    def test_concurrent_neural_processing(self, oracle_system):
        """Test concurrent neural processing."""
        inputs = []
        for i in range(8):
            input_signal = SensoryInput(
                input_type=f"concurrent_test_{i}",
                data={f"test_data_{i}": 0.8},
                source_location=f"test_source_{i}",
                timestamp=time.time(),
                priority=5,
                intensity=0.8
            )
            inputs.append(input_signal)
        
        results = []
        
        def process_input(input_signal):
            result = oracle_system.process_sensory_input(input_signal)
            results.append(result)
        
        # Process inputs concurrently
        threads = []
        for input_signal in inputs:
            thread = threading.Thread(target=process_input, args=(input_signal,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify concurrent processing
        assert len(results) == len(inputs)

    def test_memory_efficiency_optimization(self, oracle_system):
        """Test memory efficiency optimization."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many inputs
        for i in range(30):
            input_signal = SensoryInput(
                input_type="memory_test",
                data={f"memory_test_{i}": 0.8},
                source_location="memory_test_source",
                timestamp=time.time(),
                priority=5,
                intensity=0.8
            )
            oracle_system.process_sensory_input(input_signal)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 300  # Should not create excessive objects

    # Error Handling and Recovery Tests
    def test_invalid_sensory_input_handling(self, oracle_system):
        """Test handling of invalid sensory inputs."""
        # Test with None input
        with pytest.raises(ValueError):
            oracle_system.process_sensory_input(None)
        
        # Test with malformed input data
        malformed_input = SensoryInput(
            input_type="malformed_test",
            data=None,  # Invalid data
            source_location="test_source",
            timestamp=time.time(),
            priority=5,
            intensity=0.5
        )
        
        with pytest.raises(ValueError):
            oracle_system.process_sensory_input(malformed_input)

    def test_neural_pathway_failure_recovery(self, oracle_system, neural_pathway):
        """Test recovery from neural pathway failures."""
        # Simulate pathway failure
        neural_pathway.connection_strength = 0.0  # Complete failure
        
        # Attempt recovery
        recovery_result = oracle_system.recover_failed_pathway(neural_pathway)
        
        # Verify recovery
        assert recovery_result.recovery_successful is True
        assert neural_pathway.connection_strength > 0.0

    def test_oracle_query_error_handling(self, oracle_system):
        """Test error handling in oracle query processing."""
        # Create malformed query
        malformed_query = OracleQuery(
            query_text="",  # Empty query
            query_type="invalid_type",
            context=None,
            requester="test",
            timestamp=time.time(),
            priority=5
        )
        
        # Should handle gracefully
        response = oracle_system.process_oracle_query(
            malformed_query,
            fail_gracefully=True
        )
        
        assert response is not None
        assert response.error_message is not None

    def test_system_failure_graceful_degradation(self, oracle_system):
        """Test graceful degradation during system failures."""
        # Simulate partial system failure
        oracle_system.neural_network.is_active = False
        
        # Should continue operating with reduced functionality
        degraded_result = oracle_system.operate_in_degraded_mode()
        
        # Verify graceful degradation
        assert degraded_result.degraded_operation is True
        assert degraded_result.available_functions > 0

    # Integration and Compatibility Tests
    def test_consciousness_signal_integration(self, oracle_system):
        """Test integration with consciousness signals."""
        # Create consciousness signal
        consciousness_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.NEURAL_ACTIVATION,
            data={
                "activation_pattern": "distributed",
                "intensity": 0.8,
                "coherence": 0.75
            },
            source_module="consciousness_engine",
            timestamp=time.time(),
            priority=8,
            coherence_score=0.8
        )
        
        # Integrate signal
        integration_result = oracle_system.integrate_consciousness_signal(consciousness_signal)
        
        # Verify integration
        assert integration_result.integration_successful is True
        assert integration_result.neural_response > 0.0

    def test_memory_system_coordination(self, oracle_system):
        """Test coordination with memory systems."""
        # Create memory coordination request
        memory_request = {
            "operation": "wisdom_storage",
            "wisdom_content": "Test wisdom for storage",
            "priority": 7,
            "retention_level": "permanent"
        }
        
        # Coordinate with memory system
        coordination_result = oracle_system.coordinate_with_memory_system(memory_request)
        
        # Verify coordination
        assert coordination_result.coordination_successful is True
        assert coordination_result.memory_integration > 0.0

    def test_identity_system_verification(self, oracle_system):
        """Test verification with identity systems."""
        # Create identity verification request
        identity_request = {
            "verification_type": "oracle_access",
            "credentials": "oracle_test_credentials",
            "access_level": "wisdom_query"
        }
        
        # Verify with identity system
        verification_result = oracle_system.verify_with_identity_system(identity_request)
        
        # Verify verification
        assert verification_result.verification_successful is True
        assert verification_result.access_granted is True

    # Global Function Tests
    def test_get_oracle_nervous_system_singleton(self):
        """Test global oracle nervous system singleton."""
        system1 = get_oracle_nervous_system()
        system2 = get_oracle_nervous_system()
        
        # Should return the same instance
        assert system1 is system2

    # Cleanup and Resource Management Tests
    def test_system_resource_cleanup(self, oracle_system):
        """Test system resource cleanup."""
        # Start system with full initialization
        oracle_system.start()
        oracle_system.initialize_neural_network()
        oracle_system.initialize_sensory_network()
        
        # Cleanup
        oracle_system.cleanup()
        
        # Verify cleanup
        assert oracle_system.is_running is False
        assert oracle_system.neural_network.is_active is False
        assert oracle_system.sensory_network.is_active is False

    def test_graceful_system_shutdown(self, oracle_system):
        """Test graceful system shutdown with active processing."""
        # Start system
        oracle_system.start()
        
        # Start some processing
        for i in range(3):
            input_signal = SensoryInput(
                input_type=f"shutdown_test_{i}",
                data={f"test_data_{i}": 0.8},
                source_location="shutdown_test",
                timestamp=time.time(),
                priority=5,
                intensity=0.8
            )
            oracle_system.process_sensory_input(input_signal)
        
        # Graceful shutdown
        oracle_system.shutdown(graceful=True, timeout=3.0)
        
        # Verify shutdown
        assert oracle_system.is_running is False