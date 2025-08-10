"""
Unit tests for Symbolic Anomaly Explorer.

Tests the core functionality of dream session analysis, anomaly detection,
and report generation for the Jules-13 system.
"""

import json
import shutil
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from dream.tools.symbolic_anomaly_explorer import (
    AnomalySeverity,
    AnomalyType,
    DreamSession,
    SymbolicAnomaly,
    SymbolicAnomalyExplorer,
    analyze_recent_dreams,
)


@pytest.fixture
def temp_storage():
    """Create temporary storage directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_dream_sessions():
    """Create sample dream sessions for testing."""
    base_time = datetime.now(timezone.utc)

    sessions = [
        DreamSession(
            session_id="DREAM_001",
            timestamp=(base_time - timedelta(hours=2)).isoformat(),
            symbolic_tags=["eye_watcher", "golden_spiral", "ΛDRIFT"],
            emotional_state={"curiosity": 0.8, "anxiety": 0.2},
            content="Dream exploring eye_watcher and golden_spiral with ΛDRIFT patterns",
            drift_score=0.3,
            narrative_elements=["exploration", "discovery", "wonder"],
        ),
        DreamSession(
            session_id="DREAM_002",
            timestamp=(base_time - timedelta(hours=1)).isoformat(),
            symbolic_tags=["eye_watcher", "shattered_circle", "ΛFEAR"],
            emotional_state={"fear": 0.9, "curiosity": 0.1},
            content="Conflicting symbols eye_watcher and shattered_circle with ΛFEAR",
            drift_score=0.6,
            narrative_elements=["conflict", "tension", "uncertainty"],
        ),
        DreamSession(
            session_id="DREAM_003",
            timestamp=base_time.isoformat(),
            symbolic_tags=["recursive_mirror", "void_whisper", "ΛLOOP"],
            emotional_state={"confusion": 0.7, "fear": 0.8, "hope": 0.1},
            content="Recursive patterns with void_whisper creating ΛLOOP structures",
            drift_score=0.85,
            narrative_elements=["repetition", "loop", "escape"],
        ),
    ]

    return sessions


@pytest.fixture
def explorer(temp_storage):
    """Create explorer instance with temporary storage."""
    return SymbolicAnomalyExplorer(storage_path=temp_storage, drift_integration=False)


class TestSymbolicAnomalyExplorer:
    """Test suite for SymbolicAnomalyExplorer."""

    def test_initialization(self, temp_storage):
        """Test explorer initialization."""
        explorer = SymbolicAnomalyExplorer(
            storage_path=temp_storage, drift_integration=False
        )

        assert explorer.storage_path == Path(temp_storage)
        assert explorer.storage_path.exists()
        assert not explorer.drift_integration
        assert len(explorer.thresholds) > 0
        assert explorer.min_pattern_frequency == 3

    def test_dream_session_creation(self):
        """Test dream session data structure."""
        session = DreamSession(
            session_id="TEST_001",
            timestamp="2025-07-22T10:00:00Z",
            symbolic_tags=["test_symbol", "ΛTEST"],
            emotional_state={"test": 0.5},
            content="Test content with ΛTEST tag",
            drift_score=0.4,
            narrative_elements=["test_narrative"],
        )

        assert session.session_id == "TEST_001"
        assert len(session.extract_lambda_tags()) == 1
        assert session.extract_lambda_tags()[0] == "ΛTEST"
        assert session.calculate_symbolic_density() > 0

    def test_load_recent_dreams_synthetic(self, explorer):
        """Test loading synthetic dreams when no files exist."""
        dreams = explorer.load_recent_dreams(5)

        assert len(dreams) == 5
        assert all(isinstance(d, DreamSession) for d in dreams)
        assert all(d.session_id.startswith("DREAM_") for d in dreams)
        assert all(len(d.symbolic_tags) > 0 for d in dreams)

    def test_load_dreams_from_files(
        self, explorer, temp_storage, sample_dream_sessions
    ):
        """Test loading dreams from JSON files."""
        # Create sample JSON files
        for i, session in enumerate(sample_dream_sessions):
            file_path = Path(temp_storage) / f"dream_{i:03d}.json"
            session_data = {
                "session_id": session.session_id,
                "timestamp": session.timestamp,
                "symbolic_tags": session.symbolic_tags,
                "emotional_state": session.emotional_state,
                "content": session.content,
                "drift_score": session.drift_score,
                "narrative_elements": session.narrative_elements,
            }

            with open(file_path, "w") as f:
                json.dump(session_data, f)

        # Load dreams
        dreams = explorer.load_recent_dreams(10)

        assert len(dreams) == 3  # Should load our 3 files
        assert all(isinstance(d, DreamSession) for d in dreams)
        assert dreams[0].session_id in [s.session_id for s in sample_dream_sessions]

    def test_detect_symbolic_conflicts(self, explorer, sample_dream_sessions):
        """Test symbolic conflict detection."""
        anomalies = explorer.detect_symbolic_anomalies(sample_dream_sessions)

        # Should detect conflict in DREAM_002 (eye_watcher vs shattered_circle)
        conflict_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.SYMBOLIC_CONFLICT
        ]
        assert len(conflict_anomalies) > 0

        # Check conflict anomaly details
        conflict = conflict_anomalies[0]
        assert conflict.severity in [
            AnomalySeverity.MODERATE,
            AnomalySeverity.SIGNIFICANT,
        ]
        assert "DREAM_002" in conflict.affected_sessions
        assert len(conflict.recommendations) > 0

    def test_detect_recursive_loops(self, explorer):
        """Test recursive loop detection."""
        # Create sessions with recursive patterns
        loop_sessions = []
        for i in range(5):
            session = DreamSession(
                session_id=f"LOOP_{i:03d}",
                timestamp=datetime.now().isoformat(),
                symbolic_tags=["recursive_mirror", "void_whisper"]
                * 2,  # Repeating pattern
                emotional_state={"confusion": 0.7},
                content="Recursive mirror patterns",
                drift_score=0.5,
                narrative_elements=["loop", "repetition"],
            )
            loop_sessions.append(session)

        anomalies = explorer.detect_symbolic_anomalies(loop_sessions)

        # Should detect recursive loops
        loop_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.RECURSIVE_LOOP
        ]
        assert len(loop_anomalies) > 0

        loop_anomaly = loop_anomalies[0]
        assert "recursive" in loop_anomaly.description.lower()
        assert len(loop_anomaly.affected_sessions) > 0

    def test_detect_emotional_dissonance(self, explorer, sample_dream_sessions):
        """Test emotional dissonance detection."""
        anomalies = explorer.detect_symbolic_anomalies(sample_dream_sessions)

        # DREAM_003 has high fear (0.8) and low hope (0.1) - should trigger dissonance
        dissonance_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.EMOTIONAL_DISSONANCE
        ]
        assert len(dissonance_anomalies) > 0

        dissonance = dissonance_anomalies[0]
        assert "DREAM_003" in dissonance.affected_sessions
        assert dissonance.confidence > 0

    def test_detect_drift_acceleration(self, explorer, sample_dream_sessions):
        """Test drift acceleration detection."""
        anomalies = explorer.detect_symbolic_anomalies(sample_dream_sessions)

        # Sessions have drift scores: 0.3 -> 0.6 -> 0.85 (acceleration)
        drift_anomalies = [
            a for a in anomalies if a.anomaly_type == AnomalyType.DRIFT_ACCELERATION
        ]
        assert len(drift_anomalies) > 0

        drift_anomaly = drift_anomalies[0]
        assert drift_anomaly.severity in [
            AnomalySeverity.SIGNIFICANT,
            AnomalySeverity.CRITICAL,
        ]
        assert "acceleration" in drift_anomaly.description.lower()

    def test_generate_anomaly_report(self, explorer, sample_dream_sessions):
        """Test anomaly report generation."""
        anomalies = explorer.detect_symbolic_anomalies(sample_dream_sessions)
        report = explorer.generate_anomaly_report(anomalies)

        assert report.report_id.startswith("ANOMALY_REPORT_")
        assert report.sessions_analyzed > 0
        assert len(report.anomalies_detected) == len(anomalies)
        assert 0 <= report.overall_risk_score <= 1
        assert len(report.summary) > 0
        assert report.symbolic_trends is not None

    def test_summarize_symbolic_trends(self, explorer, sample_dream_sessions):
        """Test symbolic trend analysis."""
        trends = explorer.summarize_symbolic_trends(sample_dream_sessions)

        assert trends["sessions_analyzed"] == 3
        assert trends["total_symbols"] > 0
        assert trends["unique_symbols"] > 0
        assert "top_symbols" in trends
        assert "lambda_frequency" in trends
        assert trends["drift_trend"] in ["stable", "increasing", "decreasing"]
        assert 0 <= trends["average_drift_score"] <= 1

    def test_export_report_json(self, explorer, temp_storage):
        """Test JSON report export."""
        # Create minimal report
        from dream.tools.symbolic_anomaly_explorer import AnomalyReport

        report = AnomalyReport(
            report_id="TEST_REPORT",
            timestamp=datetime.now().isoformat(),
            sessions_analyzed=3,
            anomalies_detected=[],
            symbolic_trends={},
            overall_risk_score=0.3,
            summary="Test report",
            recommendations=["Test recommendation"],
        )

        json_path = explorer.export_report_json(report)

        assert Path(json_path).exists()

        # Verify JSON content
        with open(json_path) as f:
            data = json.load(f)

        assert data["report_id"] == "TEST_REPORT"
        assert data["overall_risk_score"] == 0.3
        assert data["summary"] == "Test report"

    def test_export_summary_markdown(self, explorer, temp_storage):
        """Test Markdown summary export."""
        from dream.tools.symbolic_anomaly_explorer import AnomalyReport

        # Create report with test anomaly
        test_anomaly = SymbolicAnomaly(
            anomaly_id="TEST_ANOMALY",
            anomaly_type=AnomalyType.SYMBOLIC_CONFLICT,
            severity=AnomalySeverity.MODERATE,
            confidence=0.6,
            description="Test anomaly description",
            affected_sessions=["TEST_001"],
            symbolic_elements=["test_symbol"],
            metrics={"test_metric": 0.5},
            recommendations=["Test recommendation"],
        )

        report = AnomalyReport(
            report_id="TEST_REPORT",
            timestamp=datetime.now().isoformat(),
            sessions_analyzed=1,
            anomalies_detected=[test_anomaly],
            symbolic_trends={},
            overall_risk_score=0.4,
            summary="Test report with anomaly",
            recommendations=["Overall recommendation"],
        )

        md_path = explorer.export_summary_markdown(report)

        assert Path(md_path).exists()

        # Verify Markdown content
        with open(md_path) as f:
            content = f.read()

        assert "# Symbolic Anomaly Report" in content
        assert "TEST_REPORT" in content
        assert "Test anomaly description" in content
        assert "## Overall Recommendations" in content

    def test_display_ascii_heatmap(self, explorer):
        """Test ASCII heatmap generation."""
        # Create test anomalies with different severities
        anomalies = [
            SymbolicAnomaly(
                anomaly_id="MINOR_001",
                anomaly_type=AnomalyType.SYMBOLIC_CONFLICT,
                severity=AnomalySeverity.MINOR,
                confidence=0.3,
                description="Minor anomaly",
                affected_sessions=["TEST_001"],
                symbolic_elements=[],
                metrics={},
            ),
            SymbolicAnomaly(
                anomaly_id="CRITICAL_001",
                anomaly_type=AnomalyType.DRIFT_ACCELERATION,
                severity=AnomalySeverity.CRITICAL,
                confidence=0.9,
                description="Critical anomaly",
                affected_sessions=["TEST_002"],
                symbolic_elements=[],
                metrics={},
            ),
        ]

        from dream.tools.symbolic_anomaly_explorer import AnomalyReport

        report = AnomalyReport(
            report_id="HEATMAP_TEST",
            timestamp=datetime.now().isoformat(),
            sessions_analyzed=2,
            anomalies_detected=anomalies,
            symbolic_trends={},
            overall_risk_score=0.6,
            summary="Test heatmap",
            recommendations=[],
        )

        heatmap = explorer.display_ascii_heatmap(report)

        assert "ANOMALY HEATMAP" in heatmap
        assert "minor" in heatmap.lower()
        assert "critical" in heatmap.lower()
        assert "Risk Level:" in heatmap

    def test_tag_registry_updates(self, explorer, sample_dream_sessions):
        """Test symbolic tag registry updates."""
        # Process sessions to update registry
        explorer._update_tag_registry(sample_dream_sessions)

        assert len(explorer.tag_registry) > 0
        assert "eye_watcher" in explorer.tag_registry

        # Check tag properties
        eye_watcher_tag = explorer.tag_registry["eye_watcher"]
        assert eye_watcher_tag.frequency == 2  # Appears in DREAM_001 and DREAM_002
        assert len(eye_watcher_tag.sessions) == 2
        assert eye_watcher_tag.emotional_weight > 0

    def test_severity_calculation(self, explorer):
        """Test severity calculation from scores."""
        assert explorer._calculate_severity(0.1) == AnomalySeverity.MINOR
        assert explorer._calculate_severity(0.3) == AnomalySeverity.MODERATE
        assert explorer._calculate_severity(0.5) == AnomalySeverity.SIGNIFICANT
        assert explorer._calculate_severity(0.7) == AnomalySeverity.CRITICAL
        assert explorer._calculate_severity(0.9) == AnomalySeverity.CATASTROPHIC

    def test_threshold_customization(self, temp_storage):
        """Test threshold customization."""
        custom_thresholds = {"emotional_dissonance": 0.2, "symbolic_conflict": 0.1}

        explorer = SymbolicAnomalyExplorer(storage_path=temp_storage)
        explorer.thresholds.update(custom_thresholds)

        assert explorer.thresholds["emotional_dissonance"] == 0.2
        assert explorer.thresholds["symbolic_conflict"] == 0.1

    def test_empty_sessions_handling(self, explorer):
        """Test handling of empty session lists."""
        # Test with empty list
        anomalies = explorer.detect_symbolic_anomalies([])
        assert len(anomalies) == 0

        trends = explorer.summarize_symbolic_trends([])
        assert trends == {}

        report = explorer.generate_anomaly_report([])
        assert report.overall_risk_score == 0.0
        assert "NOMINAL" in report.summary


class TestConvenienceFunctions:
    """Test convenience functions for CLI usage."""

    @patch("symbolic_anomaly_explorer.SymbolicAnomalyExplorer")
    def test_analyze_recent_dreams(self, mock_explorer_class):
        """Test analyze_recent_dreams convenience function."""
        # Mock the explorer and its methods
        mock_explorer = Mock()
        mock_explorer.load_recent_dreams.return_value = []
        mock_explorer.detect_symbolic_anomalies.return_value = []
        mock_explorer.generate_anomaly_report.return_value = Mock()

        mock_explorer_class.return_value = mock_explorer

        # Call function
        result = analyze_recent_dreams(5, "/test/path")

        # Verify calls
        mock_explorer_class.assert_called_once_with(storage_path="/test/path")
        mock_explorer.load_recent_dreams.assert_called_once_with(5)
        mock_explorer.detect_symbolic_anomalies.assert_called_once()
        mock_explorer.generate_anomaly_report.assert_called_once()

        assert result is not None


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_invalid_session_data(self, explorer, temp_storage):
        """Test handling of invalid session data."""
        # Create invalid JSON file
        invalid_file = Path(temp_storage) / "invalid.json"
        with open(invalid_file, "w") as f:
            f.write("invalid json content")

        # Should handle gracefully
        dreams = explorer.load_recent_dreams(10)
        assert len(dreams) > 0  # Should still generate synthetic data

    def test_missing_fields_in_session(self, explorer, temp_storage):
        """Test handling of missing fields in session data."""
        # Create session with missing fields
        minimal_session = {
            "session_id": "MINIMAL_001"
            # Missing other required fields
        }

        session_file = Path(temp_storage) / "minimal.json"
        with open(session_file, "w") as f:
            json.dump(minimal_session, f)

        dreams = explorer.load_recent_dreams(10)

        # Should load successfully with defaults
        assert len(dreams) > 0
        loaded_session = next(
            (d for d in dreams if d.session_id == "MINIMAL_001"), None
        )
        if loaded_session:
            assert loaded_session.symbolic_tags == []
            assert loaded_session.emotional_state == {}

    def test_extreme_drift_values(self, explorer):
        """Test handling of extreme drift values."""
        extreme_session = DreamSession(
            session_id="EXTREME_001",
            timestamp=datetime.now().isoformat(),
            symbolic_tags=["test"],
            emotional_state={"extreme": 1.0},
            content="Extreme test",
            drift_score=2.0,  # Invalid high value
            narrative_elements=["extreme"],
        )

        # Should handle gracefully
        anomalies = explorer.detect_symbolic_anomalies([extreme_session])
        assert isinstance(anomalies, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
