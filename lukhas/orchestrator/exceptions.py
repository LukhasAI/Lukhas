"""
Orchestrator Exceptions

Exception hierarchy for timeout and cancellation handling.
"""


class OrchestratorException(Exception):
    """Base exception for orchestrator errors."""

    pass


class TimeoutException(OrchestratorException):
    """Base class for timeout-related exceptions."""

    pass


class NodeTimeoutException(TimeoutException):
    """Raised when a cognitive node exceeds its timeout."""

    def __init__(self, node_id: str, timeout_ms: int):
        self.node_id = node_id
        self.timeout_ms = timeout_ms
        super().__init__(f"Node '{node_id}' exceeded timeout of {timeout_ms}ms")


class PipelineTimeoutException(TimeoutException):
    """Raised when entire pipeline exceeds its timeout."""

    def __init__(self, pipeline_id: str, timeout_ms: int, completed_nodes: list[str]):
        self.pipeline_id = pipeline_id
        self.timeout_ms = timeout_ms
        self.completed_nodes = completed_nodes
        super().__init__(
            f"Pipeline '{pipeline_id}' exceeded timeout of {timeout_ms}ms "
            f"(completed {len(completed_nodes)} nodes)"
        )


class CancellationException(OrchestratorException):
    """Raised when pipeline is cancelled."""

    def __init__(self, pipeline_id: str, reason: str = "User requested"):
        self.pipeline_id = pipeline_id
        self.reason = reason
        super().__init__(f"Pipeline '{pipeline_id}' cancelled: {reason}")
