"""Tests for branding.poetry.report_utils."""

import importlib.util
import sys
import types
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[4]
MODULE_PATH = ROOT / "branding" / "poetry" / "report_utils.py"

branding_pkg = sys.modules.setdefault("branding", types.ModuleType("branding"))
branding_pkg.__path__ = [str(ROOT / "branding")]
poetry_pkg = sys.modules.setdefault("branding.poetry", types.ModuleType("branding.poetry"))
poetry_pkg.__path__ = [str(ROOT / "branding" / "poetry")]

if "streamlit" not in sys.modules:
    sys.modules["streamlit"] = types.ModuleType("streamlit")

spec = importlib.util.spec_from_file_location("branding.poetry.report_utils", MODULE_PATH)
assert spec and spec.loader is not None
report_utils = importlib.util.module_from_spec(spec)
sys.modules["branding.poetry.report_utils"] = report_utils
spec.loader.exec_module(report_utils)

render_enrichment_summary = report_utils.render_enrichment_summary
render_frequency_line = report_utils.render_frequency_line


def test_render_frequency_line_includes_bar_and_label() -> None:
    """Frequency lines include counts, severity, and labels."""
    line = render_frequency_line("tapestry", 247, scale=10, bar_char="█", label="cliché")

    assert "tapestry" in line
    assert "247" in line
    assert "█" in line
    assert "cliché" in line
    assert "dominant" in line


def test_render_frequency_line_rejects_invalid_inputs() -> None:
    """Invalid parameters should raise a ValueError."""
    with pytest.raises(ValueError):
        render_frequency_line("fold", -1)

    with pytest.raises(ValueError):
        render_frequency_line("fold", 10, scale=0)


def test_render_enrichment_summary_reports_substitutions_and_usage() -> None:
    """Summaries surface substitutions and highlight overused metaphors."""
    usage = Counter({"tapestry": 3, "river": 1})

    summary = render_enrichment_summary(
        index=1,
        original="The consciousness is a tapestry of thoughts.",
        enriched="The consciousness is a fold-space of thoughts.",
        usage_counter=usage,
        highlight_limit=2,
        repetition_threshold=3,
    )

    assert "Example 1" in summary
    assert "Original" in summary
    assert "Enriched" in summary
    assert "tapestry→fold-space" in summary
    assert "ΛUsage: tapestry:3, river:1" in summary
    assert "Overused" in summary


def test_render_enrichment_summary_requires_positive_limit() -> None:
    """The highlight limit must be strictly positive."""
    with pytest.raises(ValueError):
        render_enrichment_summary(
            index=1,
            original="a",
            enriched="b",
            usage_counter={},
            highlight_limit=0,
            repetition_threshold=3,
        )
