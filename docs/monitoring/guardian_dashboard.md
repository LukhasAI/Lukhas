# Guardian Policy Enforcement Dashboard

This document provides an overview of the Guardian Policy Enforcement dashboard in Grafana.

## Overview

The Guardian Policy Enforcement dashboard provides a real-time view of the health and performance of the Guardian policy enforcement engine. It is designed to help operators monitor the system for anomalies, troubleshoot issues, and understand the impact of policy changes.

## Panels

### DSL Enforcement %

This panel displays the percentage of incoming requests that are allowed by the Guardian policy, averaged over the last 5 minutes. It is a key indicator of the overall policy effectiveness. A sudden drop in this percentage could indicate a misconfiguration or an attack.

-   **Query:** `sum(rate(lukhas_guardian_decision_total{outcome="allow"}[5m])) / sum(rate(lukhas_guardian_decision_total[5m])) * 100`

### Violations/hr

This panel shows the number of requests per hour that are denied by the Guardian policy. This metric is useful for identifying spikes in malicious traffic, misconfigured clients, or overly restrictive policies.

-   **Query:** `sum(rate(lukhas_guardian_decision_total{outcome="deny"}[1h])) * 3600`

### Kill-switch Status

This panel displays the current status of the Guardian kill-switch. The kill-switch is a mechanism to bypass all Guardian policy enforcement in case of an emergency.

-   `1`: Active (Enforcing policies)
-   `0`: Inactive (Bypassed)
-   **Query:** `lukhas_guardian_kill_switch_status`

### Overrides

This panel shows the total number of policy overrides that have occurred in the last hour. Overrides are manual interventions to bypass a policy decision for a specific request.

-   **Query:** `sum(increase(lukhas_guardian_overrides_total[1h]))`

### Exemptions

This panel displays the number of requests that were exempt from policy enforcement in the last hour. Exemptions are pre-configured rules that exclude certain requests from policy checks.

-   **Query:** `sum(increase(lukhas_guardian_exemptions_total[1h]))`

### p50, p95, p99 Latency

These panels show the 50th, 95th, and 99th percentile of the Guardian policy evaluation latency over the last 5 minutes. These metrics are crucial for understanding the performance of the policy evaluation engine and its impact on overall application latency.

-   **p50 Query:** `histogram_quantile(0.50, sum(rate(lukhas_guardian_decision_duration_seconds_bucket[5m])) by (le))`
-   **p95 Query:** `histogram_quantile(0.95, sum(rate(lukhas_guardian_decision_duration_seconds_bucket[5m])) by (le))`
-   **p99 Query:** `histogram_quantile(0.99, sum(rate(lukhas_guardian_decision_duration_seconds_bucket[5m])) by (le))`

## Alerting

Alerts can be configured in Grafana based on the queries in this dashboard. Some recommended alerts include:

*   **High Violation Rate:** Alert when the number of violations per hour exceeds a certain threshold.
*   **Low Enforcement Rate:** Alert when the DSL enforcement percentage drops below a critical level.
*   **High Latency:** Alert when the p95 or p99 latency exceeds a defined SLO.
*   **Kill-switch Activated:** A critical alert to notify operators whenever the kill-switch is activated.
