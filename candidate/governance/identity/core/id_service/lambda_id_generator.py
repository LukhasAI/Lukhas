"""Canonical wrapper for Lambda ID generator.

Re-exports the existing implementation from the legacy `lambd_id_generator.py`
so code can import `lambda_id_generator` while the real implementation remains
in the legacy module. This is a temporary compatibility layer to enable a
safe migration to canonical names.
"""

from .lambd_id_generator import LambdaIDGenerator

__all__ = ["LambdaIDGenerator"]
