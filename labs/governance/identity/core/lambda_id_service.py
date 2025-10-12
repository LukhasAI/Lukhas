"""Canonical wrapper for Lambda ID service.

Re-exports the implementation from legacy `lambd_id_service.py` so code can
import `lambda_id_service` during migration.
"""

from .lambd_id_service import LambdaIDService

__all__ = ["LambdaIDService"]
