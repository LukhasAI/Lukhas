# Orchestrator Timeout System

## Overview

The LUKHAS Orchestrator provides comprehensive timeout enforcement for cognitive pipelines to ensure sub-250ms p95 latency SLA compliance. This system prevents hung nodes from blocking entire pipelines and enables graceful cancellation with proper resource cleanup.

## Architecture

### Components

1. **TimeoutConfig** - Configurable timeout budgets for nodes and pipelines
2. **NodeExecutor** - Executes individual cognitive nodes with timeout enforcement
3. **PipelineExecutor** - Executes multi-node pipelines with timeout handling
4. **CancellationRegistry** - Manages cancellation tokens for graceful shutdown
5. **Exception Hierarchy** - Structured exceptions for timeout and cancellation events

## Configuration

### TimeoutConfig

```python
from lukhas.orchestrator.config import TimeoutConfig

config = TimeoutConfig(
    node_timeout_ms=200,       # 200ms per node
    pipeline_timeout_ms=500,   # 500ms for entire pipeline
    cleanup_grace_ms=100,      # 100ms grace period for cleanup
    fail_fast=True             # Fail immediately on timeout
)
```

**Default Values:**
- `node_timeout_ms`: 200ms (aggressive, enforces per-node SLA)
- `pipeline_timeout_ms`: 500ms (total pipeline budget)
- `cleanup_grace_ms`: 100ms (time for graceful cleanup)
- `fail_fast`: True (immediately propagate timeouts)

### OrchestratorConfig

```python
from lukhas.orchestrator.config import OrchestratorConfig, TimeoutConfig

config = OrchestratorConfig(
    timeouts=TimeoutConfig(),
    max_concurrent_pipelines=10,
    enable_distributed_tracing=True,
    enable_metrics=True,
    enable_cancellation=True
)
```

## Usage

### Basic Node Execution

```python
from lukhas.orchestrator.executor import NodeExecutor
from lukhas.orchestrator.config import TimeoutConfig

executor = NodeExecutor(TimeoutConfig())

async def my_cognitive_node(input_data):
    # Process input
    result = await some_processing(input_data)
    return result

try:
    result = await executor.execute_node(
        node_id="my_node",
        node_func=my_cognitive_node,
        input_data={"query": "What is consciousness?"}
    )
except NodeTimeoutException as e:
    print(f"Node {e.node_id} timed out after {e.timeout_ms}ms")
```

### Pipeline Execution

```python
from lukhas.orchestrator.pipeline import PipelineExecutor
from lukhas.orchestrator.config import OrchestratorConfig

executor = PipelineExecutor(OrchestratorConfig())

# Define pipeline stages
nodes = [
    ("perception", perception_node),
    ("reasoning", reasoning_node),
    ("action", action_node),
]

try:
    result = await executor.execute_pipeline(
        pipeline_id="cognitive_loop",
        nodes=nodes,
        initial_input={"query": "Explain quantum entanglement"}
    )
except PipelineTimeoutException as e:
    print(f"Pipeline timed out after completing {len(e.completed_nodes)} nodes")
except NodeTimeoutException as e:
    print(f"Node {e.node_id} exceeded timeout")
```

### Cancellation Support

```python
from lukhas.orchestrator.cancellation import CancellationRegistry

registry = CancellationRegistry()

# Register pipeline
token = registry.register("my_pipeline")

# Execute with cancellation support
executor = NodeExecutor(config)
result = await executor.execute_node(
    node_id="long_running_node",
    node_func=my_node,
    input_data=data,
    cancellation_token=token
)

# Cancel from another context
registry.cancel("my_pipeline", reason="User requested")

# Cleanup
registry.unregister("my_pipeline")
```

## Exception Handling

### Exception Hierarchy

```
OrchestratorException
├── TimeoutException
│   ├── NodeTimeoutException
│   └── PipelineTimeoutException
└── CancellationException
```

### NodeTimeoutException

Raised when a single node exceeds its timeout budget.

```python
try:
    await executor.execute_node(...)
except NodeTimeoutException as e:
    print(f"Node: {e.node_id}")
    print(f"Timeout: {e.timeout_ms}ms")
```

### PipelineTimeoutException

Raised when the entire pipeline exceeds its timeout budget.

```python
try:
    await executor.execute_pipeline(...)
except PipelineTimeoutException as e:
    print(f"Pipeline: {e.pipeline_id}")
    print(f"Timeout: {e.timeout_ms}ms")
    print(f"Completed nodes: {e.completed_nodes}")
```

### CancellationException

Raised when a pipeline is explicitly cancelled.

```python
try:
    await executor.execute_node(..., cancellation_token=token)
except CancellationException as e:
    print(f"Pipeline: {e.pipeline_id}")
    print(f"Reason: {e.reason}")
```

## Metrics

The orchestrator exports comprehensive Prometheus metrics:

### Node Metrics

- `orchestrator_node_duration_ms` (histogram) - Node execution duration
- `orchestrator_node_executions_total` (counter) - Total node executions by status
- `orchestrator_node_timeouts_total` (counter) - Node timeout count

**Labels:**
- `node_id`: Unique node identifier
- `status`: success | timeout | error
- `error_type`: Exception class name (for errors)

### Pipeline Metrics

- `orchestrator_pipeline_duration_ms` (histogram) - Pipeline execution duration
- `orchestrator_pipeline_executions_total` (counter) - Total pipeline executions
- `orchestrator_pipeline_timeouts_total` (counter) - Pipeline timeout count
- `orchestrator_pipeline_node_count` (histogram) - Number of nodes in pipeline
- `orchestrator_pipeline_completed_nodes_at_timeout` (gauge) - Nodes completed before timeout

