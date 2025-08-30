"""
LUKHAS AI - Multi-AI Orchestration Engine
======================================

This module provides the crown jewel of LUKHAS AI integration:
the Multi-AI Orchestration Engine that seamlessly coordinates
OpenAI GPT, Anthropic Claude, Google Gemini, and Perplexity AI.

Copyright (c) 2025 LUKHAS AI. All rights reserved.
"""

try:
    from .multi_ai_orchestrator import MultiAIOrchestrator
except Exception:
    # Backward/forward compatibility: PR #76 exports ModelOrchestrator
    from .multi_ai_orchestrator import ModelOrchestrator as MultiAIOrchestrator

    ModelOrchestrator = MultiAIOrchestrator  # re-export
from .consensus_engine import ConsensusEngine
from .context_manager import ContextManager
from .performance_monitor import PerformanceMonitor

__all__ = [
    "ConsensusEngine",
    "ContextManager",
    "MultiAIOrchestrator",
    "PerformanceMonitor",
]
