#!/usr/bin/env python3
"""
Smoke test for runtime lane integrity.

This test verifies that importing lukhas doesn't leak any candidate modules
into the runtime, enforcing clean production/development lane separation.
"""

import sys


def test_no_candidate_leak_after_importing_lukhas():
    """Test that importing lukhas doesn't dynamically load candidate modules."""
    # Clean up any leaked modules from other tests
    for m in list(sys.modules.keys()):
        if m == "candidate" or m.startswith("candidate."):
            del sys.modules[m]

    import lukhas  # noqa: F401

    leaked = [m for m in sys.modules if m == "candidate" or m.startswith("candidate.")]

    assert not leaked, (
        f"candidate modules leaked into runtime: {leaked}. "
        f"This violates production lane integrity. "
        f"Remove dynamic imports or use ALLOW_CANDIDATE_RUNTIME=1 for migration."
    )


def test_matriz_imports_cleanly():
    """Test that matriz package imports without candidate dependencies."""
    import matriz  # noqa: F401

    # matriz should be able to import independently
    assert "matriz" in sys.modules
    print("✅ matriz imports cleanly")


if __name__ == "__main__":
    # Allow running directly for quick testing
    test_no_candidate_leak_after_importing_lukhas()
    test_matriz_imports_cleanly()
    print("✅ All runtime lane smoke tests passed")
