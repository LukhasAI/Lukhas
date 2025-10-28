from __future__ import annotations

from pathlib import Path

from TODO.scripts import categorize_todos


def _create_file(path: Path, contents: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8")


def test_load_exclusions_ignores_virtualenv_directories(tmp_path: Path) -> None:
    project_root = tmp_path
    (project_root / "pyproject.toml").write_text("", encoding="utf-8")

    _create_file(project_root / "module" / "alpha.py", "# TODO: implement guardian checks\n")
    _create_file(project_root / ".venv" / "ignore.py", "# TODO: this should not be indexed\n")

    todo_lines = categorize_todos.load_exclusions(project_root=project_root)

    assert len(todo_lines) == 1
    assert todo_lines[0].startswith("./module/alpha.py:1:")


def test_generate_priority_files_supports_custom_output(tmp_path: Path) -> None:
    output_base = tmp_path / "todo_output"
    categories = {
        "CRITICAL": [
            {
                "file": "./module/alpha.py",
                "line": "10",
                "text": "address security regression",
# See: https://github.com/LukhasAI/Lukhas/issues/627
            }
        ],
        "HIGH": [],
        "MED": [],
        "LOW": [],
    }

    generated = categorize_todos.generate_priority_files(categories, output_base=output_base)

    structured_path = output_base / "CRITICAL" / "critical_todos.md"
    legacy_path = output_base / "critical_todos.md"

    assert structured_path in generated
    assert legacy_path in generated

    content = structured_path.read_text(encoding="utf-8")
    assert "🚨" in content
    assert "🛡️ Guardian" in content
