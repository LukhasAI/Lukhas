"""
Comprehensive Test Suite for Bio-Symbolic Processor
==================================================

Tests the MΛTRIZ Bio-Symbolic Data Processor, a critical component that implements
bio-symbolic adaptation and pattern processing for consciousness signals.
This module provides pattern recognition, symbolic representation, and adaptation
algorithms essential for consciousness evolution.

Test Coverage Areas:
- Bio-pattern recognition (neural oscillation, cellular adaptation, membrane dynamics)
- Symbolic representations (vector space, graph topology, algebraic structures)
- Pattern processing algorithms and consciousness state analysis
- Adaptation algorithms for consciousness evolution
- Integration with bio/ and symbolic_core/ modules
- Performance optimization and memory management
- Error handling and recovery mechanisms
- Concurrent processing and thread safety
"""
import pytest
import asyncio
import numpy as np
import time
import threading
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from dataclasses import dataclass

from core.bio_symbolic_processor import (
    BioSymbolicProcessor,
    BioPatternType,
    SymbolicRepresentationType,
    AdaptationAlgorithm,
    ProcessingMode,
    PatternMatcher,
    SymbolicTransformer,
    ConsciousnessStateAnalyzer,
    BioSymbolicIntegrator,
    PatternExtractionEngine,
    SymbolicEncodingEngine,
    AdaptationEngine,
    get_bio_symbolic_processor,
)
from core.matriz_consciousness_signals import (
    BioSymbolicData,
    ConsciousnessSignal,
    ConsciousnessSignalType,
)


