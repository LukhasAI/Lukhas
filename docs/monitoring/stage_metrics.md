# Orchestration Stage Metrics

This document outlines the Prometheus metrics provided by the `lukhas.orchestration.stage_metrics` module. These metrics are essential for monitoring the performance and reliability of orchestration pipelines within the LUKHAS ecosystem.

## Overview

The `stage_metrics` module offers a standardized way to track the execution of multi-stage pipelines. It provides histograms and counters for both individual stages and the overall pipeline, allowing for detailed analysis of latency, throughput, and error rates.

## Metrics

All metrics are prefixed with `lukhas_orchestration_`.

### Pipeline Metrics

These metrics track the performance of an entire orchestration pipeline from start to finish.

- **`lukhas_orchestration_pipeline_duration_seconds`** (Histogram)
  - Description: The total time taken to execute a pipeline.
  - Labels:
    - `lane`: The deployment lane (e.g., `production`, `staging`).
    - `pipeline_name`: The name of the pipeline (e.g., `matriz_async_cognitive`).
    - `status`: The final status of the pipeline (`success`, `failure`, `timeout`).

- **`lukhas_orchestration_pipeline_total`** (Counter)
  - Description: The total number of pipeline executions.
  - Labels:
    - `lane`: The deployment lane.
    - `pipeline_name`: The name of the pipeline.
    - `status`: The final status of the pipeline.

### Stage Metrics

These metrics track the performance of individual stages within a pipeline.

- **`lukhas_orchestration_stage_duration_seconds`** (Histogram)
  - Description: The time taken to execute a single stage.
  - Labels:
    - `lane`: The deployment lane.
    - `pipeline_name`: The name of the pipeline the stage belongs to.
    - `stage_name`: The name of the stage (e.g., `intent`, `processing`).
    - `outcome`: The outcome of the stage (`success`, `failure`, `timeout`).

- **`lukhas_orchestration_stage_total`** (Counter)
  - Description: The total number of stage executions.
  - Labels:
    - `lane`: The deployment lane.
    - `pipeline_name`: The name of the pipeline the stage belongs to.
    - `stage_name`: The name of the stage.
    - `outcome`: The outcome of the stage.

## Usage

To record metrics, import and use the `record_pipeline_metrics` and `record_stage_metrics` functions from the module.

```python
from lukhas.orchestration.stage_metrics import record_pipeline_metrics, record_stage_metrics

# Record a successful stage
record_stage_metrics(
    pipeline_name="my_pipeline",
    stage_name="data_fetching",
    duration_sec=0.25,
    outcome="success"
)

# Record a failed pipeline
record_pipeline_metrics(
    pipeline_name="my_pipeline",
    duration_sec=1.2,
    status="failure"
)
```
