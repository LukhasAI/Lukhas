"""LUKHAS entrypoints exposed for tests and tooling during pre-freeze."""
from __future__ import annotations

from collections.abc import Sequence

from bridge.api.main import app


def main(argv: Sequence[str] | None = None) -> int:
    """Lightweight CLI shim so collection can locate a callable main()."""
    _ = argv  # kept for signature parity; wired post-freeze
    print("LUKHAS main shim - pre-freeze")
    return 0


__all__ = ["app", "main"]
