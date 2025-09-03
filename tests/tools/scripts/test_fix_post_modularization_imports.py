from pathlib import Path

from tools.scripts.fix_post_modularization_imports import fix_imports_in_file


def test_fix_imports_in_file(tmp_path: Path) -> None:
    sample = "from core.symbolic.glyphs import x\n"
    file_path = tmp_path / "sample.py"
    file_path.write_text(sample)

    assert fix_imports_in_file(file_path) is True
    expected = "from core.glyph.glyphs import x\n"
    assert file_path.read_text() == expected
