import json
from pathlib import Path
from typing import Any

from tools.scripts.generate_final_research_report import generate_comprehensive_report


def _create_system_status(path: Path) -> None:
    system_status = {
        "executive_summary": {
            "overall_health_score": 95,
            "api_status": "online",
            "test_success_rate": 98,
            "vivox_components_working": 5,
        },
        "core_modules": {f"mod{i}": {"status": "working"} for i in range(7)},
        "identity_systems": {"python_files": 10},
        "performance_metrics": {"lukhas_embedding": {"execution_time": 0.5},
        "issues_detected": [],
        "recommendations": [],
    }
    (path / "system_status_report_test.json").write_text(json.dumps(system_status))


def _create_drift_test(path: Path) -> None:
    drift = {
        "summary": {
            "providerA": {
                "status": "ok",
                "average_drift": 0.1,
                "average_trinity": 0.9,
            }
        }
    }
    (path / "simple_drift_test_test.json").write_text(json.dumps(drift))


def _create_audit(path: Path) -> None:
    audit = {"avg_drift": 0.2}
    (path / "drift_audit_test.json").write_text(json.dumps(audit))


def test_generate_comprehensive_report(tmp_path: Path, monkeypatch: Any) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    _create_system_status(data_dir)
    _create_drift_test(data_dir)
    _create_audit(data_dir)

    monkeypatch.chdir(tmp_path)

    report = generate_comprehensive_report()

    assert report["metadata"]["report_title"].startswith("LUKHAS AGI")
    # ΛTAG: test_case
    assert report["executive_summary"]["overall_system_health"] == "95.0/100"
