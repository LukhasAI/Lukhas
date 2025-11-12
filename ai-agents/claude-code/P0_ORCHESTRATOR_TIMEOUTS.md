# Claude Code Task: Complete Async Orchestrator Timeouts (MP001)

**Task ID**: MP001
**Priority**: P0 (Critical)
**Effort**: Medium (4-16 hours)
**Owner**: claude-code
**Branch**: `feat/orchestrator-timeouts`

---

## Objective

Complete the **async orchestrator timeout implementation** to prevent hung pipelines, enforce SLA boundaries, and enable graceful cancellation with proper resource cleanup.

---

## Context

Current state:
- Orchestrator has basic async/await structure
- NO timeout enforcement on pipeline execution
- NO timeout enforcement on individual node execution
- Hung nodes can block pipelines indefinitely
- No cancellation support

**Problem**: A single slow/hung cognitive node can block entire pipeline, violating <250ms p95 SLA.

**Solution**: Comprehensive timeout system with:
1. Per-node timeouts (default: 200ms)
2. Per-pipeline timeouts (default: 500ms)
3. Graceful cancellation with cleanup
4. Timeout metrics and logging

---

## Implementation Requirements

### 1. Timeout Configuration

**File**: `lukhas/orchestrator/config.py`

```python
from dataclasses import dataclass
from typing import Optional


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

    timeouts: TimeoutConfig = TimeoutConfig()
    max_concurrent_pipelines: int = 10
    enable_distributed_tracing: bool = False

    # ... existing config fields ...
```

### 2. Timeout Exception Hierarchy

**File**: `lukhas/orchestrator/exceptions.py`

```python
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
        super().__init__(
            f"Node '{node_id}' exceeded timeout of {timeout_ms}ms"
        )


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
        super().__init__(
            f"Pipeline '{pipeline_id}' cancelled: {reason}"
        )
```

### 3. Node Execution with Timeout

**File**: `lukhas/orchestrator/executor.py`

```python
import asyncio
import logging
from typing import Any, Optional
from contextlib import asynccontextmanager

from .config import TimeoutConfig
from .exceptions import NodeTimeoutException, CancellationException

logger = logging.getLogger(__name__)


class NodeExecutor:
    """Executes cognitive nodes with timeout enforcement."""

    def __init__(self, config: TimeoutConfig):
        self.config = config

    async def execute_node(
        self,
        node_id: str,
        node_func: callable,
        input_data: Any,
        cancellation_token: Optional[asyncio.Event] = None
    ) -> Any:
        """
        Execute a cognitive node with timeout enforcement.

        Args:
            node_id: Unique identifier for the node
            node_func: Async function to execute
            input_data: Input data for the node
            cancellation_token: Optional event to check for cancellation

        Returns:
            Node execution result

        Raises:
            NodeTimeoutException: If node exceeds timeout
            CancellationException: If cancelled via token
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # Create task for node execution
            task = asyncio.create_task(node_func(input_data))

            # Wait with timeout
            result = await asyncio.wait_for(
                self._execute_with_cancellation(task, cancellation_token),
                timeout=self.config.node_timeout_seconds
            )

            # Record success metric
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_node_success(node_id, elapsed_ms)

            return result

        except asyncio.TimeoutError:
            # Cancel the task
            task.cancel()

            # Wait briefly for cleanup
            try:
                await asyncio.wait_for(
                    task,
                    timeout=self.config.cleanup_grace_seconds
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.warning(f"Node {node_id} did not cleanup gracefully")

            # Record timeout metric
            self._record_node_timeout(node_id)

            # Raise timeout exception
            raise NodeTimeoutException(node_id, self.config.node_timeout_ms)

        except CancellationException:
            # Propagate cancellation
            task.cancel()
            raise

        except Exception as e:
            # Record error metric
            elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
            self._record_node_error(node_id, elapsed_ms, type(e).__name__)
            raise

    async def _execute_with_cancellation(
        self,
        task: asyncio.Task,
        cancellation_token: Optional[asyncio.Event]
    ) -> Any:
        """Execute task while checking cancellation token."""
        if not cancellation_token:
            return await task

        # Wait for either task completion or cancellation
        cancel_task = asyncio.create_task(cancellation_token.wait())

        done, pending = await asyncio.wait(
            [task, cancel_task],
            return_when=asyncio.FIRST_COMPLETED
        )

        # Cancel pending tasks
        for p in pending:
            p.cancel()

        # Check if cancelled
        if cancel_task in done:
            raise CancellationException("unknown", "Cancellation token set")

        # Return task result
        return task.result()

    def _record_node_success(self, node_id: str, elapsed_ms: float) -> None:
        """Record successful node execution."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_node_duration_ms",
                elapsed_ms,
                tags={"node_id": node_id, "status": "success"}
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "success"}
            )
        except Exception as e:
            logger.warning(f"Failed to record node success metric: {e}")

    def _record_node_timeout(self, node_id: str) -> None:
        """Record node timeout."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.increment(
                "orchestrator_node_timeouts_total",
                tags={"node_id": node_id}
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "timeout"}
            )
        except Exception as e:
            logger.warning(f"Failed to record node timeout metric: {e}")

    def _record_node_error(
        self,
        node_id: str,
        elapsed_ms: float,
        error_type: str
    ) -> None:
        """Record node error."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_node_duration_ms",
                elapsed_ms,
                tags={"node_id": node_id, "status": "error"}
            )
            metrics.increment(
                "orchestrator_node_executions_total",
                tags={"node_id": node_id, "status": "error", "error_type": error_type}
            )
        except Exception as e:
            logger.warning(f"Failed to record node error metric: {e}")
```

