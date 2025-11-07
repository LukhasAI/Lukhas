from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from tools.todo_categorize import (
    TODORecord,
    extract_todo_context,
    scan_repo,
)


def test_extract_todo_context():
    """Verify that extract_todo_context correctly parses a TODO line."""
    line = "path/to/file.py:123: TODO: This is a test"
    file, line_num, text = extract_todo_context(line)
    assert file == "path/to/file.py"
    assert line_num == "123"
    assert text == "This is a test"


def test_scan_repo():
    """Verify that scan_repo correctly finds TODOs in a directory."""
    with TemporaryDirectory() as tempdir:
        root = Path(tempdir)
        (root / "file1.py").write_text("# TODO: This is a test in file 1")
        (root / "file2.txt").write_text("FIXME: This is a test in file 2")
        (root / "file3.md").write_text("# BUG: This is a test in file 3")
        (root / "file4.py").write_text("# Not a todo")
        (root / "skip.pyc").write_text("# TODO: This should be skipped")

        items = scan_repo(root)
        assert len(items) == 3

        assert items[0] == TODORecord(
            file="file1.py",
            line="1",
            text="This is a test in file 1",
            priority="MED",
        )
        assert items[1] == TODORecord(
            file="file2.txt",
            line="1",
            text="This is a test in file 2",
            priority="MED",
        )
        assert items[2] == TODORecord(
            file="file3.md",
            line="1",
            text="This is a test in file 3",
            priority="MED",
        )
