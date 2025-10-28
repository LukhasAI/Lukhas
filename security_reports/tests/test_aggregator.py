"""Tests for the :mod:`security_reports.aggregator` module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from security_reports.aggregator import SecurityReportAggregator, SecurityReportError


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data), encoding="utf-8")


def test_aggregator_combines_reports(tmp_path: Path) -> None:
    reports_dir = tmp_path
    write_json(
        reports_dir / "pip-audit.json",
        [
            {
                "name": "demo",
                "version": "1.0.0",
                "vulns": [
                    {
                        "id": "GHSA-123",
                        "severity": "HIGH",
                        "description": "Demo vulnerability",
                        "fix_versions": ["1.0.1"],
                    }
                ],
            }
        ],
    )
    write_json(
        reports_dir / "safety-report.json",
        {
            "vulnerabilities": [
                {
                    "dependency": {
                        "package_name": "demo",
                        "installed_version": "1.0.0",
                    },
                    "vulnerability_id": "GHSA-123",
                    "severity": "critical",
                    "advisory": "Upgrade required",
                    "fix_versions": ["1.1.0"],
                },
                {
                    "dependency": {
                        "package_name": "utility",
                        "installed_version": "0.9.0",
                    },
                    "vulnerability_id": "SAFE-456",
                    "severity": "low",
                    "advisory": "Minor issue",
                },
            ]
        },
    )
    write_json(
        reports_dir / "bandit.json",
        {
            "results": [
                {"issue_severity": "LOW"},
                {"issue_severity": "HIGH"},
            ]
        },
    )

    aggregator = SecurityReportAggregator(reports_dir)
    summary = aggregator.summarize()

    assert summary.bandit_issue_count == 2
    assert summary.missing_reports == ()
    assert summary.total_vulnerabilities == 2

    merged = {record.identifier: record for record in summary.vulnerabilities}
    demo_record = merged["GHSA-123"]
    assert demo_record.package == "demo"
    assert demo_record.severity == "CRITICAL"  # safety severity wins
    assert set(demo_record.fix_versions) == {"1.0.1", "1.1.0"}
    assert set(demo_record.sources) == {"pip-audit", "safety"}

    utility_record = merged["SAFE-456"]
    assert utility_record.package == "utility"
    assert utility_record.installed_version == "0.9.0"
    assert utility_record.severity == "LOW"


def test_aggregator_reports_missing_inputs(tmp_path: Path) -> None:
    reports_dir = tmp_path
    write_json(reports_dir / "pip-audit.json", [])

    summary = SecurityReportAggregator(reports_dir).summarize()

    assert summary.bandit_issue_count == 0
    assert summary.total_vulnerabilities == 0
    assert set(summary.missing_reports) == {"bandit", "safety"}


def test_invalid_json_raises(tmp_path: Path) -> None:
    reports_dir = tmp_path
    (reports_dir / "bandit.json").write_text("not-json", encoding="utf-8")

    aggregator = SecurityReportAggregator(reports_dir)

    with pytest.raises(SecurityReportError):
        aggregator.summarize()
