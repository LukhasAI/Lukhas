import json

from ethics import monitor


def test_self_reflection(tmp_path):
    monitor.DEI_LOG_PATH = tmp_path / "log.json"
    decisions = [
        {"alignment_score": 0.95, "demographic": "A"},
        {"alignment_score": 0.8, "demographic": "B"},
    ]
    report = monitor.self_reflection_report(decisions, compliance_threshold=0.9)
    assert monitor.DEI_LOG_PATH.exists()
    data = json.loads(monitor.DEI_LOG_PATH.read_text())
    assert len(data) == 1
    assert report["demographic_distribution"]["A"] == 1
