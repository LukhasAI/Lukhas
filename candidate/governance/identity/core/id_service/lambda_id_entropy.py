"""Canonical wrapper for Lambda ID entropy calculator.

Re-exports implementation from `lambd_id_entropy.py` to support canonical imports.
"""

from .lambd_id_entropy import LambdaIDEntropy

# Provide the legacy and canonical export names so callers using either
# symbol or module path continue to work during migration.
EntropyCalculator = LambdaIDEntropy

__all__ = ["EntropyCalculator", "LambdaIDEntropy"]
