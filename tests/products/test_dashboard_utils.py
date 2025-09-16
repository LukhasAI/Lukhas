from pathlib import Path

from products.experience.dashboard.core.meta import utils


def test_smooth_time_series_and_anomalies():
    raw = [0.1, 0.2, 0.9, 0.3, 0.2]
    smoothed = utils.smooth_time_series(raw, window=3)
    assert len(smoothed) == len(raw)
    assert smoothed[2] < raw[2]

    anomalies = utils.detect_drift_anomalies(raw, threshold=1.0)
    assert anomalies == [2]


def test_persona_transition_analysis():
    transitions = [("Navigator", "Guardian"), ("Guardian", "Alchemist"), ("Alchemist", "Guardian")]
    analysis = utils.analyze_persona_transitions(transitions)
    assert analysis["dominant_transition"] in {"Guardian->Alchemist", "Alchemist->Guardian"}
    assert analysis["dominant_transition_count"] == 1


def test_guardian_correlation_and_export(tmp_path: Path):
    interventions = [{"timestamp": "2024-01-01T12:00:00+00:00"}, {"timestamp": "2024-01-01T12:04:30+00:00"}]
    drift_events = [
        {"timestamp": "2024-01-01T12:03:00+00:00", "drift_score": 0.7},
        {"timestamp": "2024-01-01T13:00:00+00:00", "drift_score": 0.2},
    ]

    correlation = utils.correlate_guardian_interventions(interventions, drift_events)
    assert correlation["correlated_events"] == 2
    assert 0.9 < correlation["correlation_ratio"] <= 1.0

    report_path = tmp_path / "report.json"
    utils.export_dashboard_report({"foo": "bar"}, report_path)
    assert report_path.exists()
    assert report_path.read_text().startswith("{\n")
