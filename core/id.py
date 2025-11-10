"""Bridge module for core.id → labs.core.id"""
from __future__ import annotations

from labs.core.id import LambdaID, generate_lambda_id, IDGenerator

__all__ = ["LambdaID", "generate_lambda_id", "IDGenerator"]
