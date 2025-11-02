"""Import-smoke for core.governance.identity.core.glyph.distributed_glyph_generation."""


def test_distributed_glyph_generation_imports():
    mod = __import__("core.governance.identity.core.glyph.distributed_glyph_generation", fromlist=["*"])
    assert mod is not None
