"""Guardian API - Stub Implementation"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

router = None


def validate_action(action):
    return {"valid": True, "guardian_score": 1.0}


__all__ = ["router", "validate_action"]
