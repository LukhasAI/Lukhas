"""
LUKHAS Core MATRIZ Module

High-performance async orchestration engine for T4/0.01% performance targets.
Provides async pipeline processing with fail-soft behavior.
"""

from .async_orchestrator import AsyncOrchestrator, MockAsyncOrchestrator, PipelineResult
from .pipeline_stage import BaseStagePlugin, PipelineStage, StagePlugin, StageResult

__all__ = [
    "AsyncOrchestrator",
    "MockAsyncOrchestrator",
    "PipelineResult",
    "PipelineStage",
    "StageResult",
    "StagePlugin",
    "BaseStagePlugin",
]

__version__ = "1.0.0"
