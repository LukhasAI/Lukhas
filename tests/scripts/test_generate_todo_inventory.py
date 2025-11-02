"""Regression tests for the TODO inventory generator CLI."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

from scripts.todo_migration.generate_todo_inventory import scan_file

SCRIPT_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "todo_migration"
    / "generate_todo_inventory.py"
)


def run_generator(tmp_path: Path, max_files: int | None = None) -> list[dict[str, str]]:
    (tmp_path / "one.py").write_text("# TODO: first\n", encoding="utf-8")
    (tmp_path / "two.py").write_text("# TODO: second\n", encoding="utf-8")

    output_path = tmp_path / "todos.csv"
    cmd = [
        sys.executable,
        str(SCRIPT_PATH),
        "--root",
        str(tmp_path),
        "--output",
        str(output_path),
    ]
    if max_files is not None:
        cmd.extend(["--max-files", str(max_files)])

    subprocess.run(cmd, check=True, capture_output=True, text=True)

    with output_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def write_file(tmp_path: Path, name: str, content: str) -> Path:
    file_path = tmp_path / name
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_max_files_limits_results(tmp_path: Path) -> None:
    rows = run_generator(tmp_path, max_files=1)
    assert len(rows) == 1
    assert rows[0]["message"] == "first"


def test_without_limit_scans_all_files(tmp_path: Path) -> None:
    rows = run_generator(tmp_path)
    assert len(rows) == 2
    messages = {row["message"] for row in rows}
    assert messages == {"first", "second"}


def test_python_docstring_not_detected_as_todo(tmp_path: Path) -> None:
    python_file = write_file(
        tmp_path,
        "example.py",
        '"""Example docstring containing # TODO: sample message."""\n',
    )

    todos = scan_file(python_file)

    assert todos == []


def test_python_inline_comment_detected(tmp_path: Path) -> None:
    python_file = write_file(
        tmp_path,
        "inline.py",
        "def compute():\n"
        "    return 1  # TODO[owner:alice][priority:low]: adjust computation\n",
    )

    todos = scan_file(python_file)

    assert len(todos) == 1
    todo = todos[0]
    assert todo["file"] == str(python_file)
    assert todo["line"] == "2"
    assert todo["owner"] == "alice"
    assert todo["priority"] == "LOW"
    assert todo["message"] == "adjust computation"


def test_python_docstring_todo_detected(tmp_path: Path) -> None:
    python_file = write_file(
        tmp_path,
        "docstring_todo.py",
        "def placeholder():\n"
        '    """TODO[owner:bob][priority:high]: implement placeholder"""\n'
        "    return None\n",
    )

    todos = scan_file(python_file)

    assert len(todos) == 1
    todo = todos[0]
    assert todo["file"] == str(python_file)
    assert todo["line"] == "2"
    assert todo["owner"] == "bob"
    assert todo["priority"] == "HIGH"
    assert todo["message"] == "implement placeholder"
