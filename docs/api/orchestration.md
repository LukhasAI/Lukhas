# Orchestration Module

**Last Updated**: 2025-11-08


The Orchestration module is the heart of the LUKHAS AI system, responsible for coordinating complex workflows, managing communication between subsystems, and ensuring resilient, intelligent behavior. It is designed to handle everything from fine-grained asynchronous pipelines to high-level hybrid AI decision-making.

## Architecture

The orchestration system is composed of three primary components that work together to manage the flow of information and control within the AI.

```
+---------------------------+       +-------------------------------+       +---------------------------+
|                           |       |                               |       |                           |
|  System Integration Hub   |------>|     GPT-Colony Orchestrator   |------>|      Async Orchestrator   |
| (Central Nervous System)  |       |   (Hybrid AI Coordination)    |       |   (Resilient Pipelines)   |
|                           |       |                               |       |                           |
+---------------------------+       +-------------------------------+       +---------------------------+
```

### 1. Async Orchestrator (`async_orchestrator.py`)

The `AsyncOrchestrator` is the foundation of the orchestration layer. It executes resilient, multi-stage asynchronous pipelines. Its key responsibilities are:

-   **Pipeline Execution:** Processes a query through a configurable sequence of "stages."
-   **Resilience:** Implements patterns like per-stage timeouts, exponential backoff retries, and circuit breakers to handle node failures gracefully.
-   **Parallelism:** Can execute independent stages in parallel to reduce latency.
-   **Adaptive Routing:** Monitors the health of registered "nodes" and can dynamically route tasks to healthy fallbacks if a primary node fails.

**Core Concepts:**

-   **Stage:** A single step in a pipeline, defined by a name, timeout, and retry configuration.
-   **Node:** A concrete implementation of a cognitive function (an `ICognitiveNode`) that is executed during a stage.

### 2. GPT-Colony Orchestrator (`gpt_colony_orchestrator.py`)

This component acts as a specialized, high-level orchestrator for coordinating between large language models (GPT) and decentralized cognitive systems (Colonies). It enables hybrid intelligence by combining the strengths of both.

**Key Features:**

-   **Orchestration Modes:** Provides multiple strategies for combining GPT and Colony outputs:
    -   `PARALLEL`: GPT and Colony process the task simultaneously.
    -   `SEQUENTIAL`: One system processes the task, and the other refines the output.
    -   `COMPETITIVE`: Both systems compete, and the best solution is chosen based on confidence scores.
    -   `COLLABORATIVE`: An iterative process where GPT and Colony refine the solution together.
    -   `HIERARCHICAL`: GPT acts as a supervisor, breaking down tasks for the Colonies.
    -   `FEDERATED`: Multiple Colonies process the task, and GPT aggregates the federated consensus.
-   **Lazy Loading:** Avoids import-time dependencies on heavy modules like `labs` by loading them only when a task requires them.

### 3. System Integration Hub (`integration_hub.py`)

The `SystemIntegrationHub` is the central nervous system of the entire LUKHAS AI. It connects all major subsystems, ensuring they are synchronized and can communicate effectively.

**Key Responsibilities:**

-   **Service Registration:** Provides a central point for all major hubs (`CoreHub`, `ConsciousnessHub`, `EthicsService`, `GoldenTrio`, etc.) to register themselves.
-   **Oscillator Synchronization:** Implements a quantum-inspired oscillator and a mito-inspired health monitoring system to ensure all components are synchronized and healthy. If a system becomes desynchronized, the hub can trigger a resynchronization pulse.
-   **Integrated Request Processing:** Routes incoming requests to the appropriate subsystem based on type (`ethics`, `learning`, `bio`, `core`, etc.), ensuring proper identity verification and health checks are performed first.

## Patterns and Best Practices

### Defining a Resilient Pipeline

To create a new workflow, define a series of stages in the `AsyncOrchestrator`. Each stage should have a clear purpose, a reasonable timeout, and a fallback node if possible.

**Example: A simple reasoning pipeline**

```python
from core.orchestration.async_orchestrator import AsyncOrchestrator

orchestrator = AsyncOrchestrator()

# Configure stages
pipeline_stages = [
    {
        "name": "intent_extraction",
        "node": "intent_node", # Resolves to "node:intent_node" in the registry
        "timeout_ms": 150,
        "max_retries": 2,
        "fallback_nodes": ("simple_intent_node",)
    },
    {
        "name": "knowledge_retrieval",
        "node": "knowledge_graph_node",
        "timeout_ms": 300,
        "max_retries": 3,
    },
    {
        "name": "response_generation",
        "node": "gpt4_response_node",
        "timeout_ms": 500,
        "max_retries": 1,
    }
]
orchestrator.configure_stages(pipeline_stages)

# Execute the pipeline
initial_context = {"query": "What is the capital of France?"}
result = await orchestrator.process_query(initial_context)
```

### Choosing an Orchestration Mode

The `GPTColonyOrchestrator` provides different modes for different use cases.

-   **Use `PARALLEL`** for speed when either GPT or a Colony can solve the task independently.
-   **Use `SEQUENTIAL`** when you need one system to provide an initial draft and the other to refine or validate it.
-   **Use `COMPETITIVE`** when you want the highest quality result and are willing to spend the resources to run both systems.
-   **Use `COLLABORATIVE`** for complex, creative tasks that benefit from multiple iterations of refinement.
-   **Use `HIERARCHICAL`** when a task is too large and needs to be broken down into smaller sub-tasks suitable for specialized colonies.

### Integrating a New Subsystem

To integrate a new major component into the LUKHAS AI:

1.  **Create a Hub:** Design a central integration hub for your new subsystem (e.g., `MyNewSystemHub`).
2.  **Register with the `SystemIntegrationHub`:** In `integration_hub.py`, import your hub and register an instance of it.
3.  **Establish Connections:** Connect your hub to other essential services like `CoreHub`, `EthicsService`, or `IdentityHub` as needed within the `_connect_systems` method.
4.  **Implement Health Monitoring:** Ensure your system participates in the oscillator synchronization and health monitoring loop so the hub can track its status.
5.  **Route Requests:** Add a new request type to the `process_integrated_request` method to route relevant tasks to your subsystem.
