# Request Queuing Architecture

## Overview

The request queuing system is designed to manage incoming requests to the LUKHAS orchestration engine. It provides a mechanism for prioritizing requests, applying backpressure to prevent system overload, and ensuring fairness among different request sources.

## Components

### `RequestQueue`

The core of the system is the `RequestQueue` class, located in `lukhas/orchestration/queue.py`. It is an asynchronous priority queue with the following features:

- **Priority Levels**: Requests can be submitted with `HIGH`, `NORMAL`, or `LOW` priority. Higher-priority requests are generally processed before lower-priority ones.
- **Backpressure**: The queue has a maximum size. If the queue is full, it will raise a `QueueFull` exception, signaling to the caller to either retry later or reject the request. This prevents the system from being overwhelmed with requests.
- **Fairness**: To prevent high-priority requests from a single source from starving all other requests, a fairness mechanism is implemented. If a request source has had a request processed within a configurable "fairness window," its subsequent high-priority requests will be temporarily deprioritized, allowing other requests to be processed.

### `Priority` Enum

An `IntEnum` that defines the available priority levels.

### `Request` NamedTuple

A `NamedTuple` that encapsulates a request's information, including its priority, a unique ID, its submission time, and the task to be executed.

## Flow

1. A request is submitted to the `RequestQueue` using the `put` method. The caller provides a request ID, a coroutine to be executed, and a priority level.
2. The `RequestQueue` stores the request in an `asyncio.PriorityQueue`.
3. A worker process retrieves the next request from the queue using the `get` method.
4. The `get` method applies the fairness logic. If the highest-priority request is from a source that has recently been served, it is temporarily re-queued with a slightly lower priority.
5. Once a fair request is selected, it is returned to the worker process for execution.

## Configuration

The `RequestQueue` can be configured with the following parameters:

- `max_size`: The maximum number of requests that can be in the queue at one time.
- `fairness_window`: The time window (in seconds) used by the fairness algorithm.
