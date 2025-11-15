"""Trace Routes - Stub Implementation"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import APIRouter

router = None


def get_traces():
    return [{"trace_id": "stub_trace", "duration_ms": 100}]


__all__ = ["router", "get_traces"]
