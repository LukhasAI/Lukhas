from pathlib import Path

from tools.scripts.fix_syntax_errors import (
    find_syntax_error_line,
    fix_eol_string_literal,
)


def test_fix_eol_string_literal(tmp_path: Path) -> None:
    file_path = tmp_path / "bad.py"
    file_path.write_text('data = {\n    "content": "hello\n}\n')

    assert find_syntax_error_line(file_path) is not None
    assert fix_eol_string_literal(file_path) is True
    assert find_syntax_error_line(file_path) is None
