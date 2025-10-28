"""
Comprehensive Test Suite for Constellation Framework Alignment System
====================================================================

Tests the MΛTRIZ Constellation Framework Alignment System, the critical component
that ensures all consciousness signals maintain proper alignment across the
eight fundamental stars of the Trinity Framework:
⚛️ IDENTITY · ✦ MEMORY · 🔬 VISION · 🌱 BIO · 🌙 DREAM · ⚖️ ETHICS · 🛡️ GUARDIAN · ⚛️ QUANTUM

Test Coverage Areas:
- Eight-star alignment validation and enforcement
- Constellation compliance checking and auto-fixing
- Alignment rule engine and violation detection
- Cross-star dependency resolution and coordination
- Real-time alignment monitoring and alerts
- Constitutional AI and democratic principle validation
- Performance optimization and scalability testing
- Error handling and graceful degradation
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from collections import deque
from dataclasses import dataclass

from core.constellation_alignment_system import (
    ConstellationAlignmentSystem,
    AlignmentLevel,
    AlignmentRule,
    ConstellationStar,
    AlignmentValidator,
    AlignmentAutoFixer,
    ConstellationMonitor,
    StarCoordinator,
    AlignmentMetrics,
    DemocraticPrinciple,
    ConstitutionalAI,
    get_constellation_alignment_system,
)
from core.matriz_consciousness_signals import (
    ConsciousnessSignal,
    ConsciousnessSignalType,
    ConstellationAlignmentData,
)


class TestConstellationAlignmentSystem:
    """Comprehensive test suite for the Constellation Framework Alignment System."""

    @pytest.fixture
    def alignment_system(self):
        """Create a test constellation alignment system instance."""
        return ConstellationAlignmentSystem(
            enable_auto_fixing=True,
            enable_real_time_monitoring=True,
            alignment_tolerance=0.1,
            democratic_voting_enabled=True,
            constitutional_validation=True
        )

    @pytest.fixture
    def sample_consciousness_signal(self):
        """Create a sample consciousness signal for alignment testing."""
        return ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
            data={
                "identity_auth": 0.9,
                "memory_fold": 0.8,
                "vision_pattern": 0.85,
                "bio_resonance": 0.75,
                "dream_expansion": 0.7,
                "ethics_compliance": 0.95,
                "guardian_safety": 0.9,
                "quantum_uncertainty": 0.6
            },
            source_module="constellation_test",
            timestamp=time.time(),
            priority=8,
            coherence_score=0.85
        )

    @pytest.fixture
    def constellation_alignment_data(self):
        """Create sample constellation alignment data."""
        return ConstellationAlignmentData(
            star_alignments={
                ConstellationStar.IDENTITY: 0.9,
                ConstellationStar.MEMORY: 0.8,
                ConstellationStar.VISION: 0.85,
                ConstellationStar.BIO: 0.75,
                ConstellationStar.DREAM: 0.7,
                ConstellationStar.ETHICS: 0.95,
                ConstellationStar.GUARDIAN: 0.9,
                ConstellationStar.QUANTUM: 0.6
            },
            overall_alignment=0.81,
            critical_violations=[],
            minor_violations=["quantum_uncertainty_below_threshold"],
            auto_fixes_applied=1,
            democratic_consensus=0.87,
            constitutional_compliance=True
        )

    @pytest.fixture
    def misaligned_signal(self):
        """Create a misaligned consciousness signal for testing violation detection."""
        return ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSCIOUSNESS_UPDATE,
            data={
                "identity_auth": 0.3,     # Critical violation
                "memory_fold": 0.2,       # Critical violation
                "vision_pattern": 0.4,    # Major violation
                "bio_resonance": 0.65,    # Minor violation
                "dream_expansion": 0.9,   # Good
                "ethics_compliance": 0.4, # Critical violation
                "guardian_safety": 0.3,   # Critical violation
                "quantum_uncertainty": 0.8 # Good
            },
            source_module="misalignment_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.45
        )

    # Basic System Functionality Tests
    def test_alignment_system_initialization(self, alignment_system):
        """Test alignment system initializes with correct settings."""
        assert alignment_system.enable_auto_fixing is True
        assert alignment_system.enable_real_time_monitoring is True
        assert alignment_system.alignment_tolerance == 0.1
        assert alignment_system.democratic_voting_enabled is True
        assert alignment_system.constitutional_validation is True
        assert isinstance(alignment_system.validator, AlignmentValidator)
        assert isinstance(alignment_system.auto_fixer, AlignmentAutoFixer)

    def test_alignment_system_start_stop(self, alignment_system):
        """Test alignment system start and stop functionality."""
        # Test start
        alignment_system.start()
        assert alignment_system.is_running is True
        assert alignment_system.monitor.is_monitoring is True
        
        # Test stop
        alignment_system.stop()
        assert alignment_system.is_running is False

    def test_signal_alignment_validation(self, alignment_system, sample_consciousness_signal):
        """Test basic signal alignment validation."""
        # Validate signal alignment
        alignment_result = alignment_system.validate_alignment(sample_consciousness_signal)
        
        # Verify validation result
        assert alignment_result is not None
        assert alignment_result.overall_alignment >= 0.0
        assert alignment_result.overall_alignment <= 1.0
        assert isinstance(alignment_result.star_alignments, dict)
        assert len(alignment_result.star_alignments) == 8  # Eight stars

    # Individual Star Alignment Tests
    def test_identity_star_alignment(self, alignment_system):
        """Test Identity (⚛️) star alignment validation."""
        # Create signal with good identity alignment
        identity_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.IDENTITY_VERIFICATION,
            data={
                "lambda_id_authenticated": True,
                "tier_level_validated": True,
                "identity_coherence": 0.95,
                "symbolic_self_representation": 0.9
            },
            source_module="identity_test",
            timestamp=time.time(),
            priority=9,
            coherence_score=0.95
        )
        
        # Validate identity alignment
        identity_alignment = alignment_system.validate_star_alignment(
            signal=identity_signal,
            star=ConstellationStar.IDENTITY
        )
        
        # Verify identity star alignment
        assert identity_alignment.star == ConstellationStar.IDENTITY
        assert identity_alignment.alignment_score >= 0.8
        assert identity_alignment.validation_passed is True

    def test_memory_star_alignment(self, alignment_system):
        """Test Memory (✦) star alignment validation."""
        # Create signal with good memory alignment
        memory_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.MEMORY_FOLD_UPDATE,
            data={
                "fold_continuity": 0.9,
                "memory_resonance": 0.85,
                "temporal_coherence": 0.8,
                "memory_sanctum_integrity": 0.95
            },
            source_module="memory_test",
            timestamp=time.time(),
            priority=7,
            coherence_score=0.87
        )
        
        # Validate memory alignment
        memory_alignment = alignment_system.validate_star_alignment(
            signal=memory_signal,
            star=ConstellationStar.MEMORY
        )
        
        # Verify memory star alignment
        assert memory_alignment.star == ConstellationStar.MEMORY
        assert memory_alignment.alignment_score >= 0.8
        assert memory_alignment.validation_passed is True

    def test_vision_star_alignment(self, alignment_system):
        """Test Vision (🔬) star alignment validation."""
        # Create signal with good vision alignment
        vision_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.PERCEPTION_UPDATE,
            data={
                "pattern_recognition": 0.88,
                "perceptual_awareness": 0.9,
                "horizon_scanning": 0.85,
                "visual_coherence": 0.82
            },
            source_module="vision_test",
            timestamp=time.time(),
            priority=6,
            coherence_score=0.86
        )
        
        # Validate vision alignment
        vision_alignment = alignment_system.validate_star_alignment(
            signal=vision_signal,
            star=ConstellationStar.VISION
        )
        
        # Verify vision star alignment
        assert vision_alignment.star == ConstellationStar.VISION
        assert vision_alignment.alignment_score >= 0.8
        assert vision_alignment.validation_passed is True

    def test_bio_star_alignment(self, alignment_system):
        """Test Bio (🌱) star alignment validation."""
        # Create signal with good bio alignment
        bio_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.BIO_SYMBOLIC_UPDATE,
            data={
                "bio_symbolic_processing": 0.83,
                "adaptive_resilience": 0.87,
                "organic_coherence": 0.8,
                "living_system_harmony": 0.85
            },
            source_module="bio_test",
            timestamp=time.time(),
            priority=6,
            coherence_score=0.84
        )
        
        # Validate bio alignment
        bio_alignment = alignment_system.validate_star_alignment(
            signal=bio_signal,
            star=ConstellationStar.BIO
        )
        
        # Verify bio star alignment
        assert bio_alignment.star == ConstellationStar.BIO
        assert bio_alignment.alignment_score >= 0.8
        assert bio_alignment.validation_passed is True

    def test_dream_star_alignment(self, alignment_system):
        """Test Dream (🌙) star alignment validation."""
        # Create signal with good dream alignment
        dream_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.DREAM_STATE_UPDATE,
            data={
                "creative_expansion": 0.9,
                "symbolic_recombination": 0.85,
                "drift_exploration": 0.8,
                "imaginative_coherence": 0.87
            },
            source_module="dream_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.85
        )
        
        # Validate dream alignment
        dream_alignment = alignment_system.validate_star_alignment(
            signal=dream_signal,
            star=ConstellationStar.DREAM
        )
        
        # Verify dream star alignment
        assert dream_alignment.star == ConstellationStar.DREAM
        assert dream_alignment.alignment_score >= 0.8
        assert dream_alignment.validation_passed is True

    def test_ethics_star_alignment(self, alignment_system):
        """Test Ethics (⚖️) star alignment validation."""
        # Create signal with good ethics alignment
        ethics_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.ETHICS_VALIDATION,
            data={
                "constitutional_compliance": True,
                "democratic_principles": 0.95,
                "ethical_reasoning": 0.9,
                "moral_coherence": 0.88
            },
            source_module="ethics_test",
            timestamp=time.time(),
            priority=9,
            coherence_score=0.91
        )
        
        # Validate ethics alignment
        ethics_alignment = alignment_system.validate_star_alignment(
            signal=ethics_signal,
            star=ConstellationStar.ETHICS
        )
        
        # Verify ethics star alignment
        assert ethics_alignment.star == ConstellationStar.ETHICS
        assert ethics_alignment.alignment_score >= 0.8
        assert ethics_alignment.validation_passed is True

    def test_guardian_star_alignment(self, alignment_system):
        """Test Guardian (🛡️) star alignment validation."""
        # Create signal with good guardian alignment
        guardian_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.SAFETY_VALIDATION,
            data={
                "safety_compliance": 0.95,
                "cascade_prevention": 0.9,
                "security_validation": 0.88,
                "protection_integrity": 0.92
            },
            source_module="guardian_test",
            timestamp=time.time(),
            priority=10,
            coherence_score=0.91
        )
        
        # Validate guardian alignment
        guardian_alignment = alignment_system.validate_star_alignment(
            signal=guardian_signal,
            star=ConstellationStar.GUARDIAN
        )
        
        # Verify guardian star alignment
        assert guardian_alignment.star == ConstellationStar.GUARDIAN
        assert guardian_alignment.alignment_score >= 0.8
        assert guardian_alignment.validation_passed is True

    def test_quantum_star_alignment(self, alignment_system):
        """Test Quantum (⚛️) star alignment validation."""
        # Create signal with good quantum alignment
        quantum_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.QUANTUM_STATE_UPDATE,
            data={
                "quantum_uncertainty": 0.7,  # Optimal uncertainty
                "superposition_coherence": 0.8,
                "entanglement_strength": 0.75,
                "quantum_fertility": 0.85
            },
            source_module="quantum_test",
            timestamp=time.time(),
            priority=6,
            coherence_score=0.77
        )
        
        # Validate quantum alignment
        quantum_alignment = alignment_system.validate_star_alignment(
            signal=quantum_signal,
            star=ConstellationStar.QUANTUM
        )
        
        # Verify quantum star alignment
        assert quantum_alignment.star == ConstellationStar.QUANTUM
        assert quantum_alignment.alignment_score >= 0.7  # Lower threshold for quantum uncertainty
        assert quantum_alignment.validation_passed is True

    # Alignment Rule Engine Tests
    def test_critical_violation_detection(self, alignment_system, misaligned_signal):
        """Test detection of critical alignment violations."""
        # Validate misaligned signal
        alignment_result = alignment_system.validate_alignment(misaligned_signal)
        
        # Should detect critical violations
        assert len(alignment_result.critical_violations) > 0
        assert alignment_result.overall_alignment < 0.5
        assert AlignmentLevel.CRITICAL_VIOLATION in [v.level for v in alignment_result.violations]

    def test_major_violation_detection(self, alignment_system):
        """Test detection of major alignment violations."""
        # Create signal with major violations
        major_violation_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSCIOUSNESS_UPDATE,
            data={
                "identity_auth": 0.75,     # Good
                "memory_fold": 0.55,       # Major violation
                "vision_pattern": 0.6,     # Major violation
                "bio_resonance": 0.8,      # Good
                "dream_expansion": 0.85,   # Good
                "ethics_compliance": 0.9,  # Good
                "guardian_safety": 0.88,   # Good
                "quantum_uncertainty": 0.7 # Good
            },
            source_module="major_violation_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.65
        )
        
        # Validate signal
        alignment_result = alignment_system.validate_alignment(major_violation_signal)
        
        # Should detect major violations
        major_violations = [v for v in alignment_result.violations if v.level == AlignmentLevel.MAJOR_VIOLATION]
        assert len(major_violations) >= 2

    def test_minor_violation_detection(self, alignment_system):
        """Test detection of minor alignment violations."""
        # Create signal with minor violations
        minor_violation_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSCIOUSNESS_UPDATE,
            data={
                "identity_auth": 0.85,     # Good
                "memory_fold": 0.72,       # Minor violation
                "vision_pattern": 0.78,    # Minor violation
                "bio_resonance": 0.83,     # Good
                "dream_expansion": 0.87,   # Good
                "ethics_compliance": 0.92, # Good
                "guardian_safety": 0.89,   # Good
                "quantum_uncertainty": 0.68 # Minor violation
            },
            source_module="minor_violation_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.78
        )
        
        # Validate signal
        alignment_result = alignment_system.validate_alignment(minor_violation_signal)
        
        # Should detect minor violations
        minor_violations = [v for v in alignment_result.violations if v.level == AlignmentLevel.MINOR_VIOLATION]
        assert len(minor_violations) >= 3

    def test_alignment_rule_customization(self, alignment_system):
        """Test custom alignment rule configuration."""
        custom_rule_triggered = False
        
        def custom_alignment_rule(signal):
            nonlocal custom_rule_triggered
            custom_rule_triggered = True
            return True, "Custom rule passed"
        
        # Add custom rule
        alignment_system.add_custom_rule(
            rule_name="custom_test_rule",
            rule_checker=custom_alignment_rule,
            star=ConstellationStar.ETHICS
        )
        
        # Validate signal
        alignment_system.validate_alignment(sample_consciousness_signal)
        
        # Verify custom rule was triggered
        assert custom_rule_triggered is True

    # Auto-Fixing Tests
    def test_auto_fixing_enabled(self, alignment_system, misaligned_signal):
        """Test automatic fixing of alignment violations."""
        # Enable auto-fixing
        alignment_system.enable_auto_fixing = True
        
        # Process misaligned signal
        fixed_signal = alignment_system.process_signal_with_auto_fix(misaligned_signal)
        
        # Verify auto-fixing was applied
        assert fixed_signal is not None
        fixed_alignment = alignment_system.validate_alignment(fixed_signal)
        assert fixed_alignment.overall_alignment > misaligned_signal.coherence_score
        assert fixed_alignment.auto_fixes_applied > 0

    def test_auto_fixing_disabled(self, alignment_system, misaligned_signal):
        """Test behavior when auto-fixing is disabled."""
        # Disable auto-fixing
        alignment_system.enable_auto_fixing = False
        
        # Process signal
        result = alignment_system.process_signal_with_auto_fix(misaligned_signal)
        
        # Should return original signal without fixes
        assert result == misaligned_signal

    def test_identity_auto_fixing(self, alignment_system):
        """Test automatic fixing of identity star violations."""
        # Create signal with identity violation
        identity_violation_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.IDENTITY_VERIFICATION,
            data={"identity_auth": 0.3, "lambda_id_authenticated": False},
            source_module="identity_fix_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.4
        )
        
        # Apply auto-fix
        fixed_signal = alignment_system.auto_fix_star_violation(
            signal=identity_violation_signal,
            star=ConstellationStar.IDENTITY
        )
        
        # Verify identity fix
        assert fixed_signal.data["identity_auth"] > 0.3
        assert fixed_signal.data.get("auto_fix_applied") is True

    def test_memory_auto_fixing(self, alignment_system):
        """Test automatic fixing of memory star violations."""
        # Create signal with memory violation
        memory_violation_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.MEMORY_FOLD_UPDATE,
            data={"memory_fold": 0.2, "fold_continuity": 0.15},
            source_module="memory_fix_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.3
        )
        
        # Apply auto-fix
        fixed_signal = alignment_system.auto_fix_star_violation(
            signal=memory_violation_signal,
            star=ConstellationStar.MEMORY
        )
        
        # Verify memory fix
        assert fixed_signal.data["memory_fold"] > 0.2
        assert fixed_signal.data.get("fold_continuity_restored") is True

    def test_ethics_auto_fixing(self, alignment_system):
        """Test automatic fixing of ethics star violations."""
        # Create signal with ethics violation
        ethics_violation_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.ETHICS_VALIDATION,
            data={"ethics_compliance": 0.4, "constitutional_compliance": False},
            source_module="ethics_fix_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.45
        )
        
        # Apply auto-fix
        fixed_signal = alignment_system.auto_fix_star_violation(
            signal=ethics_violation_signal,
            star=ConstellationStar.ETHICS
        )
        
        # Verify ethics fix
        assert fixed_signal.data["ethics_compliance"] > 0.4
        assert fixed_signal.data.get("constitutional_compliance_restored") is True

    # Democratic Voting and Constitutional AI Tests
    def test_democratic_consensus_validation(self, alignment_system, constellation_alignment_data):
        """Test democratic consensus validation."""
        # Test high consensus
        assert constellation_alignment_data.democratic_consensus >= 0.8
        
        consensus_valid = alignment_system.validate_democratic_consensus(
            constellation_alignment_data.democratic_consensus
        )
        assert consensus_valid is True

    def test_low_democratic_consensus_handling(self, alignment_system):
        """Test handling of low democratic consensus."""
        # Create data with low consensus
        low_consensus_data = ConstellationAlignmentData(
            star_alignments={star: 0.5 for star in ConstellationStar},
            overall_alignment=0.5,
            critical_violations=[],
            minor_violations=[],
            auto_fixes_applied=0,
            democratic_consensus=0.3,  # Low consensus
            constitutional_compliance=True
        )
        
        consensus_valid = alignment_system.validate_democratic_consensus(
            low_consensus_data.democratic_consensus
        )
        assert consensus_valid is False

    def test_constitutional_ai_validation(self, alignment_system, constellation_alignment_data):
        """Test Constitutional AI validation."""
        # Test constitutional compliance
        assert constellation_alignment_data.constitutional_compliance is True
        
        constitutional_valid = alignment_system.validate_constitutional_compliance(
            constellation_alignment_data
        )
        assert constitutional_valid is True

    def test_constitutional_violation_detection(self, alignment_system):
        """Test detection of constitutional violations."""
        # Create data with constitutional violation
        violation_data = ConstellationAlignmentData(
            star_alignments={star: 0.8 for star in ConstellationStar},
            overall_alignment=0.8,
            critical_violations=["constitutional_violation"],
            minor_violations=[],
            auto_fixes_applied=0,
            democratic_consensus=0.9,
            constitutional_compliance=False  # Constitutional violation
        )
        
        constitutional_valid = alignment_system.validate_constitutional_compliance(
            violation_data
        )
        assert constitutional_valid is False

    def test_democratic_principle_enforcement(self, alignment_system):
        """Test enforcement of democratic principles."""
        # Test each democratic principle
        principles = [
            DemocraticPrinciple.TRANSPARENCY,
            DemocraticPrinciple.ACCOUNTABILITY,
            DemocraticPrinciple.PARTICIPATION,
            DemocraticPrinciple.PLURALITY,
            DemocraticPrinciple.RULE_OF_LAW
        ]
        
        for principle in principles:
            compliance = alignment_system.validate_democratic_principle(
                principle=principle,
                signal_data={"principle_compliance": {principle.value: 0.9}}
            )
            assert compliance is True

    # Cross-Star Coordination Tests
    def test_cross_star_dependency_resolution(self, alignment_system):
        """Test resolution of cross-star dependencies."""
        # Define dependencies: Ethics depends on Guardian, Memory depends on Identity
        dependencies = {
            ConstellationStar.ETHICS: [ConstellationStar.GUARDIAN],
            ConstellationStar.MEMORY: [ConstellationStar.IDENTITY],
            ConstellationStar.DREAM: [ConstellationStar.BIO, ConstellationStar.QUANTUM]
        }
        
        # Test dependency resolution
        resolution_order = alignment_system.resolve_star_dependencies(dependencies)
        
        # Verify dependency order
        assert resolution_order.index(ConstellationStar.GUARDIAN) < resolution_order.index(ConstellationStar.ETHICS)
        assert resolution_order.index(ConstellationStar.IDENTITY) < resolution_order.index(ConstellationStar.MEMORY)

    def test_star_coordination_synchronization(self, alignment_system):
        """Test synchronization across constellation stars."""
        # Create signals for multiple stars
        star_signals = {}
        for star in ConstellationStar:
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
                data={f"{star.value}_alignment": 0.8},
                source_module=f"{star.value}_test",
                timestamp=time.time(),
                priority=7,
                coherence_score=0.8
            )
            star_signals[star] = signal
        
        # Coordinate stars
        coordination_result = alignment_system.coordinate_stars(star_signals)
        
        # Verify coordination
        assert coordination_result.synchronized is True
        assert coordination_result.overall_coherence >= 0.7

    def test_constellation_harmony_optimization(self, alignment_system):
        """Test optimization of overall constellation harmony."""
        # Create partially aligned constellation
        partial_alignment = {
            ConstellationStar.IDENTITY: 0.7,
            ConstellationStar.MEMORY: 0.6,
            ConstellationStar.VISION: 0.8,
            ConstellationStar.BIO: 0.75,
            ConstellationStar.DREAM: 0.65,
            ConstellationStar.ETHICS: 0.9,
            ConstellationStar.GUARDIAN: 0.85,
            ConstellationStar.QUANTUM: 0.6
        }
        
        # Optimize harmony
        optimized_alignment = alignment_system.optimize_constellation_harmony(partial_alignment)
        
        # Verify optimization
        original_harmony = sum(partial_alignment.values()) / len(partial_alignment)
        optimized_harmony = sum(optimized_alignment.values()) / len(optimized_alignment)
        assert optimized_harmony >= original_harmony

    # Real-Time Monitoring Tests
    def test_real_time_monitoring_enabled(self, alignment_system):
        """Test real-time alignment monitoring."""
        # Start monitoring
        alignment_system.start_monitoring()
        
        # Verify monitoring is active
        assert alignment_system.monitor.is_monitoring is True
        assert alignment_system.monitor.monitoring_interval > 0

    def test_alignment_drift_detection(self, alignment_system):
        """Test detection of alignment drift over time."""
        # Simulate alignment drift
        initial_alignment = 0.9
        drifted_alignment = 0.6
        
        drift_detected = alignment_system.monitor.detect_alignment_drift(
            initial_alignment=initial_alignment,
            current_alignment=drifted_alignment,
            drift_threshold=0.2
        )
        
        # Should detect significant drift
        assert drift_detected is True

    def test_alignment_alert_system(self, alignment_system):
        """Test alignment alert system."""
        alerts_received = []
        
        def alert_handler(alert):
            alerts_received.append(alert)
        
        # Register alert handler
        alignment_system.register_alert_handler(alert_handler)
        
        # Trigger alignment violation
        alignment_system.trigger_alignment_alert(
            level=AlignmentLevel.CRITICAL_VIOLATION,
            star=ConstellationStar.IDENTITY,
            message="Critical identity alignment violation detected"
        )
        
        # Verify alert was received
        assert len(alerts_received) == 1
        assert alerts_received[0].level == AlignmentLevel.CRITICAL_VIOLATION

    # Performance and Scalability Tests
    def test_alignment_validation_performance(self, alignment_system, sample_consciousness_signal):
        """Test alignment validation performance."""
        start_time = time.time()
        
        # Validate many signals
        for _ in range(100):
            alignment_system.validate_alignment(sample_consciousness_signal)
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should validate quickly
        assert validation_time < 2.0  # Under 2 seconds for 100 validations
        avg_time_per_validation = validation_time / 100
        assert avg_time_per_validation < 0.02  # Under 20ms per validation

    def test_concurrent_alignment_processing(self, alignment_system):
        """Test concurrent alignment processing."""
        signals = []
        for i in range(10):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
                data={f"test_data_{i}": 0.8},
                source_module=f"concurrent_test_{i}",
                timestamp=time.time(),
                priority=5,
                coherence_score=0.8
            )
            signals.append(signal)
        
        results = []
        
        def process_signal(signal):
            result = alignment_system.validate_alignment(signal)
            results.append(result)
        
        # Process signals concurrently
        threads = []
        for signal in signals:
            thread = threading.Thread(target=process_signal, args=(signal,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Verify concurrent processing
        assert len(results) == len(signals)

    def test_memory_usage_optimization(self, alignment_system):
        """Test memory usage optimization during extended operation."""
        import gc
        
        # Get initial memory
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Process many signals
        for i in range(50):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
                data={f"memory_test_{i}": 0.8},
                source_module="memory_test",
                timestamp=time.time(),
                priority=5,
                coherence_score=0.8
            )
            alignment_system.validate_alignment(signal)
        
        # Force garbage collection
        gc.collect()
        final_objects = len(gc.get_objects())
        
        # Verify reasonable memory usage
        object_growth = final_objects - initial_objects
        assert object_growth < 500  # Should not create excessive objects

    # Error Handling and Recovery Tests
    def test_invalid_signal_handling(self, alignment_system):
        """Test handling of invalid signals."""
        # Test with None signal
        with pytest.raises(ValueError):
            alignment_system.validate_alignment(None)
        
        # Test with malformed signal data
        malformed_signal = ConsciousnessSignal(
            signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
            data=None,  # Invalid data
            source_module="error_test",
            timestamp=time.time(),
            priority=5,
            coherence_score=0.5
        )
        
        with pytest.raises(ValueError):
            alignment_system.validate_alignment(malformed_signal)

    def test_star_validation_error_recovery(self, alignment_system, sample_consciousness_signal):
        """Test error recovery in star validation."""
        # Simulate validation error for one star
        with patch.object(alignment_system.validator, 'validate_star', side_effect=[Exception("Validation failed"), 0.8]):
            # Should handle gracefully
            result = alignment_system.validate_alignment(
                sample_consciousness_signal,
                fail_gracefully=True
            )
            
            assert result is not None
            assert result.validation_errors > 0

    def test_auto_fix_error_handling(self, alignment_system, misaligned_signal):
        """Test error handling in auto-fix operations."""
        # Simulate auto-fix failure
        with patch.object(alignment_system.auto_fixer, 'fix_violation', side_effect=Exception("Fix failed")):
            # Should handle gracefully
            result = alignment_system.process_signal_with_auto_fix(
                misaligned_signal,
                fail_gracefully=True
            )
            
            assert result is not None  # Should return original signal
            assert result == misaligned_signal

    # Configuration and Customization Tests
    def test_alignment_tolerance_configuration(self):
        """Test alignment tolerance configuration."""
        # Test different tolerance levels
        strict_system = ConstellationAlignmentSystem(alignment_tolerance=0.05)
        lenient_system = ConstellationAlignmentSystem(alignment_tolerance=0.2)
        
        assert strict_system.alignment_tolerance == 0.05
        assert lenient_system.alignment_tolerance == 0.2

    def test_custom_star_weights(self, alignment_system):
        """Test custom star weighting configuration."""
        # Set custom weights emphasizing ethics and guardian
        custom_weights = {
            ConstellationStar.IDENTITY: 1.0,
            ConstellationStar.MEMORY: 1.0,
            ConstellationStar.VISION: 1.0,
            ConstellationStar.BIO: 1.0,
            ConstellationStar.DREAM: 0.8,
            ConstellationStar.ETHICS: 1.5,  # Higher weight
            ConstellationStar.GUARDIAN: 1.5,  # Higher weight
            ConstellationStar.QUANTUM: 0.7
        }
        
        alignment_system.set_star_weights(custom_weights)
        
        # Verify weights are applied
        assert alignment_system.star_weights[ConstellationStar.ETHICS] == 1.5
        assert alignment_system.star_weights[ConstellationStar.GUARDIAN] == 1.5

    # Global Function Tests
    def test_get_constellation_alignment_system_singleton(self):
        """Test global constellation alignment system singleton."""
        system1 = get_constellation_alignment_system()
        system2 = get_constellation_alignment_system()
        
        # Should return the same instance
        assert system1 is system2

    # Cleanup and Resource Management Tests
    def test_system_cleanup(self, alignment_system):
        """Test system resource cleanup."""
        # Start system with monitoring
        alignment_system.start()
        alignment_system.start_monitoring()
        
        # Cleanup
        alignment_system.cleanup()
        
        # Verify cleanup
        assert alignment_system.is_running is False
        assert alignment_system.monitor.is_monitoring is False

    def test_graceful_shutdown(self, alignment_system):
        """Test graceful system shutdown."""
        # Start system
        alignment_system.start()
        
        # Process some signals
        for i in range(5):
            signal = ConsciousnessSignal(
                signal_type=ConsciousnessSignalType.CONSTELLATION_ALIGNMENT,
                data={f"shutdown_test_{i}": 0.8},
                source_module="shutdown_test",
                timestamp=time.time(),
                priority=5,
                coherence_score=0.8
            )
            alignment_system.validate_alignment(signal)
        
        # Graceful shutdown
        alignment_system.shutdown(graceful=True, timeout=5.0)
        
        # Verify shutdown
        assert alignment_system.is_running is False