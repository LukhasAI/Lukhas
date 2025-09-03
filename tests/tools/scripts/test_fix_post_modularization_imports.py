from pathlib import Path

from tools.scripts.fix_post_modularization_imports import fix_imports_in_file


def test_fix_imports_in_file(tmp_path):
    """Ensure import mappings apply correctly"""
    # ΛTAG: import_mapping_test
    file_path = tmp_path / "sample.py"
    file_path.write_text("from memory.glyph_memory_integration import foo\n")

    changed = fix_imports_in_file(file_path)

    assert changed
    assert "core.glyph.glyph_memory_integration" in file_path.read_text()
    # TODO: expand coverage
