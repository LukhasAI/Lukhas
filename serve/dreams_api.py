"""Dreams API - Stub Implementation"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

router = None


def generate_dream(params):
    return {"dream_id": "stub_dream_001", "success": True}


__all__ = ["router", "generate_dream"]
