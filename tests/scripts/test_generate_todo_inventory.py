from pathlib import Path

from scripts.todo_migration.generate_todo_inventory import scan_file


def write_file(tmp_path: Path, name: str, content: str) -> Path:
    file_path = tmp_path / name
    file_path.write_text(content)
    return file_path


def test_python_docstring_not_detected_as_todo(tmp_path):
    python_file = write_file(
        tmp_path,
        "example.py",
        '"""Example docstring containing # TODO: sample message."""\n',
    )

    todos = scan_file(python_file)

    assert todos == []


def test_python_inline_comment_detected(tmp_path):
    python_file = write_file(
        tmp_path,
        "inline.py",
        """
def compute():
    return 1  # TODO[owner:alice][priority:low]: adjust computation
""",
    )

    todos = scan_file(python_file)

    assert len(todos) == 1
    todo = todos[0]
    assert todo["file"] == str(python_file)
    assert todo["line"] == "3"
    assert todo["owner"] == "alice"
    assert todo["priority"] == "LOW"
    assert todo["message"] == "adjust computation"
