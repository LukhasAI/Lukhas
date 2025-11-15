# Adaptive Routing Architecture

## Overview

The LUKHAS Adaptive Routing system provides a mechanism for dynamically routing requests to the most suitable service node based on real-time performance metrics. This ensures high availability and optimal performance by automatically directing traffic away from overloaded or failing nodes.

## Core Components

### Node

A `Node` represents a routable destination, such as a microservice instance, a worker process, or an external API endpoint. Each node maintains a set of performance metrics:

-   **`node_id`**: A unique identifier for the node.
-   **`capacity`**: The maximum number of concurrent requests the node can handle.
-   **`current_load`**: The number of in-flight requests.
-   **`average_latency_ms`**: The moving average of request latency in milliseconds.
-   **`error_rate`**: The moving average of the request error rate (0.0 to 1.0).

### Router

The `Router` is the central component that manages a registry of `Node` objects and selects the best one for a given request. It uses a configurable `RoutingStrategy` to make its decisions.

### Routing Strategies

A `RoutingStrategy` is a class that implements a specific algorithm for node selection. The following strategies are available:

-   **`LeastLoadedStrategy`**: Selects the node with the lowest ratio of `current_load` to `capacity`. This is the default strategy and is effective at distributing load evenly.
-   **`LowestLatencyStrategy`**: Selects the node with the lowest `average_latency_ms`. This strategy is ideal for latency-sensitive operations.

## How it Works

1.  **Node Registration**: Service instances (nodes) are registered with the `Router` upon startup, providing their `node_id` and `capacity`.
2.  **Node Selection**: When a request needs to be routed, the `Router`'s `select_node()` method is called. It applies the configured `RoutingStrategy` to the current list of registered nodes and returns the optimal one.
3.  **Metrics Update**: After a request is processed, the calling service is responsible for reporting the outcome to the `Router` via the `update_node_metrics()` method. This method takes the `node_id`, a `success` boolean, and the `latency_ms` of the operation.
4.  **Dynamic Adaptation**: The `Router` continuously updates the metrics for each node. As a result, the routing decisions adapt in real-time to the changing health and performance of the nodes.

## Configuration and Usage

To use the adaptive router, instantiate a `Router` object with the desired `RoutingStrategy`:

```python
from lukhas.orchestration.adaptive_routing import Router, LowestLatencyStrategy

# Use the lowest latency strategy
router = Router(strategy=LowestLatencyStrategy)

# Register nodes
await router.register_node("service-a-1", capacity=100)
await router.register_node("service-a-2", capacity=100)

# Select a node for a request
best_node = await router.select_node()
if best_node:
    # Send the request to best_node.node_id
    ...

# Update metrics after the request is complete
await router.update_node_metrics(
    node_id=best_node.node_id,
    success=True,
    latency_ms=120.0
)
```
