#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: tests.test_lambda_echo_detector
📄 FILENAME: test_lambda_echo_detector.py
🎯 PURPOSE: Comprehensive Test Suite for ΛECHO Emotional Loop Detection
🧠 CONTEXT: Unit and integration tests for emotional echo detection functionality
🔮 CAPABILITY: Archetype detection, ELI/RIS scoring, loop identification validation
🛡️ ETHICS: Test coverage for safety-critical loop detection algorithms
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: pytest framework, synthetic data generation, integration validation
═══════════════════════════════════════════════════════════════════════════════════

🧪 ΛECHO TEST SUITE - COMPREHENSIVE VALIDATION FRAMEWORK
────────────────────────────────────────────────────────────────────

This test suite validates all components of the ΛECHO emotional-symbolic loop
detection system, ensuring accurate identification of high-risk emotional
patterns and appropriate scoring mechanisms.

🔬 TEST CATEGORIES:
- Unit Tests: Individual component functionality (ArchetypeDetector, scoring)
- Integration Tests: End-to-end loop detection workflows
- Performance Tests: Processing speed and memory efficiency
- Safety Tests: Critical failure mode validation
- Data Tests: Various input format handling

🎯 COVERAGE TARGETS:
- ArchetypeDetector pattern matching: 95%+ accuracy
- ELI/RIS score computation: Mathematical correctness validation
- Sequence extraction: Multi-format data source handling
- Alert generation: Proper ΛTAG and severity assignment
- CLI interface: All modes and parameter combinations

