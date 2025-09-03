from pathlib import Path

from tools.scripts.generate_final_research_report import generate_comprehensive_report


def test_generate_comprehensive_report_empty(tmp_path: Path, monkeypatch) -> None:
    """Generate report with no data and verify structure."""
    monkeypatch.chdir(tmp_path)
    report = generate_comprehensive_report()

    # ΛTAG: report_generation_test
    assert report["metadata"]["components_analyzed"] == 0
    assert "executive_summary" in report
