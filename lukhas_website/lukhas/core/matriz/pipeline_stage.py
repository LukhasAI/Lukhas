#!/usr/bin/env python3
"""
MATRIZ Pipeline Stage

Individual processing stages for the async orchestration pipeline.
Supports critical/non-critical execution modes for fail-soft behavior.
"""

from dataclasses import dataclass
from typing import Any, Optional, Protocol


class StagePlugin(Protocol):
    """Protocol for stage plugins."""

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process input data and return output."""
        ...

    async def health_check(self) -> dict[str, Any]:
        """Optional health check method."""
        ...


@dataclass
class StageResult:
    """Result of stage execution."""
    success: bool
    output: Optional[dict[str, Any]]
    processing_time: float
    error: Optional[Exception] = None


@dataclass
class PipelineStage:
    """
    Individual pipeline stage configuration.

    Args:
        name: Unique stage identifier
        plugin: Processing plugin implementing StagePlugin protocol
        critical: Whether stage failure should abort entire pipeline
        timeout: Optional stage-specific timeout override
        retry_count: Number of retries on failure (default: 0)
        dependencies: List of stage names this stage depends on
    """
    name: str
    plugin: StagePlugin
    critical: bool = True
    timeout: Optional[float] = None
    retry_count: int = 0
    dependencies: Optional[list[str]] = None

    def __post_init__(self):
        """Validate stage configuration."""
        if not self.name:
            raise ValueError("Stage name cannot be empty")

        if not hasattr(self.plugin, 'process'):
            raise ValueError("Plugin must implement process method")

        if self.retry_count < 0:
            raise ValueError("Retry count cannot be negative")

        if self.dependencies is None:
            self.dependencies = []


class BaseStagePlugin:
    """Base implementation for stage plugins."""

    def __init__(self, name: str):
        self.name = name
        self.call_count = 0
        self.last_input = None
        self.last_output = None

    async def process(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Default process implementation."""
        self.call_count += 1
        self.last_input = input_data

        # Default: pass through input data
        output = {
            "processed_by": self.name,
            "stage_metadata": {
                "call_count": self.call_count,
                "plugin_name": self.name
            }
        }

        self.last_output = output
        return output

    async def health_check(self) -> dict[str, Any]:
        """Default health check implementation."""
        return {
            "plugin_name": self.name,
            "healthy": True,
            "call_count": self.call_count,
            "last_call_success": self.last_output is not None
        }
