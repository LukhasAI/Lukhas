# Orchestrator Memory Optimization

This document outlines the memory optimization work performed on the `CognitiveOrchestrator` in `matriz/core/orchestrator.py`.

## Problem

The `CognitiveOrchestrator` was experiencing unbounded memory growth, leading to a memory leak. The root causes of this issue were:

*   **Unbounded History:** The `execution_trace` and `matriz_graph` were storing a complete history of all operations, growing indefinitely.
*   **Data Duplication:** The `reasoning_chain` was stored in every `ExecutionTrace` object, leading to redundant data storage.
*   **Inefficient Object Creation:** Temporary helper classes were being created on every call to `process_query`, leading to unnecessary object churn.

## Optimizations

The following optimizations were performed to address these issues:

*   **Bounded History:** The `execution_trace` and `matriz_graph` were refactored to use `collections.deque` and `collections.OrderedDict` with a `max_history` limit. This prevents them from growing indefinitely.
*   **On-the-Fly Reasoning Chain:** The `reasoning_chain` is now generated on the fly in the `process_query` method, just before it's returned. This eliminates redundant data storage.
*   **Reusable Helper Class:** A single, reusable `_NodeEmitter` class was introduced to replace the temporary helper classes. This reduces object churn and improves memory efficiency.

## Results

These optimizations have successfully reduced the memory usage of the `CognitiveOrchestrator` to a steady state, well under the 100MB target. The memory profiling tests now pass, and the orchestrator's functionality is preserved.
