# Orchestrator Stress Testing

## Overview

This document describes the stress testing methodology for the LUKHAS async orchestrator. The primary goal of these tests is to ensure the orchestrator's performance, stability, and reliability under high load and adverse conditions.

The stress tests are located in `tests/load/orchestrator_stress_test.py`.

## Test Scenarios

The stress test suite includes the following scenarios:

### 1. Concurrent Requests

- **Purpose:** To verify the orchestrator's ability to handle a large number of concurrent pipeline executions.
- **Methodology:** Launches 1000 concurrent pipelines, each consisting of three simple, successful nodes.
- **Success Criteria:**
    - All 1000 pipelines must complete successfully.
    - The 95th percentile (p95) latency for pipeline execution must be below 250ms.

### 2. Timeout Handling

- **Purpose:** To ensure the orchestrator correctly handles both node and pipeline timeouts.
- **Methodology:**
    - **Node Timeout:** Executes a pipeline containing a node that is designed to be slower than the configured node timeout.
    - **Pipeline Timeout:** Executes a pipeline where the cumulative execution time of its nodes exceeds the configured pipeline timeout.
- **Success Criteria:**
    - The orchestrator must raise a `NodeTimeoutException` when a node times out.
    - The orchestrator must raise a `PipelineTimeoutException` when a pipeline times out.

### 3. Cancellation

- **Purpose:** To verify that in-flight pipeline executions can be successfully cancelled.
- **Methodology:** Starts a long-running pipeline and then sets a cancellation token.
- **Success Criteria:**
    - The orchestrator must raise a `CancellationException`.
    - The pipeline must not run to completion.

### 4. Error Recovery

- **Purpose:** To test the orchestrator's ability to gracefully handle and report errors that occur within a node.
- **Methodology:** Executes a pipeline that includes a node designed to raise an exception.
- **Success Criteria:**
    - The orchestrator must propagate the exception raised by the node.

## Running the Tests

To run the orchestrator stress tests, use the following command:

```bash
pytest tests/load/orchestrator_stress_test.py
```