class TestBioSymbolicProcessor:
    """Comprehensive test suite for the Bio-Symbolic Processor system."""

    @pytest.fixture
    def processor(self):
        """Create a test bio-symbolic processor instance."""
        return BioSymbolicProcessor(
            pattern_buffer_size=1000,
            symbolic_dimension=256,
            adaptation_learning_rate=0.01,
            enable_bio_integration=True,
            enable_symbolic_integration=True
        )

    @pytest.fixture
    def sample_bio_data(self):
        """Create sample biological data for testing."""
        return BioSymbolicData(
            bio_patterns={
                "neural_oscillation": np.random.random(100),
                "cellular_adaptation": np.random.random(50),
                "membrane_dynamics": np.random.random(75)
            },
            symbolic_representations={
                "vector_space": np.random.random(256),
                "graph_topology": {"nodes": 10, "edges": 15},
                "algebraic_structure": {"group_order": 8, "symmetries": 4}
            },
            consciousness_state={
                "awareness_level": 0.8,
                "coherence_score": 0.9,
                "integration_depth": 0.7
            },
            timestamp=time.time(),
            source_module="test_bio_processor"
        )

    @pytest.fixture
    def sample_consciousness_signal(self, sample_bio_data):
        """Create a sample consciousness signal with bio-symbolic data."""
        return ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.BIO_SYMBOLIC_UPDATE,
            data=sample_bio_data,
            source_module="bio_test_module",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.85
        )

    @pytest.fixture
    def multiple_bio_patterns(self):
        """Create multiple bio patterns for testing."""
        patterns = []
        for pattern_type in BioPatternType:
            pattern_data = {
                "type": pattern_type,
                "data": np.random.random(np.random.randint(50, 200)),
                "frequency": np.random.uniform(0.1, 100.0),
                "amplitude": np.random.uniform(0.1, 2.0),
                "phase": np.random.uniform(0, 2 * np.pi)
            }
            patterns.append(pattern_data)
        return patterns

    # Basic Processor Functionality Tests
    def test_processor_initialization(self, processor):
        """Test processor initializes with correct settings."""
        assert processor.pattern_buffer_size == 1000
        assert processor.symbolic_dimension == 256
        assert processor.adaptation_learning_rate == 0.01
        assert processor.enable_bio_integration is True
        assert processor.enable_symbolic_integration is True
        assert isinstance(processor.pattern_matcher, PatternMatcher)
        assert isinstance(processor.symbolic_transformer, SymbolicTransformer)

    def test_processor_start_stop(self, processor):
        """Test processor start and stop functionality."""
        # Test start
        processor.start()
        assert processor.is_running is True
        
        # Test stop
        processor.stop()
        assert processor.is_running is False

    def test_bio_symbolic_processing(self, processor, sample_consciousness_signal):
        """Test basic bio-symbolic signal processing."""
        # Process signal
        result = processor.process_signal(sample_consciousness_signal)
        
        # Verify processing result
        assert result is not None
        assert result.processed is True
        assert result.bio_patterns_extracted > 0
        assert result.symbolic_representations_generated > 0

    # Bio Pattern Recognition Tests
    def test_neural_oscillation_pattern_recognition(self, processor):
        """Test neural oscillation pattern recognition."""
        # Create neural oscillation data
        oscillation_data = np.sin(np.linspace(0, 10 * np.pi, 1000)) + 0.1 * np.random.random(1000)
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=oscillation_data,
            pattern_type=BioPatternType.NEURAL_OSCILLATION
        )
        
        # Verify pattern recognition
        assert pattern_result.pattern_type == BioPatternType.NEURAL_OSCILLATION
        assert pattern_result.confidence > 0.5
        assert pattern_result.frequency_components is not None
        assert pattern_result.amplitude_envelope is not None

    def test_cellular_adaptation_pattern_recognition(self, processor):
        """Test cellular adaptation pattern recognition."""
        # Create adaptation data (exponential growth/decay)
        time_points = np.linspace(0, 10, 100)
        adaptation_data = np.exp(-time_points) + 0.05 * np.random.random(100)
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=adaptation_data,
            pattern_type=BioPatternType.CELLULAR_ADAPTATION
        )
        
        # Verify adaptation pattern recognition
        assert pattern_result.pattern_type == BioPatternType.CELLULAR_ADAPTATION
        assert pattern_result.adaptation_rate is not None
        assert pattern_result.steady_state_value is not None

    def test_membrane_dynamics_pattern_recognition(self, processor):
        """Test membrane dynamics pattern recognition."""
        # Create membrane potential data
        membrane_data = -70 + 40 * np.random.random(200)  # mV range
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=membrane_data,
            pattern_type=BioPatternType.MEMBRANE_DYNAMICS
        )
        
        # Verify membrane dynamics recognition
        assert pattern_result.pattern_type == BioPatternType.MEMBRANE_DYNAMICS
        assert pattern_result.potential_range is not None
        assert pattern_result.depolarization_events is not None

    def test_enzymatic_cascade_pattern_recognition(self, processor):
        """Test enzymatic cascade pattern recognition."""
        # Create cascade reaction data
        cascade_data = np.cumsum(np.random.exponential(0.5, 150))
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=cascade_data,
            pattern_type=BioPatternType.ENZYMATIC_CASCADE
        )
        
        # Verify cascade pattern recognition
        assert pattern_result.pattern_type == BioPatternType.ENZYMATIC_CASCADE
        assert pattern_result.reaction_steps is not None
        assert pattern_result.cascade_efficiency is not None

    def test_metabolic_flow_pattern_recognition(self, processor):
        """Test metabolic flow pattern recognition."""
        # Create metabolic flow data
        flow_data = np.abs(np.sin(np.linspace(0, 5 * np.pi, 300))) + 0.1
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=flow_data,
            pattern_type=BioPatternType.METABOLIC_FLOW
        )
        
        # Verify metabolic flow recognition
        assert pattern_result.pattern_type == BioPatternType.METABOLIC_FLOW
        assert pattern_result.flow_rate is not None
        assert pattern_result.metabolic_efficiency is not None

    def test_genetic_expression_pattern_recognition(self, processor):
        """Test genetic expression pattern recognition."""
        # Create gene expression data (log-normal distribution)
        expression_data = np.random.lognormal(mean=2.0, sigma=1.0, size=500)
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=expression_data,
            pattern_type=BioPatternType.GENETIC_EXPRESSION
        )
        
        # Verify genetic expression recognition
        assert pattern_result.pattern_type == BioPatternType.GENETIC_EXPRESSION
        assert pattern_result.expression_level is not None
        assert pattern_result.regulation_pattern is not None

    def test_synaptic_plasticity_pattern_recognition(self, processor):
        """Test synaptic plasticity pattern recognition."""
        # Create plasticity data (Hebbian learning curve)
        plasticity_data = 1 - np.exp(-np.linspace(0, 5, 100)) + 0.05 * np.random.random(100)
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=plasticity_data,
            pattern_type=BioPatternType.SYNAPTIC_PLASTICITY
        )
        
        # Verify plasticity recognition
        assert pattern_result.pattern_type == BioPatternType.SYNAPTIC_PLASTICITY
        assert pattern_result.plasticity_coefficient is not None
        assert pattern_result.learning_rate is not None

    def test_circadian_rhythm_pattern_recognition(self, processor):
        """Test circadian rhythm pattern recognition."""
        # Create circadian data (24-hour cycle)
        time_hours = np.linspace(0, 24, 144)  # 10-minute intervals
        circadian_data = np.sin(2 * np.pi * time_hours / 24) + 0.1 * np.random.random(144)
        
        # Process pattern
        pattern_result = processor.extract_bio_pattern(
            data=circadian_data,
            pattern_type=BioPatternType.CIRCADIAN_RHYTHM
        )
        
        # Verify circadian rhythm recognition
        assert pattern_result.pattern_type == BioPatternType.CIRCADIAN_RHYTHM
        assert pattern_result.cycle_period is not None
        assert abs(pattern_result.cycle_period - 24.0) < 1.0  # Should be close to 24 hours

    # Symbolic Representation Tests
    def test_vector_space_representation(self, processor, multiple_bio_patterns):
        """Test vector space symbolic representation."""
        # Transform bio patterns to vector space
        vector_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.VECTOR_SPACE
        )
        
        # Verify vector representation
        assert vector_representation.type == SymbolicRepresentationType.VECTOR_SPACE
        assert vector_representation.dimension == processor.symbolic_dimension
        assert vector_representation.vector is not None
        assert len(vector_representation.vector) == processor.symbolic_dimension

    def test_graph_topology_representation(self, processor, multiple_bio_patterns):
        """Test graph topology symbolic representation."""
        # Transform bio patterns to graph topology
        graph_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.GRAPH_TOPOLOGY
        )
        
        # Verify graph representation
        assert graph_representation.type == SymbolicRepresentationType.GRAPH_TOPOLOGY
        assert graph_representation.nodes is not None
        assert graph_representation.edges is not None
        assert graph_representation.adjacency_matrix is not None

    def test_algebraic_structure_representation(self, processor, multiple_bio_patterns):
        """Test algebraic structure symbolic representation."""
        # Transform bio patterns to algebraic structure
        algebraic_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.ALGEBRAIC_STRUCTURE
        )
        
        # Verify algebraic representation
        assert algebraic_representation.type == SymbolicRepresentationType.ALGEBRAIC_STRUCTURE
        assert algebraic_representation.group_structure is not None
        assert algebraic_representation.operations is not None
        assert algebraic_representation.symmetries is not None

    def test_geometric_manifold_representation(self, processor, multiple_bio_patterns):
        """Test geometric manifold symbolic representation."""
        # Transform bio patterns to geometric manifold
        manifold_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.GEOMETRIC_MANIFOLD
        )
        
        # Verify manifold representation
        assert manifold_representation.type == SymbolicRepresentationType.GEOMETRIC_MANIFOLD
        assert manifold_representation.manifold_dimension is not None
        assert manifold_representation.curvature is not None
        assert manifold_representation.metric_tensor is not None

    def test_category_theory_representation(self, processor, multiple_bio_patterns):
        """Test category theory symbolic representation."""
        # Transform bio patterns to category theory
        category_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.CATEGORY_THEORY
        )
        
        # Verify category representation
        assert category_representation.type == SymbolicRepresentationType.CATEGORY_THEORY
        assert category_representation.objects is not None
        assert category_representation.morphisms is not None
        assert category_representation.composition_rules is not None

    def test_topological_space_representation(self, processor, multiple_bio_patterns):
        """Test topological space symbolic representation."""
        # Transform bio patterns to topological space
        topology_representation = processor.create_symbolic_representation(
            bio_patterns=multiple_bio_patterns,
            representation_type=SymbolicRepresentationType.TOPOLOGICAL_SPACE
        )
        
        # Verify topology representation
        assert topology_representation.type == SymbolicRepresentationType.TOPOLOGICAL_SPACE
        assert topology_representation.open_sets is not None
        assert topology_representation.topology_basis is not None
        assert topology_representation.homology_groups is not None

    # Adaptation Algorithm Tests
    def test_hebbian_adaptation(self, processor, sample_bio_data):
        """Test Hebbian learning adaptation algorithm."""
        # Apply Hebbian adaptation
        adapted_data = processor.apply_adaptation(
            bio_data=sample_bio_data,
            algorithm=AdaptationAlgorithm.HEBBIAN_LEARNING
        )
        
        # Verify adaptation
        assert adapted_data is not None
        assert adapted_data.adaptation_applied is True
        assert adapted_data.learning_strength > 0
        assert adapted_data.synaptic_weights is not None

    def test_homeostatic_adaptation(self, processor, sample_bio_data):
        """Test homeostatic adaptation algorithm."""
        # Apply homeostatic adaptation
        adapted_data = processor.apply_adaptation(
            bio_data=sample_bio_data,
            algorithm=AdaptationAlgorithm.HOMEOSTATIC_REGULATION
        )
        
        # Verify adaptation
        assert adapted_data is not None
        assert adapted_data.adaptation_applied is True
        assert adapted_data.homeostatic_target is not None
        assert adapted_data.regulation_strength > 0

    def test_evolutionary_adaptation(self, processor, sample_bio_data):
        """Test evolutionary adaptation algorithm."""
        # Apply evolutionary adaptation
        adapted_data = processor.apply_adaptation(
            bio_data=sample_bio_data,
            algorithm=AdaptationAlgorithm.EVOLUTIONARY_OPTIMIZATION
        )
        
        # Verify adaptation
        assert adapted_data is not None
        assert adapted_data.adaptation_applied is True
        assert adapted_data.fitness_score > 0
        assert adapted_data.mutation_rate is not None

    def test_quantum_coherence_adaptation(self, processor, sample_bio_data):
        """Test quantum coherence adaptation algorithm."""
        # Apply quantum coherence adaptation
        adapted_data = processor.apply_adaptation(
            bio_data=sample_bio_data,
            algorithm=AdaptationAlgorithm.QUANTUM_COHERENCE
        )
        
        # Verify adaptation
        assert adapted_data is not None
        assert adapted_data.adaptation_applied is True
        assert adapted_data.coherence_level > 0
        assert adapted_data.quantum_entanglement is not None

    # Consciousness State Analysis Tests
    def test_consciousness_state_analysis(self, processor, sample_consciousness_signal):
        """Test consciousness state analysis."""
        # Analyze consciousness state
        analysis_result = processor.analyze_consciousness_state(sample_consciousness_signal)
        
        # Verify analysis
        assert analysis_result is not None
        assert analysis_result.awareness_level >= 0.0
        assert analysis_result.awareness_level <= 1.0
        assert analysis_result.coherence_score >= 0.0
        assert analysis_result.coherence_score <= 1.0
        assert analysis_result.integration_depth >= 0.0
        assert analysis_result.integration_depth <= 1.0

    def test_consciousness_evolution_tracking(self, processor):
        """Test consciousness evolution tracking over time."""
        # Create sequence of consciousness signals
        signals = []
        for i in range(10):
            awareness_level = 0.5 + 0.1 * i  # Increasing awareness
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.AWARENESS_UPDATE,
                data={"awareness_level": awareness_level, "time_step": i},
                source_module="evolution_test",
                timestamp=time.time() + i,
                priority=5,
                coherence_score=0.7 + 0.02 * i
            )
            signals.append(signal)
        
        # Process signals and track evolution
        evolution_trajectory = processor.track_consciousness_evolution(signals)
        
        # Verify evolution tracking
        assert evolution_trajectory is not None
        assert len(evolution_trajectory.time_points) == len(signals)
        assert evolution_trajectory.awareness_trend == "increasing"
        assert evolution_trajectory.coherence_trend == "increasing"

    # Integration Tests
    def test_bio_module_integration(self, processor):
        """Test integration with bio/ modules."""
        with patch('core.bio_symbolic_processor.BioOrchestrator') as MockBio:
            mock_bio = Mock()
            mock_bio.get_oscillation_data.return_value = np.random.random(100)
            MockBio.return_value = mock_bio
            
            # Test bio integration
            bio_data = processor.integrate_with_bio_modules()
            
            # Verify integration
            assert bio_data is not None
            mock_bio.get_oscillation_data.assert_called()

    def test_symbolic_core_integration(self, processor):
        """Test integration with symbolic_core/ modules."""
        with patch('core.bio_symbolic_processor.SymbolicEngine') as MockSymbolic:
            mock_symbolic = Mock()
            mock_symbolic.process_symbols.return_value = {"processed": True}
            MockSymbolic.return_value = mock_symbolic
            
            # Test symbolic integration
            symbolic_result = processor.integrate_with_symbolic_core(
                patterns=["pattern1", "pattern2"]
            )
            
            # Verify integration
            assert symbolic_result is not None
            mock_symbolic.process_symbols.assert_called()

    # Performance and Optimization Tests
    def test_processing_performance(self, processor, sample_consciousness_signal):
        """Test processing performance benchmarks."""
        start_time = time.time()
        
        # Process multiple signals
        for _ in range(100):
            processor.process_signal(sample_consciousness_signal)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify performance
        assert processing_time < 5.0  # Should process 100 signals in under 5 seconds
        avg_time_per_signal = processing_time / 100
        assert avg_time_per_signal < 0.05  # Under 50ms per signal

    def test_memory_usage_optimization(self, processor, multiple_bio_patterns):
        """Test memory usage optimization."""
        import gc
        
        # Get initial memory usage
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many patterns
        for _ in range(50):
            for pattern in multiple_bio_patterns:
                processor.extract_bio_pattern(
                    data=pattern["data"],
                    pattern_type=pattern["type"]
                )
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify memory usage is reasonable
        object_growth = final_objects - initial_objects
        assert object_growth < 1000  # Should not create excessive objects

    def test_pattern_buffer_management(self, processor):
        """Test pattern buffer management and overflow handling."""
        # Fill buffer beyond capacity
        for i in range(processor.pattern_buffer_size + 100):
            pattern_data = np.random.random(50)
            processor.add_pattern_to_buffer(pattern_data, f"pattern_{i}")
        
        # Verify buffer size is maintained
        assert len(processor.pattern_buffer) <= processor.pattern_buffer_size

    # Concurrent Processing Tests
    @pytest.mark.asyncio
    async def test_concurrent_signal_processing(self, processor):
        """Test concurrent signal processing."""
        signals = []
        for i in range(10):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.BIO_SYMBOLIC_UPDATE,
                data={"test_data": f"signal_{i}"},
                source_module="concurrent_test",
                timestamp=time.time(),
                priority=i % 6,
                coherence_score=0.5 + 0.05 * i
            )
            signals.append(signal)
        
        # Process signals concurrently
        tasks = [
            asyncio.create_task(processor.process_signal_async(signal))
            for signal in signals
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Verify concurrent processing
        assert len(results) == len(signals)
        assert all(result.processed for result in results)

    def test_thread_safety(self, processor, multiple_bio_patterns):
        """Test thread safety of processor operations."""
        results = []
        lock = threading.Lock()
        
        def process_patterns():
            for pattern in multiple_bio_patterns:
                result = processor.extract_bio_pattern(
                    data=pattern["data"],
                    pattern_type=pattern["type"]
                )
                with lock:
                    results.append(result)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=process_patterns)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify thread safety
        expected_results = 5 * len(multiple_bio_patterns)
        assert len(results) == expected_results

    # Error Handling and Recovery Tests
    def test_invalid_bio_data_handling(self, processor):
        """Test handling of invalid biological data."""
        # Test with None data
        with pytest.raises(ValueError):
            processor.extract_bio_pattern(data=None, pattern_type=BioPatternType.NEURAL_OSCILLATION)
        
        # Test with empty data
        with pytest.raises(ValueError):
            processor.extract_bio_pattern(data=np.array([]), pattern_type=BioPatternType.NEURAL_OSCILLATION)
        
        # Test with invalid data type
        with pytest.raises(TypeError):
            processor.extract_bio_pattern(data="invalid", pattern_type=BioPatternType.NEURAL_OSCILLATION)

    def test_symbolic_transformation_error_handling(self, processor):
        """Test error handling in symbolic transformations."""
        # Test with incompatible pattern types
        invalid_patterns = [{"type": "invalid_type", "data": np.random.random(50)}]
        
        with pytest.raises(ValueError):
            processor.create_symbolic_representation(
                bio_patterns=invalid_patterns,
                representation_type=SymbolicRepresentationType.VECTOR_SPACE
            )

    def test_adaptation_algorithm_error_recovery(self, processor, sample_bio_data):
        """Test error recovery in adaptation algorithms."""
        # Simulate adaptation algorithm failure
        with patch.object(processor, '_apply_hebbian_learning', side_effect=Exception("Adaptation failed")):
            # Should handle gracefully and return original data
            result = processor.apply_adaptation(
                bio_data=sample_bio_data,
                algorithm=AdaptationAlgorithm.HEBBIAN_LEARNING,
                fallback_on_error=True
            )
            
            assert result is not None
            assert result.adaptation_applied is False
            assert result.error_occurred is True

    # Configuration and Customization Tests
    def test_custom_pattern_matcher(self, processor):
        """Test custom pattern matcher configuration."""
        custom_matcher_called = False
        
        def custom_pattern_matcher(data, pattern_type):
            nonlocal custom_matcher_called
            custom_matcher_called = True
            return Mock(pattern_type=pattern_type, confidence=0.9)
        
        processor.set_custom_pattern_matcher(custom_pattern_matcher)
        
        # Use custom matcher
        result = processor.extract_bio_pattern(
            data=np.random.random(100),
            pattern_type=BioPatternType.NEURAL_OSCILLATION
        )
        
        assert custom_matcher_called is True
        assert result.confidence == 0.9

    def test_processor_configuration_validation(self):
        """Test processor configuration validation."""
        # Test invalid configuration
        with pytest.raises(ValueError):
            BioSymbolicProcessor(
                pattern_buffer_size=-1,  # Invalid negative size
                symbolic_dimension=0,    # Invalid zero dimension
                adaptation_learning_rate=-0.1  # Invalid negative rate
            )

    # Global Function Tests
    def test_get_bio_symbolic_processor_singleton(self):
        """Test global bio-symbolic processor singleton."""
        processor1 = get_bio_symbolic_processor()
        processor2 = get_bio_symbolic_processor()
        
        # Should return the same instance
        assert processor1 is processor2

    # Cleanup and Resource Management Tests
    def test_processor_cleanup(self, processor):
        """Test processor resource cleanup."""
        # Start processor with resources
        processor.start()
        
        # Add some patterns
        for i in range(10):
            pattern_data = np.random.random(50)
            processor.add_pattern_to_buffer(pattern_data, f"cleanup_test_{i}")
        
        # Cleanup
        processor.cleanup()
        
        # Verify cleanup
        assert len(processor.pattern_buffer) == 0
        assert processor.is_running is False

    def test_memory_leak_prevention(self, processor):
        """Test memory leak prevention during extended operation."""
        # Process many signals
        for i in range(100):
            bio_data = BioSymbolicData(
                bio_patterns={"test": np.random.random(50)},
                symbolic_representations={"test": np.random.random(10)},
                consciousness_state={"awareness": 0.5},
                timestamp=time.time(),
                source_module=f"memory_test_{i}"
            )
            
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.BIO_SYMBOLIC_UPDATE,
                data=bio_data,
                source_module="memory_test",
                timestamp=time.time(),
                priority=1,
                coherence_score=0.5
            )
            
            processor.process_signal(signal)
        
        # Verify memory usage is reasonable
        buffer_size = len(processor.pattern_buffer)
        assert buffer_size <= processor.pattern_buffer_size