"""Tests for import fixer stub generation helpers."""

from __future__ import annotations

from pathlib import Path

from tools.analysis import import_fixer as analysis_fixer
from tools.automation import import_fixer as automation_fixer


def test_analysis_stub_generation_has_no_todo_markers() -> None:
    content = analysis_fixer._generate_stub_module_content(Path("foo/bar.py"))
    assert "TODO" not in content
    assert "Auto-generated stub" in content
    assert "__getattr__" in content


def test_automation_stub_generation_matches_analysis_helper() -> None:
    analysis_stub = analysis_fixer._generate_stub_module_content(Path("foo/bar.py"))
    automation_stub = automation_fixer._generate_stub_module_content(Path("foo/bar.py"))

    for stub in (analysis_stub, automation_stub):
        assert "Auto-generated stub" in stub
        assert "logger.warning" in stub
        assert "__getattr__" in stub
        assert "TODO" not in stub
