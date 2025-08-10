import importlib
import sys


def test_lukhas_import_alias_branding_module():
    sys.path.insert(0, "/Users/agi_dev/LOCAL-REPOS/Lukhas_PWM")
    mod = importlib.import_module("lukhas.branding.terminology")
    assert hasattr(mod, "normalize_output")
    # Ensure the module actually came from lukhas_pwm
    assert mod.__name__ == "lukhas.branding.terminology"
    # Behavior sanity
    out = mod.normalize_output("Lukhas AGI uses quantum processing.")
    assert "Lukhas AI" in out and "quantum-inspired" in out
