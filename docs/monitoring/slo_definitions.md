# LUKHAS Subsystem SLO Definitions

This document provides definitions for the Service Level Objectives (SLOs) that govern the performance and reliability of key LUKHAS subsystems. These SLOs are monitored using Prometheus and are defined as recording rules in `lukhas/observability/slo_monitoring.py`.

---

## 1. Memory Recall Latency

- **Service Level Indicator (SLI)**: The proportion of memory recall operations that complete in under 100 milliseconds. This measures the speed of our memory retrieval, which is critical for real-time cognitive functions.
- **Service Level Objective (SLO)**: **99.0%** of memory recall operations must complete in under **100ms**.
- **Rationale**: A fast memory recall is essential for maintaining fluid conversations and providing timely information. This SLO ensures a highly responsive user experience.

---

## 2. Pipeline Execution Latency (p95)

- **Service Level Indicator (SLI)**: The 95th percentile (p95) of the end-to-end cognitive pipeline execution latency. This captures the "worst-case" latency experienced by the majority of users.
- **Service Level Objective (SLO)**: The p95 pipeline execution latency must be less than **250ms**.
- **Rationale**: This SLO guarantees that even complex processing pipelines remain fast enough for interactive applications. Keeping the p95 latency low prevents user-perceptible delays.

---

## 3. Cascade Prevention Success Rate

- **Service Level Indicator (SLI)**: The proportion of potential cascading failures that are successfully identified and prevented by the resilience subsystems.
- **Service Level Objective (SLO)**: **99.7%** of potential cascading failures must be prevented.
- **Rationale**: Cascading failures pose a significant threat to system stability. This SLO ensures that our resilience mechanisms are effective at isolating faults and preventing widespread outages, maintaining high overall system availability.
