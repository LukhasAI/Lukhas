"""
Golden Trio Orchestration Module

Unified orchestration for DAST, ABAS, and NIAS systems.
"""

from .trio_orchestrator import (
    TrioOrchestrator,
    SharedContextManager,
    SystemType,
    MessagePriority,
    ProcessingMode,
    TrioMessage,
    TrioResponse,
    get_trio_orchestrator
)

__all__ = [
    "TrioOrchestrator",
    "SharedContextManager",
    "SystemType",
    "MessagePriority",
    "ProcessingMode",
    "TrioMessage",
    "TrioResponse",
    "get_trio_orchestrator"
]

__version__ = "1.0.0"