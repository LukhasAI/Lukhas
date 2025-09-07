"""
LUKHAS AGI Registry Systems
==========================

This package contains registry implementations for managing various
components across the LUKHAS AGI system.
"""
import streamlit as st

from .intelligence_engine_registry import (
    EngineCapability,
    EngineInfo,
    EngineStatus,
    EngineType,
    HealthChecker,
    IntelligenceEngineRegistry,
    QueryFilter,
    RegistryConfig,
    RegistryEvent,
    create_capability,
    create_engine_info,
    get_global_registry,
)

__all__ = [
    # Enums
    "EngineType",
    "EngineStatus",
    "RegistryEvent",
    # Data classes
    "EngineCapability",
    "EngineInfo",
    "RegistryConfig",
    "QueryFilter",
    # Abstract base classes
    "HealthChecker",
    # Main registry class
    "IntelligenceEngineRegistry",
    # Factory functions
    "get_global_registry",
    "create_engine_info",
    "create_capability",
]
