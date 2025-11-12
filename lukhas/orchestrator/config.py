"""
Orchestrator Configuration

Timeout and configuration management for cognitive pipeline orchestration.
"""

from dataclasses import dataclass


@dataclass
class TimeoutConfig:
    """Timeout configuration for orchestrator."""

    # Per-node execution timeout
    node_timeout_ms: int = 200  # 200ms per node (aggressive)

    # Per-pipeline execution timeout
    pipeline_timeout_ms: int = 500  # 500ms for entire pipeline

    # Grace period for cleanup after timeout
    cleanup_grace_ms: int = 100  # 100ms for cleanup

    # Whether to fail fast on timeout or try to continue
    fail_fast: bool = True

    @property
    def node_timeout_seconds(self) -> float:
        """Node timeout in seconds."""
        return self.node_timeout_ms / 1000.0

    @property
    def pipeline_timeout_seconds(self) -> float:
        """Pipeline timeout in seconds."""
        return self.pipeline_timeout_ms / 1000.0

    @property
    def cleanup_grace_seconds(self) -> float:
        """Cleanup grace period in seconds."""
        return self.cleanup_grace_ms / 1000.0


@dataclass
class OrchestratorConfig:
    """Complete orchestrator configuration."""

    timeouts: TimeoutConfig = None  # type: ignore[assignment]
    max_concurrent_pipelines: int = 10
    enable_distributed_tracing: bool = False
    enable_metrics: bool = True
    enable_cancellation: bool = True

    def __post_init__(self):
        """Initialize with default TimeoutConfig if not provided."""
        if self.timeouts is None:
            self.timeouts = TimeoutConfig()
