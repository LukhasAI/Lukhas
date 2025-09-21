"""Tests for the collapse simulator CLI scaffolding."""
from __future__ import annotations

import json
import pathlib

import pytest

from lukhas.tools import collapse_simulator_main
from lukhas.tools.collapse_simulator import (
    DEFAULT_OUTPUT_PATH,
    SimulationContext,
    compile_summary,
    derive_top_symbols,
    simulate_collapse,
)


def test_simulate_collapse_creates_artifact(tmp_path: pathlib.Path) -> None:
    """The simulator should emit a JSON artifact with required fields."""

    output_path = tmp_path / "collapse_report.json"
    summary = simulate_collapse(
        scenario="memory",
        iterations=2,
        noise=0.01,
        output_path=output_path,
        seed_override=42,
    )

    assert output_path.exists(), "Expected collapse artifact to be written"
    payload = json.loads(output_path.read_text(encoding="utf-8"))

    assert summary["scenario"] == "memory"
    assert summary["iterations"] == 2
    assert "driftScore" in payload
    assert "top_symbols" in payload
    assert payload["repairsInvoked"] >= payload["repairsSucceeded"]


def test_cli_main_accepts_custom_output(tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    """CLI main should succeed and write stdout + file artifacts."""

    output_path = tmp_path / "custom.json"
    exit_code = collapse_simulator_main(
        [
            "ethical",
            "--iterations",
            "1",
            "--noise",
            "0.02",
            "--output",
            str(output_path),
            "--seed",
            "123",
        ]
    )

    assert exit_code == 0
    assert output_path.exists()

    stdout = capsys.readouterr().out
    payload = json.loads(stdout)
    assert payload["scenario"] == "ethical"
    assert payload["iterations"] == 1
    assert payload["seed"] == 123


def test_compile_summary_tracks_repair_counts() -> None:
    """Ensure compile_summary mirrors SimulationContext counters."""

    context = SimulationContext(scenario="identity", iterations=3, noise=0.1, seed=7)
    context.repair_attempts = 3
    context.repair_successes = 2
    context.record_step(0.2, 0.05, "0001")
    context.record_step(0.21, 0.045, "0002")
    context.record_step(0.22, 0.04, "0003")

    summary = compile_summary(context, derive_top_symbols("identity"))
    assert summary["repairsInvoked"] == 3
    assert summary["repairsSucceeded"] == 2
    assert summary["collapseHash"] == "0003"


def test_default_output_path_points_to_codex_artifacts() -> None:
    """Guard default output path for compliance with Codex job spec."""

    assert str(DEFAULT_OUTPUT_PATH).startswith("codex_artifacts/")
