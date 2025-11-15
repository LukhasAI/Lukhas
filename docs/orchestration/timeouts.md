# Orchestration Timeouts and Cancellation

The LUKHAS orchestration system provides robust support for managing timeouts and cancellations, ensuring that pipelines are resilient and responsive. This document explains how to use these features to build reliable and efficient data processing pipelines.

## Timeouts

Timeouts can be configured at both the node and pipeline level, providing granular control over the execution time of your pipelines.

### Pipeline Timeouts

A pipeline timeout defines the maximum amount of time that a pipeline can run before it is automatically cancelled. You can configure the default pipeline timeout in the `OrchestratorConfig`, or you can override it on a per-call basis.

```python
from lukhas.orchestration.orchestrator import Orchestrator
from lukhas.orchestrator.config import OrchestratorConfig

# Configure the default pipeline timeout to 60 seconds.
config = OrchestratorConfig()
config.timeouts.pipeline_timeout_seconds = 60

orchestrator = Orchestrator(config)

# Execute a pipeline with the default timeout.
await orchestrator.execute("my_pipeline", nodes, initial_input)

# Execute a pipeline with a custom timeout of 120 seconds.
await orchestrator.pipeline_executor.execute_pipeline(
    "my_pipeline", nodes, initial_input, timeout_seconds=120
)
```

### Node Timeouts

A node timeout defines the maximum amount of time that a single node can run before it is automatically cancelled. You can configure the default node timeout in the `OrchestratorConfig`.

```python
from lukhas.orchestration.config import OrchestratorConfig

# Configure the default node timeout to 10 seconds.
config = OrchestratorConfig()
config.timeouts.node_timeout_seconds = 10
```

## Cancellation

Pipelines can be cancelled at any time, allowing you to gracefully terminate long-running processes.

```python
import asyncio

# Start a pipeline in the background.
task = asyncio.create_task(
    orchestrator.execute("my_pipeline", nodes, initial_input)
)

# Cancel the pipeline after 5 seconds.
await asyncio.sleep(5)
await orchestrator.cancel("my_pipeline")
```

## Cleanup Handlers

You can provide optional cleanup handlers to be called when a pipeline is timed out or cancelled. This allows you to perform any necessary cleanup, such as closing database connections or releasing locks.

```python
async def on_timeout():
    print("Pipeline timed out!")

async def on_cancel():
    print("Pipeline cancelled!")

await orchestrator.pipeline_executor.execute_pipeline(
    "my_pipeline",
    nodes,
    initial_input,
    on_timeout=on_timeout,
    on_cancel=on_cancel,
)
```
