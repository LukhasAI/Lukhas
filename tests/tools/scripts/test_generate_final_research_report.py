from pathlib import Path

from tools.scripts.generate_final_research_report import (
    generate_comprehensive_report,
    save_comprehensive_report,
)


def test_generate_and_save_report(tmp_path: Path) -> None:
    report = generate_comprehensive_report()
    assert "metadata" in report

    file_path = tmp_path / "report.json"
    saved = save_comprehensive_report(report, filename=str(file_path))
    assert Path(saved).exists()
