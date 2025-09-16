# ΛTASK_ID: 0
# ΛCOMMIT_WINDOW: modular-audit
# ΛPROVED_BY: GRDM
# ΛUDIT: Added demo main


from .glyph_redactor_engine import GlyphRedactorEngine


def demo():
    GlyphRedactorEngine(
access_context={"level": "G0_PUBLIC_UTILITY"},
glyph_metadata_provider=None,
)
sample = "Hello ΛAIG"  # Example text with glyph
print(engine.redact_stream(sample))


if __name__ == "__main__":
    demo()
