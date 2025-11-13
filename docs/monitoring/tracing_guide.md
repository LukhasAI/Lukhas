# Distributed Tracing Guide

This document outlines the distributed tracing system implemented in the LUKHAS AI Platform, leveraging OpenTelemetry for comprehensive monitoring of MATRIZ orchestrator and node operations.

## Overview

Distributed tracing provides a detailed, end-to-end view of requests as they travel through the various components of the system. It is an essential tool for debugging, performance analysis, and understanding the complex interactions between MATRIZ nodes.

Our implementation uses the OpenTelemetry SDK to create, manage, and export traces. Traces are composed of spans, which represent individual operations (e.g., an orchestrator stage, a node's `process` method).

## Key Features

- **Automatic Tracing of MATRIZ Nodes:** The `trace_node_process` decorator automatically creates spans for any `ICognitiveNode.process` method, capturing its execution time, metadata, and outcome.
- **Trace Context Propagation:** The system automatically propagates the trace context across all orchestrator stages and node executions, ensuring that all operations related to a single request are linked in a single, cohesive trace.
- **OTLP Integration:** The system is configured to export traces via the OpenTelemetry Protocol (OTLP), allowing for integration with a wide range of observability platforms (e.g., Jaeger, Honeycomb, Datadog).
- **Resilient Design:** The tracing module is designed to be resilient. If the OpenTelemetry SDK is not installed, the tracing decorators and functions become no-ops, ensuring the application continues to function without errors.

## Usage

### Tracing MATRIZ Nodes

To trace a MATRIZ node, simply apply the `@trace_node_process` decorator to its `process` method:

```python
from lukhas.observability.distributed_tracing import trace_node_process

class MyCognitiveNode:
    name = "my_node"

    @trace_node_process
    async def process(self, ctx):
        # ... your logic here ...
        return {"result": "ok"}
```

The decorator will automatically:
- Create a new span named `matriz.node.my_node`.
- Link it to the parent span from the orchestrator.
- Record the node's name and input query as attributes.
- Set the span's status to `OK` or `ERROR` based on the outcome.
- Inject the updated trace context into the result, for propagation to the next stage.

### Orchestrator Tracing

The `AsyncOrchestrator` is already instrumented to manage the tracing lifecycle:
1. It creates a top-level span for each `process_query` or `process_query_parallel` call.
2. It extracts the trace context from the initial input.
3. It passes the trace context to each stage, which is then picked up by the `@trace_node_process` decorator.
4. It ensures the trace context is propagated between stages.

No additional setup is required to trace orchestrator operations.

## Interpreting Traces

When viewed in an observability platform, a trace will appear as a waterfall diagram of spans. A typical trace will show:
- A root span representing the entire orchestrator pipeline (`matriz_pipeline` or `matriz_parallel_pipeline`).
- Nested spans for each orchestrator stage (`matriz.stage_...`).
- Further nested spans for each MATRIZ node execution (`matriz.node...`).

By examining the duration, attributes, and status of each span, you can:
- Identify performance bottlenecks.
- Trace the flow of a request through the system.
- Understand the causal relationships between different operations.
- Quickly diagnose the root cause of errors.
