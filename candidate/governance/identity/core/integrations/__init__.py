"""
LUKHAS AGI Core System Integration

This module provides integration between the identity system and LUKHAS AGI
core systems including memory, consciousness, and inference engines.
"""

from .consciousness_bridge import ConsciousnessBridge, ConsciousnessSync
from .inference_adapter import (
    InferenceAdapter,
    InferenceRequest,
    InferenceResult,
)
from .memory_connector import MemoryConnector, MemoryIntegrationResult

__all__ = [
    "MemoryConnector",
    "MemoryIntegrationResult",
    "ConsciousnessBridge",
    "ConsciousnessSync",
    "InferenceAdapter",
    "InferenceRequest",
    "InferenceResult",
]
