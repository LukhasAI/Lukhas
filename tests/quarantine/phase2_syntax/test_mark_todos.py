from __future__ import annotations

from pathlib import Path

import pytest
from quarantine.phase2_syntax.ci import mark_todos


def test_annotate_file_inserts_suggestion(tmp_path: Path) -> None:
    target_file = tmp_path / "sample.py"
    target_file.write_text("# TODO[T4-AUTOFIX]: use list comprehension\nvalue = 1\n", encoding="utf-8")

    todos = mark_todos.find_todo_markers(str(target_file))
    assert todos, "Expected TODO marker to be detected"

    modifications = mark_todos.annotate_file(str(target_file), todos, dry_run=False)
    assert modifications == 1

    updated_lines = target_file.read_text(encoding="utf-8").splitlines()
    assert "# T4-SUGGESTION:" in updated_lines[1]
    assert "Replace loop" in updated_lines[1]


def test_generate_todo_report_uses_utc_timestamp(monkeypatch: pytest.MonkeyPatch) -> None:
    class FixedDatetime(mark_todos.datetime):
        @classmethod
        def now(cls, tz=None):  # type: ignore[override]
            return cls(2024, 1, 2, 3, 4, 5, tzinfo=tz)

    monkeypatch.setattr(mark_todos, "datetime", FixedDatetime)

    sample_todos = [
        {
            "file": f"path/file_{idx}.py",
            "line": idx + 1,
            "type": "AUTOFIX",
            "message": "use list comprehension",
            "full_line": "# TODO[T4-AUTOFIX]: use list comprehension",
            "context": "global",
        }
        for idx in range(12)
    ]

    report = mark_todos.generate_todo_report(sample_todos)

    assert "Generated: 2024-01-02T03:04:05Z" in report
    assert "- ... and 2 more" in report
