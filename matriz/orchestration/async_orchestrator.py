"""Shim module exposing the async MATRIZ orchestrator via orchestration namespace."""

# ΛTAG: async_orchestrator_shim -- maintain canonical import pathway for async orchestrator
from matriz.core.async_orchestrator import AsyncCognitiveOrchestrator

__all__ = ["AsyncCognitiveOrchestrator"]
