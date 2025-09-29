"""
LUKHAS Core MATRIZ Module

High-performance async orchestration engine for T4/0.01% performance targets.
Provides async pipeline processing with fail-soft behavior.
"""

from .async_orchestrator import AsyncOrchestrator, PipelineResult, MockAsyncOrchestrator
from .pipeline_stage import PipelineStage, StageResult, StagePlugin, BaseStagePlugin

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