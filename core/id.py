"""Bridge module for core.id → labs.core.id"""
from __future__ import annotations

from labs.core.id import IDGenerator, LambdaID, generate_lambda_id

__all__ = ["IDGenerator", "LambdaID", "generate_lambda_id"]