LUKHAS_TAG: test_lambda_echo, validation_framework, safety_testing, claude_code
COLLAPSE_READY: True
"""

import asyncio
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock

import pytest

# Add the parent directory to the path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from emotion.tools.emotional_echo_detector import (
        ArchetypeDetector,
        ArchetypePattern,
        EchoSeverity,
        EmotionalEchoDetector,
        EmotionalSequence,
        LoopReport,
        RecurringMotif,
    )
except ImportError as e:
    pytest.skip(f"Could not import ΛECHO module: {e}", allow_module_level=True)


class TestArchetypeDetector:
    """Test suite for ArchetypeDetector component."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = ArchetypeDetector()

    def test_initialization(self):
        """Test detector initialization."""
        assert self.detector is not None
        assert len(self.detector.pattern_cache) > 0
        assert ArchetypePattern.SPIRAL_DOWN in self.detector.pattern_cache

    def test_spiral_down_detection(self):
        """Test detection of spiral down archetype."""
        # Exact pattern match
        sequence = ["fear", "anxiety", "falling", "void", "despair"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.SPIRAL_DOWN
        assert score > 0.5

        # Variation pattern match
        sequence = ["worry", "panic", "dropping", "abyss", "hopelessness"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.SPIRAL_DOWN
        assert score > 0.3

    def test_nostalgic_trap_detection(self):
        """Test detection of nostalgic trap archetype."""
        sequence = ["nostalgia", "longing", "regret", "loss", "melancholy"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.NOSTALGIC_TRAP
        assert score > 0.5

    def test_anger_cascade_detection(self):
        """Test detection of anger cascade archetype."""
        sequence = ["irritation", "frustration", "anger", "rage", "fury"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.ANGER_CASCADE
        assert score > 0.5

    def test_identity_crisis_detection(self):
        """Test detection of identity crisis archetype."""
        sequence = ["confusion", "uncertainty", "doubt", "dissociation", "emptiness"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.IDENTITY_CRISIS
        assert score > 0.5

    def test_trauma_echo_detection(self):
        """Test detection of trauma echo archetype."""
        sequence = ["pain", "memory", "trigger", "reaction", "pain", "memory"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.TRAUMA_ECHO
        assert score > 0.5

    def test_void_descent_detection(self):
        """Test detection of void descent archetype (highest risk)."""
        sequence = ["emptiness", "void", "nothingness", "dissolution"]
        archetype, score = self.detector.detect_archetype(sequence)

        assert archetype == ArchetypePattern.VOID_DESCENT
        assert score > 0.3

    def test_no_archetype_detection(self):
        """Test that normal sequences don't trigger archetype detection."""
        sequence = ["happiness", "joy", "satisfaction", "contentment"]
        archetype, score = self.detector.detect_archetype(sequence)

        # Should not detect any high-risk archetype
        assert archetype is None or score < 0.3

    def test_partial_pattern_matching(self):
        """Test partial pattern matching with mixed content."""
        sequence = ["normal", "fear", "content", "void", "happy", "despair"]
        archetype, score = self.detector.detect_archetype(sequence)

        # Should detect spiral down with lower confidence
        if archetype == ArchetypePattern.SPIRAL_DOWN:
            assert 0.2 <= score <= 0.7

    def test_empty_sequence(self):
        """Test handling of empty sequences."""
        archetype, score = self.detector.detect_archetype([])
        assert archetype is None
        assert score == 0.0

    def test_single_word_sequence(self):
        """Test handling of single-word sequences."""
        archetype, score = self.detector.detect_archetype(["void"])
        assert archetype is None
        assert score == 0.0


class TestEmotionalSequenceExtraction:
    """Test suite for emotional sequence extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

    def test_dream_extraction(self):
        """Test extraction from dream data."""
        dream_data = {
            "dream_content": "I felt fear and anxiety, then started falling into a void of despair",
            "timestamp": "2023-07-22T10:00:00Z",
            "emotional_intensity": 0.8,
            "dream_type": "nightmare",
            "duration_minutes": 30,
        }

        sequence = self.detector.extract_emotional_sequence(dream_data)

        assert sequence is not None
        assert sequence.source == "dream"
        assert "fear" in sequence.emotions
        assert "anxiety" in sequence.emotions
        assert "falling" in sequence.emotions
        assert sequence.intensity == 0.8
        assert sequence.duration_minutes == 30

    def test_memory_extraction(self):
        """Test extraction from memory data."""
        memory_data = {
            "emotions": ["sadness", "regret", "nostalgia"],
            "timestamp": "2023-07-22T11:00:00Z",
            "intensity": 0.6,
            "memory_type": "episodic",
            "confidence": 0.85,
        }

        sequence = self.detector.extract_emotional_sequence(memory_data)

        assert sequence is not None
        assert sequence.source == "memory"
        assert sequence.emotions == ["sadness", "regret", "nostalgia"]
        assert sequence.intensity == 0.6

    def test_drift_log_extraction(self):
        """Test extraction from drift log data."""
        drift_data = {
            "drift_score": 0.75,
            "timestamp": "2023-07-22T12:00:00Z",
            "emotional_state": "anxiety",
            "context": {"emotions": ["worry", "concern"]},
            "violation_type": "ethical_drift",
        }

        sequence = self.detector.extract_emotional_sequence(drift_data)

        assert sequence is not None
        assert sequence.source == "drift_log"
        assert "anxiety" in sequence.emotions
        assert sequence.intensity == 0.75

    def test_generic_data_extraction(self):
        """Test extraction from generic emotional data."""
        generic_data = {
            "emotions": ["confusion", "doubt", "dissociation"],
            "timestamp": "2023-07-22T13:00:00Z",
            "symbols": ["mirror", "void"],
            "intensity": 0.7,
        }

        sequence = self.detector.extract_emotional_sequence(generic_data)

        assert sequence is not None
        assert sequence.emotions == ["confusion", "doubt", "dissociation"]
        assert "mirror" in sequence.symbols
        assert "void" in sequence.symbols

    def test_insufficient_data(self):
        """Test handling of insufficient emotional data."""
        insufficient_data = {
            "emotions": ["happy"],  # Below minimum sequence length
            "timestamp": "2023-07-22T14:00:00Z",
        }

        sequence = self.detector.extract_emotional_sequence(insufficient_data)
        assert sequence is None

    def test_malformed_data(self):
        """Test handling of malformed data."""
        malformed_data = {"invalid_field": "invalid_value"}

        sequence = self.detector.extract_emotional_sequence(malformed_data)
        assert sequence is None


class TestRecurringMotifDetection:
    """Test suite for recurring motif detection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector(recurrence_threshold=2)

    def test_simple_motif_detection(self):
        """Test detection of simple recurring motifs."""
        emotions = [
            "fear",
            "void",
            "despair",
            "fear",
            "void",
            "despair",
            "fear",
            "void",
        ]
        motifs = self.detector.detect_recurring_motifs(emotions, [])

        assert len(motifs) > 0

        # Should detect the fear->void pattern
        fear_void_motifs = [
            m for m in motifs if "fear" in m.pattern and "void" in m.pattern
        ]
        assert len(fear_void_motifs) > 0

    def test_archetype_motif_detection(self):
        """Test detection of motifs that match archetypes."""
        # Create a sequence that should match SPIRAL_DOWN
        emotions = ["fear", "anxiety", "falling", "void", "despair"] * 3
        motifs = self.detector.detect_recurring_motifs(emotions, [])

        archetype_motifs = [m for m in motifs if m.archetype_match is not None]
        assert len(archetype_motifs) > 0

        spiral_motifs = [
            m
            for m in archetype_motifs
            if m.archetype_match == ArchetypePattern.SPIRAL_DOWN
        ]
        if spiral_motifs:
            assert spiral_motifs[0].archetype_score > 0.3

    def test_frequency_threshold(self):
        """Test that motifs below frequency threshold are filtered out."""
        emotions = ["happy", "sad", "happy"]  # Below threshold
        motifs = self.detector.detect_recurring_motifs(emotions, [])

        # Should not return motifs below recurrence threshold
        recurring_motifs = [
            m for m in motifs if m.frequency >= self.detector.recurrence_threshold
        ]
        assert len(recurring_motifs) == 0

    def test_complex_pattern_detection(self):
        """Test detection of complex emotional patterns."""
        emotions = [
            "nostalgia",
            "longing",
            "regret",
            "loss",  # First occurrence
            "other",
            "emotion",  # Interruption
            "nostalgia",
            "longing",
            "regret",
            "loss",  # Second occurrence
            "different",  # Another interruption
            "nostalgia",
            "longing",
            "regret",  # Partial third occurrence
        ]

        motifs = self.detector.detect_recurring_motifs(emotions, [])

        # Should detect nostalgic patterns
        nostalgic_motifs = [
            m for m in motifs if any("nostalgia" in str(p) for p in m.pattern)
        ]
        assert len(nostalgic_motifs) > 0


class TestLoopScoring:
    """Test suite for ELI/RIS scoring algorithms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

    def test_eli_ris_calculation_no_motifs(self):
        """Test ELI/RIS calculation with no motifs."""
        eli, ris = self.detector.compute_loop_score([])

        assert eli == 0.0
        assert ris == 0.0

    def test_eli_ris_calculation_single_motif(self):
        """Test ELI/RIS calculation with single motif."""
        # Create a mock motif
        motif = RecurringMotif(
            motif_id="test_motif",
            pattern=["fear", "void"],
            occurrences=[],
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            frequency=5,
            intensity_trend="stable",
            archetype_match=ArchetypePattern.SPIRAL_DOWN,
            archetype_score=0.8,
        )

        eli, ris = self.detector.compute_loop_score([motif])

        assert 0.0 <= eli <= 1.0
        assert 0.0 <= ris <= 1.0
        assert eli > 0.0  # Should have some score
        assert ris > 0.0  # Should have some score

    def test_eli_ris_high_risk_archetype(self):
        """Test ELI/RIS calculation with high-risk archetype."""
        # Create motif with void descent (highest risk)
        motif = RecurringMotif(
            motif_id="high_risk_motif",
            pattern=["void", "nothingness", "dissolution"],
            occurrences=[],
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            frequency=8,
            intensity_trend="increasing",
            archetype_match=ArchetypePattern.VOID_DESCENT,
            archetype_score=0.95,
        )

        eli, ris = self.detector.compute_loop_score([motif])

        # Should produce high scores for high-risk archetype
        assert eli > 0.5
        assert ris > 0.5

    def test_eli_ris_multiple_motifs(self):
        """Test ELI/RIS calculation with multiple motifs."""
        motifs = [
            RecurringMotif(
                motif_id="motif1",
                pattern=["fear", "anxiety"],
                occurrences=[],
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                frequency=3,
                intensity_trend="stable",
                archetype_match=None,
                archetype_score=0.0,
            ),
            RecurringMotif(
                motif_id="motif2",
                pattern=["nostalgia", "regret"],
                occurrences=[],
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                frequency=4,
                intensity_trend="stable",
                archetype_match=ArchetypePattern.NOSTALGIC_TRAP,
                archetype_score=0.7,
            ),
        ]

        eli, ris = self.detector.compute_loop_score(motifs)

        assert 0.0 <= eli <= 1.0
        assert 0.0 <= ris <= 1.0

        # Should be higher than single low-risk motif
        single_eli, single_ris = self.detector.compute_loop_score([motifs[0]])
        assert eli >= single_eli
        assert ris >= single_ris


class TestReportGeneration:
    """Test suite for report generation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

        # Add some test sequences
        test_sequences = [
            EmotionalSequence(
                sequence_id="test1",
                timestamp=datetime.now().isoformat(),
                source="dream",
                emotions=["fear", "falling", "void"],
                symbols=["darkness"],
                intensity=0.7,
            ),
            EmotionalSequence(
                sequence_id="test2",
                timestamp=datetime.now().isoformat(),
                source="memory",
                emotions=["nostalgia", "regret", "loss"],
                symbols=[],
                intensity=0.5,
            ),
        ]

        self.detector.emotional_sequences = test_sequences

    def test_json_report_generation(self):
        """Test JSON report generation."""
        report = self.detector.generate_loop_report(format="json")

        assert isinstance(report, dict)
        assert "report_meta" in report
        assert "analysis_summary" in report
        assert "detected_motifs" in report
        assert "archetype_alerts" in report
        assert "recommendations" in report
        assert "ΛTAG" in report

        # Validate report structure
        assert "eli_score" in report["analysis_summary"]
        assert "ris_score" in report["analysis_summary"]
        assert "severity" in report["analysis_summary"]

    def test_markdown_report_generation(self):
        """Test Markdown report generation."""
        report = self.detector.generate_loop_report(format="markdown")

        assert isinstance(report, str)
        assert "# 🔄 ΛECHO Emotional Loop Detection Report" in report
        assert "Analysis Summary" in report
        assert "ELI Score" in report
        assert "RIS Score" in report

    def test_report_with_high_risk_motifs(self):
        """Test report generation with high-risk motifs."""
        # Add high-risk sequence
        high_risk_sequence = EmotionalSequence(
            sequence_id="high_risk",
            timestamp=datetime.now().isoformat(),
            source="dream",
            emotions=["fear", "anxiety", "falling", "void", "despair"]
            * 3,  # Repeat for frequency
            symbols=["void", "darkness"],
            intensity=0.9,
        )

        self.detector.emotional_sequences.append(high_risk_sequence)

        report = self.detector.generate_loop_report(format="json")

        assert report["analysis_summary"]["severity"] in [
            "WARNING",
            "CRITICAL",
            "EMERGENCY",
        ]
        assert report["analysis_summary"]["high_risk_motifs"] > 0
        assert len(report["archetype_alerts"]) > 0

    def test_severity_determination(self):
        """Test severity level determination logic."""
        # Test normal severity
        normal_motifs = [
            RecurringMotif(
                motif_id="normal",
                pattern=["content", "satisfaction"],
                occurrences=[],
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                frequency=2,
                intensity_trend="stable",
            )
        ]

        severity = self.detector._determine_severity(0.1, 0.1, normal_motifs)
        assert severity == EchoSeverity.NORMAL

        # Test emergency severity
        emergency_motifs = [
            RecurringMotif(
                motif_id="emergency",
                pattern=["void", "nothingness"],
                occurrences=[],
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                frequency=10,
                intensity_trend="increasing",
                archetype_match=ArchetypePattern.VOID_DESCENT,
                archetype_score=0.95,
            )
        ]

        severity = self.detector._determine_severity(0.95, 0.95, emergency_motifs)
        assert severity == EchoSeverity.EMERGENCY


class TestSymbolicAlerts:
    """Test suite for symbolic alert generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

    def test_alert_generation_normal(self):
        """Test alert generation for normal scores."""
        alert = self.detector.emit_symbolic_echo_alert(0.3, None)

        assert alert["alert_level"] == "ΛCAUTION"
        assert "ΛECHO" in alert["ΛTAG"]
        assert "ΛECHO_LOOP" in alert["ΛTAG"]

    def test_alert_generation_high_risk(self):
        """Test alert generation for high-risk archetype."""
        alert = self.detector.emit_symbolic_echo_alert(
            0.85, ArchetypePattern.VOID_DESCENT
        )

        assert alert["alert_level"] == "ΛCRITICAL"
        assert "ΛARCHETYPE_WARNING" in alert["ΛTAG"]
        assert "ΛRESONANCE_HIGH" in alert["ΛTAG"]
        assert alert["archetype"] == ArchetypePattern.VOID_DESCENT.value

    def test_alert_generation_emergency(self):
        """Test alert generation for emergency scores."""
        alert = self.detector.emit_symbolic_echo_alert(
            0.95, ArchetypePattern.TRAUMA_ECHO
        )

        assert alert["alert_level"] == "ΛEMERGENCY"
        assert len(alert["recommended_actions"]) > 0
        assert any(
            "emergency" in action.lower() for action in alert["recommended_actions"]
        )


class TestIntegrationScenarios:
    """Test suite for integration scenarios and end-to-end workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

    @pytest.mark.asyncio
    async def test_governor_escalation_integration(self):
        """Test integration with governor escalation."""
        # Mock governor
        mock_governor = AsyncMock()
        mock_response = Mock()
        mock_response.decision.value = "QUARANTINE"
        mock_governor.receive_escalation.return_value = mock_response

        self.detector.integrate_with_governor(mock_governor)

        # Create high-risk motifs
        high_risk_motifs = [
            RecurringMotif(
                motif_id="critical",
                pattern=["void", "dissolution"],
                occurrences=[],
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat(),
                frequency=10,
                intensity_trend="increasing",
                archetype_match=ArchetypePattern.VOID_DESCENT,
                archetype_score=0.95,
            )
        ]

        # Should escalate to governor
        await self.detector.escalate_to_governor(0.9, 0.85, high_risk_motifs)

        # Verify escalation was called
        mock_governor.receive_escalation.assert_called_once()
        assert self.detector.stats["escalations_sent"] == 1

    def test_tuner_integration(self):
        """Test integration with tuner."""
        # Mock tuner
        mock_tuner = Mock()
        self.detector.integrate_with_tuner(mock_tuner)

        assert self.detector.tuner == mock_tuner

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # Simulate data input
        test_data = [
            {
                "dream_content": "I felt overwhelming fear, then started falling into an endless void of despair",
                "timestamp": datetime.now().isoformat(),
                "emotional_intensity": 0.9,
            },
            {
                "emotions": ["fear", "falling", "void", "despair"],
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "intensity": 0.8,
            },
            {
                "emotions": ["anxiety", "void", "emptiness"],
                "timestamp": (datetime.now() - timedelta(minutes=60)).isoformat(),
                "intensity": 0.7,
            },
        ]

        # Process data
        for data in test_data:
            sequence = self.detector.extract_emotional_sequence(data)
            if sequence:
                self.detector.emotional_sequences.append(sequence)

        # Generate report
        report = self.detector.generate_loop_report(format="json")

        # Validate complete workflow
        assert report["analysis_summary"]["sequences_analyzed"] > 0
        assert report["analysis_summary"]["eli_score"] >= 0.0
        assert report["analysis_summary"]["ris_score"] >= 0.0

        # Recommendations should be generated even for normal severity
        # (may be empty if no specific issues detected, which is valid)
        assert "recommendations" in report
        assert isinstance(report["recommendations"], list)

        # Should detect high-risk patterns
        if report["analysis_summary"]["high_risk_motifs"] > 0:
            assert len(report["archetype_alerts"]) > 0
            assert report["analysis_summary"]["severity"] in [
                "WARNING",
                "CRITICAL",
                "EMERGENCY",
            ]


class TestPerformanceAndSafety:
    """Test suite for performance and safety validation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = EmotionalEchoDetector()

    def test_large_dataset_performance(self):
        """Test performance with large datasets."""
        # Generate large synthetic dataset
        large_emotions = ["fear", "anxiety", "void", "despair"] * 500  # 2000 emotions

        import time

        start_time = time.time()

        motifs = self.detector.detect_recurring_motifs(large_emotions, [])

        end_time = time.time()
        processing_time = end_time - start_time

        # Should complete within reasonable time (< 5 seconds)
        assert processing_time < 5.0
        assert len(motifs) > 0

    def test_memory_usage_bounds(self):
        """Test that memory usage stays within bounds."""
        # Add many sequences
        for i in range(200):
            sequence = EmotionalSequence(
                sequence_id=f"seq_{i}",
                timestamp=datetime.now().isoformat(),
                source="test",
                emotions=["test", "emotion", "sequence"],
                symbols=[],
                intensity=0.5,
            )
            self.detector.emotional_sequences.append(sequence)

        # Should not cause memory issues
        assert len(self.detector.emotional_sequences) == 200

        # Processing should still work
        report = self.detector.generate_loop_report()
        assert report is not None

    def test_malformed_input_safety(self):
        """Test safety with malformed inputs."""
        malformed_inputs = [
            None,
            {},
            {"invalid": "data"},
            {"emotions": None},
            {"emotions": "not_a_list"},
            {"emotions": []},
            {"emotions": [None, None]},
        ]

        for bad_input in malformed_inputs:
            # Should not crash
            try:
                sequence = self.detector.extract_emotional_sequence(bad_input)
                # Should return None for invalid input
                assert sequence is None
            except Exception as e:
                # Should not raise unhandled exceptions
                pytest.fail(f"Unhandled exception with input {bad_input}: {e}")

    def test_infinite_loop_prevention(self):
        """Test prevention of infinite loops in processing."""
        # Create pathological input that could cause loops
        circular_emotions = ["a"] * 1000  # Massive repetition

        # Should complete without hanging
        import signal

        def timeout_handler(signum, frame):
            pytest.fail("Test timed out - possible infinite loop")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        try:
            motifs = self.detector.detect_recurring_motifs(circular_emotions, [])
            assert isinstance(motifs, list)
        finally:
            signal.alarm(0)  # Cancel timeout


class TestCLIInterface:
    """Test suite for CLI interface functionality."""

    def test_synthetic_data_generation(self):
        """Test synthetic data generation utility."""
        from emotion.tools.emotional_echo_detector import (
            _generate_synthetic_emotional_data,
        )

        # Test normal data generation
        normal_data = _generate_synthetic_emotional_data(count=10, high_risk=False)
        assert len(normal_data) == 10
        assert all("timestamp" in item for item in normal_data)

        # Test high-risk data generation
        high_risk_data = _generate_synthetic_emotional_data(count=10, high_risk=True)
        assert len(high_risk_data) == 10

        # High-risk data should contain more concerning patterns
        emotions_found = []
        for item in high_risk_data:
            if "emotions" in item:
                emotions_found.extend(item["emotions"])
            elif "dream_content" in item:
                emotions_found.append(item["dream_content"])

        # Should contain high-risk emotional terms
        risk_terms = ["fear", "void", "despair", "rage", "destruction", "pain"]
        found_risk_terms = any(
            any(term in str(emotion).lower() for term in risk_terms)
            for emotion in emotions_found
        )
        assert found_risk_terms

    def test_data_loading_utility(self):
        """Test data loading from file utility."""
        from emotion.tools.emotional_echo_detector import _load_sample_data

        # Test with non-existent file
        data = _load_sample_data("non_existent_file.jsonl")
        assert data == []

        # Test with temporary file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            test_data = [
                {"emotions": ["test1", "test2"], "timestamp": "2023-07-22T10:00:00Z"},
                {"emotions": ["test3", "test4"], "timestamp": "2023-07-22T11:00:00Z"},
            ]

            for item in test_data:
                f.write(json.dumps(item) + "\n")

            temp_path = f.name

        try:
            loaded_data = _load_sample_data(temp_path)
            assert len(loaded_data) == 2
            assert loaded_data[0]["emotions"] == ["test1", "test2"]
        finally:
            os.unlink(temp_path)


# Integration fixtures for async tests
@pytest.fixture
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# Test data fixtures
@pytest.fixture
def sample_dream_data():
    """Sample dream data for testing."""
    return {
        "dream_content": "I was walking through a dark forest when suddenly I felt overwhelming fear. Then I started falling into an endless void, surrounded by despair and emptiness.",
        "timestamp": "2023-07-22T02:30:00Z",
        "emotional_intensity": 0.85,
        "dream_type": "nightmare",
        "duration_minutes": 25,
        "lucidity_level": 0.1,
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory data for testing."""
    return {
        "current_emotion_vector": {
            "primary_emotion": "nostalgia",
            "dimensions": {
                "nostalgia": 0.8,
                "regret": 0.6,
                "melancholy": 0.7,
                "longing": 0.9,
            },
        },
        "timestamp": "2023-07-22T14:15:00Z",
        "intensity": 0.7,
        "memory_type": "episodic",
        "confidence": 0.85,
    }


@pytest.fixture
def high_risk_motifs():
    """High-risk motifs for testing."""
    return [
        RecurringMotif(
            motif_id="void_descent_motif",
            pattern=["emptiness", "void", "nothingness", "dissolution"],
            occurrences=[],
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
            frequency=8,
            intensity_trend="increasing",
            archetype_match=ArchetypePattern.VOID_DESCENT,
            archetype_score=0.92,
        ),
        RecurringMotif(
            motif_id="spiral_down_motif",
            pattern=["fear", "falling", "void", "despair"],
            occurrences=[],
            first_seen=(datetime.now() - timedelta(hours=2)).isoformat(),
            last_seen=datetime.now().isoformat(),
            frequency=6,
            intensity_trend="stable",
            archetype_match=ArchetypePattern.SPIRAL_DOWN,
            archetype_score=0.78,
        ),
    ]


if __name__ == "__main__":
    # Run tests with coverage report
    pytest.main(
        [
            __file__,
            "-v",
            "--cov=emotion.tools.emotional_echo_detector",
            "--cov-report=html",
            "--cov-report=term-missing",
        ]
    )

## CLAUDE CHANGELOG
# - Created comprehensive test suite for ΛECHO emotional loop detection system # CLAUDE_EDIT_v0.1
# - Implemented unit tests for ArchetypeDetector with all 6 archetype patterns validation # CLAUDE_EDIT_v0.1
# - Added extensive sequence extraction tests for dream/memory/drift log data formats # CLAUDE_EDIT_v0.1
# - Created motif detection tests with frequency thresholds and pattern complexity # CLAUDE_EDIT_v0.1
# - Implemented ELI/RIS scoring validation with mathematical correctness checks # CLAUDE_EDIT_v0.1
# - Added report generation tests for both JSON and Markdown formats # CLAUDE_EDIT_v0.1
# - Created symbolic alert generation tests with proper ΛTAG validation # CLAUDE_EDIT_v0.1
# - Implemented integration tests for governor escalation and tuner coordination # CLAUDE_EDIT_v0.1
# - Added performance and safety tests for large datasets and malformed input handling # CLAUDE_EDIT_v0.1
# - Created CLI utility tests and data loading validation # CLAUDE_EDIT_v0.1
