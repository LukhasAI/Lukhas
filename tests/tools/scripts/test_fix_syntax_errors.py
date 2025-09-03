import ast
from pathlib import Path

from tools.scripts.fix_syntax_errors import fix_eol_string_literal


def test_fix_eol_string_literal(tmp_path: Path) -> None:
    """Patch EOL string literal and ensure syntax validity."""
    target = tmp_path / "broken.py"
    target.write_text('{"content": "Hello\n}\n')

    assert fix_eol_string_literal(target)
    ast.parse(target.read_text())
    # ΛTAG: eol_fix_test
    assert '"Hello"' in target.read_text()
