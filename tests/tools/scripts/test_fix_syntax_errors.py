from tools.scripts.fix_syntax_errors import (
    find_syntax_error_line,
    fix_eol_string_literal,
)


def test_fix_eol_string_literal(tmp_path):
    """Repair unclosed string lines"""
    # ΛTAG: syntax_repair
    file_path = tmp_path / "broken.json"
    file_path.write_text('{"content": "hello\n}')

    assert find_syntax_error_line(file_path)
    assert fix_eol_string_literal(file_path)
    assert find_syntax_error_line(file_path) is None
    # TODO: expand coverage
