"""Compatibility shim exposing AGI service bridge under legacy cognitive_service_bridge name."""

from __future__ import annotations

from .agi_service_bridge import (
    AGIServiceAdapter,
    AGIServiceBridge,
    ServiceMetrics,
    ServiceRegistration,
    cognitive_service_bridge,
    get_agi_service,
    health_check_agi_services,
    initialize_agi_services,
    register_agi_service,
)

__all__ = [
    "AGIServiceAdapter",
    "AGIServiceBridge",
    "ServiceMetrics",
    "ServiceRegistration",
    "cognitive_service_bridge",
    "get_agi_service",
    "health_check_agi_services",
    "initialize_agi_services",
    "register_agi_service",
]