### 4. Pipeline Execution with Timeout

**File**: `lukhas/orchestrator/pipeline.py`

```python
import asyncio
import logging
from typing import Any, List, Optional
from dataclasses import dataclass

from .config import OrchestratorConfig
from .executor import NodeExecutor
from .exceptions import PipelineTimeoutException, CancellationException

logger = logging.getLogger(__name__)


@dataclass
class PipelineContext:
    """Context for pipeline execution."""
    pipeline_id: str
    nodes: List[str]
    cancellation_token: asyncio.Event
    start_time: float
    completed_nodes: List[str]


class PipelineExecutor:
    """Executes multi-node pipelines with timeout enforcement."""

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.node_executor = NodeExecutor(config.timeouts)

    async def execute_pipeline(
        self,
        pipeline_id: str,
        nodes: List[tuple[str, callable]],
        initial_input: Any
    ) -> Any:
        """
        Execute a pipeline of cognitive nodes with timeout enforcement.

        Args:
            pipeline_id: Unique identifier for pipeline
            nodes: List of (node_id, node_func) tuples
            initial_input: Initial input data

        Returns:
            Final pipeline output

        Raises:
            PipelineTimeoutException: If pipeline exceeds timeout
            NodeTimeoutException: If a node exceeds its timeout
            CancellationException: If pipeline is cancelled
        """
        # Create pipeline context
        context = PipelineContext(
            pipeline_id=pipeline_id,
            nodes=[node_id for node_id, _ in nodes],
            cancellation_token=asyncio.Event(),
            start_time=asyncio.get_event_loop().time(),
            completed_nodes=[]
        )

        try:
            # Execute pipeline with timeout
            result = await asyncio.wait_for(
                self._execute_nodes(context, nodes, initial_input),
                timeout=self.config.timeouts.pipeline_timeout_seconds
            )

            # Record success metric
            elapsed_ms = (asyncio.get_event_loop().time() - context.start_time) * 1000
            self._record_pipeline_success(pipeline_id, len(nodes), elapsed_ms)

            return result

        except asyncio.TimeoutError:
            # Set cancellation token
            context.cancellation_token.set()

            # Record timeout metric
            self._record_pipeline_timeout(pipeline_id, len(context.completed_nodes))

            raise PipelineTimeoutException(
                pipeline_id,
                self.config.timeouts.pipeline_timeout_ms,
                context.completed_nodes
            )

        except (NodeTimeoutException, CancellationException):
            # Propagate node timeout or cancellation
            context.cancellation_token.set()
            raise

        except Exception as e:
            # Record error metric
            elapsed_ms = (asyncio.get_event_loop().time() - context.start_time) * 1000
            self._record_pipeline_error(
                pipeline_id,
                len(context.completed_nodes),
                elapsed_ms,
                type(e).__name__
            )
            raise

    async def _execute_nodes(
        self,
        context: PipelineContext,
        nodes: List[tuple[str, callable]],
        initial_input: Any
    ) -> Any:
        """Execute pipeline nodes sequentially."""
        current_input = initial_input

        for node_id, node_func in nodes:
            logger.debug(f"Executing node {node_id} in pipeline {context.pipeline_id}")

            # Execute node with timeout
            current_input = await self.node_executor.execute_node(
                node_id=node_id,
                node_func=node_func,
                input_data=current_input,
                cancellation_token=context.cancellation_token
            )

            # Mark node completed
            context.completed_nodes.append(node_id)

            logger.debug(
                f"Node {node_id} completed "
                f"({len(context.completed_nodes)}/{len(context.nodes)})"
            )

        return current_input

    def _record_pipeline_success(
        self,
        pipeline_id: str,
        node_count: int,
        elapsed_ms: float
    ) -> None:
        """Record successful pipeline execution."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_pipeline_duration_ms",
                elapsed_ms,
                tags={"pipeline_id": pipeline_id, "status": "success"}
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={"pipeline_id": pipeline_id, "status": "success"}
            )
            metrics.histogram(
                "orchestrator_pipeline_node_count",
                node_count,
                tags={"pipeline_id": pipeline_id}
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline success metric: {e}")

    def _record_pipeline_timeout(
        self,
        pipeline_id: str,
        completed_nodes: int
    ) -> None:
        """Record pipeline timeout."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.increment(
                "orchestrator_pipeline_timeouts_total",
                tags={"pipeline_id": pipeline_id}
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={"pipeline_id": pipeline_id, "status": "timeout"}
            )
            metrics.gauge(
                "orchestrator_pipeline_completed_nodes_at_timeout",
                completed_nodes,
                tags={"pipeline_id": pipeline_id}
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline timeout metric: {e}")

    def _record_pipeline_error(
        self,
        pipeline_id: str,
        completed_nodes: int,
        elapsed_ms: float,
        error_type: str
    ) -> None:
        """Record pipeline error."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.histogram(
                "orchestrator_pipeline_duration_ms",
                elapsed_ms,
                tags={"pipeline_id": pipeline_id, "status": "error"}
            )
            metrics.increment(
                "orchestrator_pipeline_executions_total",
                tags={
                    "pipeline_id": pipeline_id,
                    "status": "error",
                    "error_type": error_type
                }
            )
        except Exception as e:
            logger.warning(f"Failed to record pipeline error metric: {e}")
```

