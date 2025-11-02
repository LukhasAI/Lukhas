"""Compatibility shim for legacy imports: `consciousness.matriz_thought_loop`.

Provides minimal symbols expected by bridge and soak tests. This module is a
thin facade that should be replaced by direct usage of the canonical MATRIZ
entrypoints. All call paths raise a clear error until wired to real
implementations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class _NotWiredError(RuntimeError):
    pass


@dataclass
class MATRIZProcessingContext:
    """Placeholder processing context for legacy tests.

    Replace usage with canonical MATRIZ processing context.
    """

    params: dict[str, Any] | None = None


class MATRIZThoughtLoop:
    """Placeholder thought loop entrypoint.

    Methods raise informative errors until the real backend is wired.
    """

    def __init__(self, context: MATRIZProcessingContext | None = None) -> None:
        self.context = context or MATRIZProcessingContext()

    def run(self, *args: Any, **kwargs: Any) -> Any:
        raise _NotWiredError("MATRIZThoughtLoop shim invoked. Wire to canonical MATRIZ runtime or update tests.")


# Backwards-compatible aliases often referenced by tests
matrizProcessingContext = MATRIZProcessingContext
matrizThoughtLoop = MATRIZThoughtLoop

__all__ = [
    "MATRIZProcessingContext",
    "MATRIZThoughtLoop",
    "matrizProcessingContext",
    "matrizThoughtLoop",
]
