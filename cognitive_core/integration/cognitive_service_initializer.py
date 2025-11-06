"""Compatibility shim for legacy cognitive_service_initializer import path."""

from __future__ import annotations

from .agi_service_initializer import (
    AGIServiceConfiguration,
    AGIServiceInitializer,
    cognitive_initializer,
    initialize_agi_system,
)

__all__ = [
    "AGIServiceConfiguration",
    "AGIServiceInitializer",
    "cognitive_initializer",
    "initialize_agi_system",
]