### 5. Cancellation Support

**File**: `lukhas/orchestrator/cancellation.py`

```python
import asyncio
from typing import Dict
from datetime import datetime


class CancellationRegistry:
    """Registry for pipeline cancellation tokens."""

    def __init__(self):
        self._tokens: Dict[str, asyncio.Event] = {}
        self._metadata: Dict[str, dict] = {}

    def register(self, pipeline_id: str) -> asyncio.Event:
        """Register a new pipeline and return its cancellation token."""
        token = asyncio.Event()
        self._tokens[pipeline_id] = token
        self._metadata[pipeline_id] = {
            "created_at": datetime.utcnow(),
            "cancelled": False
        }
        return token

    def cancel(self, pipeline_id: str, reason: str = "User requested") -> bool:
        """Cancel a pipeline by ID."""
        if pipeline_id not in self._tokens:
            return False

        token = self._tokens[pipeline_id]
        token.set()

        self._metadata[pipeline_id]["cancelled"] = True
        self._metadata[pipeline_id]["cancelled_at"] = datetime.utcnow()
        self._metadata[pipeline_id]["reason"] = reason

        return True

    def unregister(self, pipeline_id: str) -> None:
        """Unregister a completed pipeline."""
        self._tokens.pop(pipeline_id, None)
        self._metadata.pop(pipeline_id, None)

    def is_cancelled(self, pipeline_id: str) -> bool:
        """Check if pipeline is cancelled."""
        if pipeline_id not in self._tokens:
            return False
        return self._tokens[pipeline_id].is_set()

    def get_metadata(self, pipeline_id: str) -> dict:
        """Get pipeline metadata."""
        return self._metadata.get(pipeline_id, {})
```

