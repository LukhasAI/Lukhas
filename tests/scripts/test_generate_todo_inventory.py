"""Tests for :mod:`scripts.todo_migration.generate_todo_inventory`."""

from scripts.todo_migration.generate_todo_inventory import scan_file


def test_scan_file_parses_metadata(tmp_path):
    """Scan a synthetic file and ensure metadata is parsed correctly."""
    source = """# TODO[priority:HIGH][owner:codex][scope:OPS]: rotate API key\nprint('done')\n"""

    path = tmp_path / "sample.py"
    path.write_text(source)

    todos = scan_file(path)

    assert todos == [
        {
            "file": str(path),
            "line": "1",
            "kind": "TODO",
            "priority": "HIGH",
            "owner": "codex",
            "scope": "OPS",
            "message": "rotate API key",
        }
    ]


def test_scan_file_elevates_security_todos(tmp_path):
    """Security-related TODOs should be surfaced with SECURITY scope and HIGH priority."""
    source = """# TODO: rotate password used in legacy integration tests\n"""

    path = tmp_path / "security.py"
    path.write_text(source)

    todos = scan_file(path)

    assert len(todos) == 1
    todo = todos[0]

    assert todo["scope"] == "SECURITY"
    assert todo["priority"] == "HIGH"
    assert "password" in todo["message"]
