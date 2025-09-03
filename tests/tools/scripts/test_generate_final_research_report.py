from tools.scripts.generate_final_research_report import (
    generate_comprehensive_report,
)


def test_generate_comprehensive_report_no_data(tmp_path, monkeypatch):
    """Report generation works without existing data"""
    # ΛTAG: report_generation
    monkeypatch.chdir(tmp_path)

    report = generate_comprehensive_report()

    assert "metadata" in report
    assert report["executive_summary"]["key_findings"] == []
    # TODO: expand coverage
