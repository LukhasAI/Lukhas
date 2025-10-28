import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "scripts"
    / "todo_migration"
    / "generate_todo_inventory.py"
)
spec = importlib.util.spec_from_file_location("generate_todo_inventory", MODULE_PATH)
inventory = importlib.util.module_from_spec(spec)
assert spec and spec.loader  # help mypy/linters
spec.loader.exec_module(inventory)


def write_todo(tmp_path: Path, content: str) -> Path:
    file_path = tmp_path / "sample.py"
    file_path.write_text(content, encoding="utf-8")
    return file_path


def test_invalid_scope_defaults_to_unknown(tmp_path, capsys):
    todo = (
        "# TODO[scope:X][priority:HIGH] : Review mapping generation for safety\n"
    )
    file_path = write_todo(tmp_path, todo)

    entries = inventory.scan_file(file_path)

    assert entries[0]["scope"] == "UNKNOWN"
    captured = capsys.readouterr()
    assert "Invalid scope" in captured.err


def test_invalid_priority_defaults_to_medium(tmp_path, capsys):
    todo = "# TODO[scope:prod][priority:bananas] : Validate metadata\n"
    file_path = write_todo(tmp_path, todo)

    entries = inventory.scan_file(file_path)

    assert entries[0]["priority"] == "MEDIUM"
    captured = capsys.readouterr()
    assert "Invalid priority" in captured.err


def test_valid_metadata_preserved(tmp_path):
    todo = (
        "# TODO[scope:prod][priority:high][owner:@codex] : Ensure TODO parser handles metadata\n"
    )
    file_path = write_todo(tmp_path, todo)

    entries = inventory.scan_file(file_path)

    assert entries[0]["scope"] == "PROD"
    assert entries[0]["priority"] == "HIGH"
    assert entries[0]["owner"] == "@codex"
