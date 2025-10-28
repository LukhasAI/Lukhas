from __future__ import annotations

import importlib.util
import sys
from datetime import datetime
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def _load_module(module_name: str, file_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader  # for type checking
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


categorize = _load_module("categorize_todos", REPO_ROOT / "TODO" / "scripts" / "categorize_todos.py")
weekly_hygiene = _load_module("weekly_hygiene", REPO_ROOT / "tools" / "reports" / "weekly_hygiene.py")


def test_extract_todo_context_normalizes_path() -> None:
    file_path, line, text = categorize.extract_todo_context(
        "./tools/example.py:42:    # TODO: tighten validation logic"
    )
    assert file_path == "tools/example.py"
    assert line == "42"
    assert text == "tighten validation logic"


def test_categorize_todos_prioritizes_keywords() -> None:
    sample_lines = [
# See: https://github.com/LukhasAI/Lukhas/issues/628
        "tools/helpers.py:5:# TODO: add docstring for helper",
    ]

    categories = categorize.categorize_todos(todo_lines=sample_lines)

    critical_entries = categories["CRITICAL"]
    low_entries = categories["LOW"]

    assert len(critical_entries) == 1
    assert critical_entries[0].file == "candidate/security/auth.py"
    assert critical_entries[0].priority == "CRITICAL"

    assert len(low_entries) == 1
    assert low_entries[0].file == "tools/helpers.py"
    assert low_entries[0].priority == "LOW"


def test_generate_priority_files_creates_markdown(tmp_path: Path) -> None:
    record = categorize.TODORecord(
        file="candidate/core/module.py",
        line="12",
        text="Implement identity verification for guardian compliance",
        priority="HIGH",
# See: https://github.com/LukhasAI/Lukhas/issues/629
    )

    categories = {"CRITICAL": [], "HIGH": [record], "MED": [], "LOW": []}

    generated = categorize.generate_priority_files(
        categories,
        repo_path=tmp_path,
        updated_at=datetime(2024, 1, 1),
    )

    high_path = generated["HIGH"]
    output = high_path.read_text(encoding="utf-8")

    assert "January 01, 2024" in output
    assert "candidate/core/module.py:12" in output
    assert "⚛️ Identity" in output


def test_weekly_hygiene_todo_count_handles_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert weekly_hygiene.todo_count(tmp_path) == 0


def test_weekly_hygiene_spark_scaling() -> None:
    assert weekly_hygiene.spark(0) == ""
    assert weekly_hygiene.spark(5) == "▂▂▂▂▂"
    assert weekly_hygiene.spark(50) == "█" * 20
