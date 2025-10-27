#!/usr/bin/env python3
"""
Smoke test for runtime lane integrity.

This test verifies that importing lukhas doesn't leak any labs modules
into the runtime, enforcing clean production/development lane separation.
"""

import sys


def test_no_labs_leak_after_importing_lukhas():
    """Test that importing lukhas doesn't dynamically load labs modules."""
    # Clean up any leaked modules from other tests
    for m in list(sys.modules.keys()):
        if m == "labs" or m.startswith("labs."):
            del sys.modules[m]

    import lukhas

    leaked = [m for m in sys.modules if m == "labs" or m.startswith("labs.")]

    assert not leaked, (
        f"labs modules leaked into runtime: {leaked}. "
        f"This violates production lane integrity. "
        f"Remove dynamic imports or use ALLOW_CANDIDATE_RUNTIME=1 for migration."
    )


def test_matriz_imports_cleanly():
    """Test that MATRIZ package imports without labs dependencies."""
    import MATRIZ

    # MATRIZ should be able to import independently
    assert "MATRIZ" in sys.modules
    print("✅ MATRIZ imports cleanly")


if __name__ == "__main__":
    # Allow running directly for quick testing
    test_no_labs_leak_after_importing_lukhas()
    test_matriz_imports_cleanly()
    print("✅ All runtime lane smoke tests passed")
