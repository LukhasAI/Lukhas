"""Serve API Schemas - Stub Implementation"""
from pydantic import BaseModel
from typing import Any, Dict, Optional

class RequestSchema(BaseModel):
    """Base request schema."""
    request_id: Optional[str] = None
    data: Dict[str, Any] = {}

class ResponseSchema(BaseModel):
    """Base response schema."""
    success: bool = True
    data: Dict[str, Any] = {}

__all__ = ["RequestSchema", "ResponseSchema"]
