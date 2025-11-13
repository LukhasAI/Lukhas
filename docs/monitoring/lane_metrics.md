# Lane-Specific Metrics

This document outlines the Prometheus metrics used to monitor the different development lanes within the LUKHAS system.

## Overview

Lane-specific metrics are designed to provide visibility into the performance and behavior of the `candidate`, `core`, and `lukhas` lanes. By tagging metrics with a `lane` label, we can compare the stability and efficiency of new features in the `candidate` lane against the `core` production environment.

## Metrics

### `lane_operations_total`

A counter that tracks the total number of operations executed in a specific lane.

-   **Metric Name:** `lane_operations_total`
-   **Type:** Counter
-   **Labels:**
    -   `lane`: The development lane (`candidate`, `core`, or `lukhas`).
    -   `operation`: The name of the operation being performed.

#### Example Query

To get the rate of operations per second for the `candidate` lane, you can use the following PromQL query:

```promql
rate(lane_operations_total{lane="candidate"}[5m])
```

### `lane_active_requests`

A gauge that measures the current number of active requests in a specific lane.

-   **Metric Name:** `lane_active_requests`
-   **Type:** Gauge
-   **Labels:**
    -   `lane`: The development lane (`candidate`, `core`, or `lukhas`).

#### Example Query

To get the total number of active requests across all lanes, you can use the following PromQL query:

```promql
sum(lane_active_requests)
```
