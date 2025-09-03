from pathlib import Path

from tools.scripts.fix_post_modularization_imports import fix_imports_in_file


def test_fix_imports_in_file(tmp_path: Path) -> None:
    """Ensure import mappings apply correctly."""
    sample = tmp_path / "sample.py"
    sample.write_text("from memory.glyph_memory_integration import Foo\n")

    assert fix_imports_in_file(sample)
    content = sample.read_text()
    # ΛTAG: import_mapping_test
    assert "from core.glyph.glyph_memory_integration import Foo" in content