**Labels:**
- `pipeline_id`: Unique pipeline identifier
- `status`: success | timeout | error
- `error_type`: Exception class name (for errors)

### Grafana Queries

```promql
# Node timeout rate (timeouts per second)
rate(orchestrator_node_timeouts_total[5m])

# Pipeline timeout rate
rate(orchestrator_pipeline_timeouts_total[5m])

# P95 node execution time
histogram_quantile(0.95, orchestrator_node_duration_ms_bucket)

# P95 pipeline execution time
histogram_quantile(0.95, orchestrator_pipeline_duration_ms_bucket)

# Node success rate
rate(orchestrator_node_executions_total{status="success"}[5m])
/ rate(orchestrator_node_executions_total[5m])

# Pipeline success rate
rate(orchestrator_pipeline_executions_total{status="success"}[5m])
/ rate(orchestrator_pipeline_executions_total[5m])
```

## Performance Characteristics

### Overhead

Timeout enforcement adds minimal overhead:
- **Per-node overhead**: <1ms
- **Per-pipeline overhead**: <5ms
- **Cancellation check overhead**: <0.1ms

### SLA Targets

With default configuration:
- **Node timeout**: 200ms (aggressive)
- **Pipeline timeout**: 500ms (end-to-end)
- **P95 latency**: <250ms (includes all overhead)

### Cleanup Guarantees

When a timeout occurs:
1. Task is immediately cancelled via `asyncio.Task.cancel()`
2. Cleanup grace period (100ms) allows for graceful shutdown
3. If cleanup exceeds grace period, task is forcefully terminated
4. Metrics are recorded even for incomplete operations

## Best Practices

### 1. Set Appropriate Timeouts

```python
# For fast operations (perception, filtering)
config = TimeoutConfig(node_timeout_ms=50)

# For complex reasoning
config = TimeoutConfig(node_timeout_ms=300)

# For multi-stage pipelines
config = TimeoutConfig(
    node_timeout_ms=100,
    pipeline_timeout_ms=500
)
```

### 2. Handle Timeouts Gracefully

```python
try:
    result = await executor.execute_node(...)
except NodeTimeoutException:
    # Fallback to cached result or default
    result = get_cached_result()
    logger.warning("Node timed out, using cached result")
```

### 3. Monitor Timeout Rates

- **Target**: <1% node timeout rate
- **Alert**: >5% node timeout rate
- **Critical**: >10% pipeline timeout rate

### 4. Use Cancellation for Long Operations

```python
registry = CancellationRegistry()
token = registry.register(pipeline_id)

# Pass token to all nodes
for node_id, node_func in nodes:
    await executor.execute_node(
        node_id=node_id,
        node_func=node_func,
        input_data=data,
        cancellation_token=token
    )
```

### 5. Tune Timeouts Based on Metrics

```python
# Query P95 latency
p95_latency = get_p95_node_duration("reasoning_node")

# Adjust timeout to 2x P95 with headroom
new_timeout = int(p95_latency * 2.5)
config = TimeoutConfig(node_timeout_ms=new_timeout)
```

## Testing

### Unit Tests

```bash
pytest tests/unit/orchestrator/test_timeouts.py -v
```

### Integration Tests

```bash
pytest tests/integration/orchestrator/test_timeout_integration.py -v
```

### Performance Tests

```bash
pytest tests/performance/test_orchestrator_performance.py --benchmark
```

## Troubleshooting

### High Timeout Rates

**Symptoms:** >5% node/pipeline timeout rate

**Causes:**
- Node timeout too aggressive
- External service latency
- Resource contention

**Solutions:**
1. Increase node timeout budget
2. Add caching layer
3. Scale infrastructure
4. Optimize node implementation

### Memory Leaks on Timeout

**Symptoms:** Memory growth during timeouts

**Causes:**
- Tasks not properly cancelled
- Resources not released in cleanup

**Solutions:**
1. Ensure `try/finally` blocks in nodes
2. Implement proper cleanup handlers
3. Use context managers for resources
4. Monitor `orchestrator_pipeline_completed_nodes_at_timeout`

### Cancellation Not Working

**Symptoms:** Nodes continue after cancellation

**Causes:**
- Node not checking cancellation token
- Blocking operations without await

**Solutions:**
1. Check `cancellation_token.is_set()` in loops
2. Use async operations throughout
3. Break long operations into checkpoints

## Advanced Topics

### Custom Timeout Strategies

```python
class AdaptiveTimeoutConfig(TimeoutConfig):
    """Timeout config that adapts based on load."""

    def __init__(self, base_timeout_ms: int = 200):
        super().__init__(node_timeout_ms=base_timeout_ms)
        self.load_factor = 1.0

    def adjust_for_load(self, current_load: float):
        """Increase timeout under high load."""
        if current_load > 0.8:
            self.load_factor = 1.5
        else:
            self.load_factor = 1.0

        self.node_timeout_ms = int(self.base_timeout * self.load_factor)
```

### Distributed Tracing Integration

```python
config = OrchestratorConfig(
    enable_distributed_tracing=True
)

# Automatic span creation for:
# - Pipeline execution
# - Node execution
# - Timeout events
# - Cancellation events
```

## See Also

- [PERFORMANCE.md](../architecture/PERFORMANCE.md) - Performance SLA documentation
- [MATRIZ Architecture](../architecture/MATRIZ.md) - Cognitive architecture overview
- [Monitoring Guide](../operations/MONITORING.md) - Metrics and alerting setup