---

## Testing Requirements

### 1. Unit Tests

**File**: `tests/unit/orchestrator/test_timeouts.py`

```python
import pytest
import asyncio
from lukhas.orchestrator.config import TimeoutConfig
from lukhas.orchestrator.executor import NodeExecutor
from lukhas.orchestrator.exceptions import NodeTimeoutException


@pytest.fixture
def timeout_config():
    """Timeout config with very short timeouts for testing."""
    return TimeoutConfig(
        node_timeout_ms=100,  # 100ms
        pipeline_timeout_ms=300,  # 300ms
        cleanup_grace_ms=50  # 50ms
    )


@pytest.mark.asyncio
async def test_node_timeout_raises_exception(timeout_config):
    """Test that slow node raises NodeTimeoutException."""
    executor = NodeExecutor(timeout_config)

    async def slow_node(input_data):
        await asyncio.sleep(1.0)  # 1 second - exceeds 100ms timeout
        return "never reached"

    with pytest.raises(NodeTimeoutException) as exc_info:
        await executor.execute_node("slow_node", slow_node, {})

    assert exc_info.value.node_id == "slow_node"
    assert exc_info.value.timeout_ms == 100


@pytest.mark.asyncio
async def test_fast_node_succeeds(timeout_config):
    """Test that fast node completes successfully."""
    executor = NodeExecutor(timeout_config)

    async def fast_node(input_data):
        await asyncio.sleep(0.01)  # 10ms - well under timeout
        return "success"

    result = await executor.execute_node("fast_node", fast_node, {})

    assert result == "success"


@pytest.mark.asyncio
async def test_node_cancellation_via_token(timeout_config):
    """Test node cancellation via cancellation token."""
    executor = NodeExecutor(timeout_config)
    cancellation_token = asyncio.Event()

    async def long_node(input_data):
        await asyncio.sleep(10.0)  # Very long
        return "never reached"

    # Start node execution
    task = asyncio.create_task(
        executor.execute_node("long_node", long_node, {}, cancellation_token)
    )

    # Cancel after 50ms
    await asyncio.sleep(0.05)
    cancellation_token.set()

    # Should raise CancellationException
    with pytest.raises(CancellationException):
        await task


@pytest.mark.asyncio
async def test_pipeline_timeout(timeout_config):
    """Test pipeline timeout when nodes take too long collectively."""
    from lukhas.orchestrator.config import OrchestratorConfig
    from lukhas.orchestrator.pipeline import PipelineExecutor
    from lukhas.orchestrator.exceptions import PipelineTimeoutException

    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config)

    async def medium_node(input_data):
        await asyncio.sleep(0.15)  # 150ms each
        return input_data

    # 3 nodes × 150ms = 450ms total > 300ms pipeline timeout
    nodes = [
        ("node1", medium_node),
        ("node2", medium_node),
        ("node3", medium_node),
    ]

    with pytest.raises(PipelineTimeoutException) as exc_info:
        await executor.execute_pipeline("test_pipeline", nodes, {})

    # Should complete at least 1 node before timeout
    assert len(exc_info.value.completed_nodes) >= 1
    assert exc_info.value.timeout_ms == 300


@pytest.mark.asyncio
async def test_pipeline_succeeds_within_timeout(timeout_config):
    """Test pipeline succeeds when all nodes complete within timeout."""
    from lukhas.orchestrator.config import OrchestratorConfig
    from lukhas.orchestrator.pipeline import PipelineExecutor

    config = OrchestratorConfig(timeouts=timeout_config)
    executor = PipelineExecutor(config)

    async def fast_node(input_data):
        await asyncio.sleep(0.02)  # 20ms each
        return input_data + 1

    # 3 nodes × 20ms = 60ms total < 300ms pipeline timeout
    nodes = [
        ("node1", fast_node),
        ("node2", fast_node),
        ("node3", fast_node),
    ]

    result = await executor.execute_pipeline("test_pipeline", nodes, 0)

    assert result == 3  # 0 + 1 + 1 + 1
```

