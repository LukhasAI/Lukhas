from pathlib import Path

import pytest

from tools.scripts import fix_syntax_errors as fse


def test_fix_eol_string_literal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "broken.py"
    target.write_text('{"content": "hello\n}')

    monkeypatch.setattr(
        fse,
        "find_syntax_error_line",
        lambda _: (1, "EOL while scanning string literal"),
    )

    fixed = fse.fix_eol_string_literal(target)

    assert fixed is True
    # ΛTAG: test_case
    assert target.read_text().splitlines()[0].endswith('"')
