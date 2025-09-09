from pathlib import Path

from tools.scripts.fix_post_modularization_imports import fix_imports_in_file


def test_fix_imports_in_file(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text("import memory.glyph_memory_integration\n")

    changed = fix_imports_in_file(sample)

    assert changed is True
    # ΛTAG: test_case
    assert "core.glyph.glyph_memory_integration" in sample.read_text()