### 2. Integration Tests

**File**: `tests/integration/orchestrator/test_timeout_integration.py`

```python
import pytest
import asyncio
from lukhas.orchestrator.orchestrator import Orchestrator
from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig


@pytest.mark.asyncio
async def test_real_pipeline_with_timeout():
    """Test real MATRIZ pipeline with timeout enforcement."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(
            node_timeout_ms=200,
            pipeline_timeout_ms=500
        )
    )

    orchestrator = Orchestrator(config)

    # Create test pipeline: perception → reasoning → action
    result = await orchestrator.execute(
        pipeline_name="test_perception_reasoning_action",
        input_data={"query": "What is 2+2?"}
    )

    assert result is not None
    # Verify pipeline completed within timeout


@pytest.mark.asyncio
async def test_timeout_metrics_recorded(metrics_client):
    """Test that timeout metrics are properly recorded."""
    config = OrchestratorConfig(
        timeouts=TimeoutConfig(node_timeout_ms=50)
    )

    orchestrator = Orchestrator(config)

    # Execute pipeline with slow node (will timeout)
    try:
        await orchestrator.execute("slow_pipeline", {})
    except:
        pass

    # Verify metrics recorded
    assert metrics_client.get_counter("orchestrator_node_timeouts_total") > 0
```

---

## Acceptance Criteria

- [ ] `TimeoutConfig` with node/pipeline/cleanup timeouts
- [ ] `NodeTimeoutException` and `PipelineTimeoutException` hierarchy
- [ ] `NodeExecutor` with `asyncio.wait_for` timeout enforcement
- [ ] `PipelineExecutor` with pipeline-level timeout
- [ ] Cancellation token support for graceful shutdown
- [ ] `CancellationRegistry` for managing cancellation tokens
- [ ] Timeout metrics: `orchestrator_node_timeouts_total`, `orchestrator_pipeline_timeouts_total`
- [ ] Duration metrics: `orchestrator_node_duration_ms`, `orchestrator_pipeline_duration_ms`
- [ ] Unit tests for node timeout, pipeline timeout, cancellation (>95% coverage)
- [ ] Integration tests with real pipelines
- [ ] Performance test: timeout overhead <5ms

---

## Monitoring

### Grafana Queries

```promql
# Node timeout rate
rate(orchestrator_node_timeouts_total[5m])

# Pipeline timeout rate
rate(orchestrator_pipeline_timeouts_total[5m])

# P95 node execution time
histogram_quantile(0.95, orchestrator_node_duration_ms_bucket)

# P95 pipeline execution time
histogram_quantile(0.95, orchestrator_pipeline_duration_ms_bucket)
```

---

## Documentation Updates

1. **docs/orchestrator/TIMEOUTS.md** - Complete timeout documentation
2. **docs/architecture/PERFORMANCE.md** - Update SLA enforcement section

---

**Estimated Completion**: 6-8 hours (Medium effort)
**PR Target**: Ready for review within 2 days
**Performance Impact**: <5ms overhead for timeout checks

