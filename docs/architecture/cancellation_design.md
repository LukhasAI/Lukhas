# Orchestrator Cancellation and Cleanup Design

## Overview

This document outlines the design of the cancellation and cleanup system for the LUKHAS orchestrator. The system provides a robust mechanism for cancelling long-running pipelines, handling partial results, and ensuring that resources are properly cleaned up.

## Key Components

### `CancellationRegistry`

The `CancellationRegistry` is the central component for managing cancellation. It is responsible for:

- **Cancellation Tokens**: Issuing `asyncio.Event` tokens that can be used to signal cancellation to running tasks.
- **Cleanup Handlers**: Registering and executing asynchronous cleanup handlers when a pipeline is cancelled.
- **Partial Results**: Storing and retrieving the results of successfully completed nodes in a pipeline.

### `PipelineExecutor`

The `PipelineExecutor` is responsible for executing pipelines and integrating with the `CancellationRegistry`. It:

- Registers each pipeline with the `CancellationRegistry` to obtain a cancellation token.
- Stores the output of each successfully completed node as a partial result in the registry.
- Triggers cancellation on pipeline timeouts or downstream exceptions.
- Ensures that pipelines are unregistered from the registry upon completion.

## Usage

### Registering a Pipeline

When a new pipeline is executed, the `PipelineExecutor` automatically registers it with the `CancellationRegistry` and obtains a cancellation token. This token is then passed down to each node in the pipeline.

### Registering Cleanup Handlers

Cleanup handlers can be registered for a pipeline to ensure that resources are properly released on cancellation. Handlers should be asynchronous functions that perform the necessary cleanup tasks.

**Example:**

```python
async def cleanup_resource():
    # Code to clean up a resource
    pass

registry.register_cleanup_handler("my_pipeline", cleanup_resource)
```

### Storing and Retrieving Partial Results

The `PipelineExecutor` automatically stores the result of each successfully completed node. These results can be retrieved from the `CancellationRegistry` when a pipeline is cancelled or times out.

**Example:**

```python
try:
    await executor.execute_pipeline(pipeline_id, nodes, {})
except PipelineTimeoutException as e:
    print(f"Pipeline timed out. Partial results: {e.partial_results}")
```

### Manual Cancellation

Pipelines can be manually cancelled by calling the `cancel` method on the `CancellationRegistry`.

**Example:**

```python
await registry.cancel("my_pipeline", "User requested cancellation")
```

This will set the cancellation token and execute any registered cleanup handlers.
