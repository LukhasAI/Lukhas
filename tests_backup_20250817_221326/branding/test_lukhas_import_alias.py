import importlib
import sys


def test_lukhas_import_alias_branding_module():
    sys.path.insert(0, "/Users/agi_dev/LOCAL-REPOS/Lukhas")
    alias_mod = importlib.import_module("lukhas.branding.terminology")
    real_mod = importlib.import_module("lukhas.branding.terminology")
    # Both paths should reference the same underlying module object
    assert alias_mod is real_mod
    # Behavior sanity
    assert hasattr(alias_mod, "normalize_output")
    out = alias_mod.normalize_output("Lukhas AGI uses quantum processing.")
    assert "Lukhas AI" in out and "quantum-inspired" in out
