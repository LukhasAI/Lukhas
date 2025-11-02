"""Tests for the drift dream CLI scaffold."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from oneiric_core.tools.drift_dream_test import (
    DriftDreamProbeRequest,
    generate_probe_report,
    run_cli,
    write_report,
)


@pytest.fixture
def tmp_report_path(tmp_path: Path) -> Path:
    """Provide a temporary report destination."""

    return tmp_path / "report.json"


def test_generate_probe_report_is_deterministic() -> None:
    """Seeded probes should emit deterministic symbolic metrics."""

    request = DriftDreamProbeRequest(symbol="LOYALTY", user="demo", seed=7, recursive=False)
    report_one = generate_probe_report(request)
    report_two = generate_probe_report(request)
    # Timestamp is generated at runtime; compare stable keys only.
    for key in ("symbol", "driftDelta", "driftScore", "affect_delta", "top_symbols"):
        assert report_one[key] == report_two[key]
    assert report_one["telemetry"]["attempts"] == 1


def test_write_report_persists_json(tmp_report_path: Path) -> None:
    """Reports are serialized to JSON with expected keys."""

    request = DriftDreamProbeRequest(symbol="LOYALTY", user="demo", seed=7, recursive=True)
    report = generate_probe_report(request)
    output_path = write_report(report, tmp_report_path)
    assert output_path == tmp_report_path
    payload = json.loads(output_path.read_text())
    assert {"symbol", "driftDelta", "top_symbols"}.issubset(payload)


def test_run_cli_creates_artifact(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI run writes artifact and returns structured payload."""

    monkeypatch.chdir(tmp_path)
    result = run_cli(["--symbol", "LOYALTY", "--user", "demo", "--seed", "5"])
    assert result["symbol"] == "LOYALTY"
    assert Path("codex_artifacts/dream_drift_report.json").exists()
    data = json.loads(Path("codex_artifacts/dream_drift_report.json").read_text())
    assert data["telemetry"]["successes"] == 1
