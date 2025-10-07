---
status: wip
type: documentation
owner: unknown
module: slos
redirect: false
moved_to: null
---

![Status: WIP](https://img.shields.io/badge/status-wip-yellow)

# API Service Level Objectives (SLOs)

This document defines the SLOs for the LUKHAS AI API.

## 1. API Availability

- **SLI**: The proportion of successful HTTP requests to the API (status code < 500).
- **SLO**: 99.9% over a 28-day rolling window.
- **Error Budget**: 0.1%

## 2. API Latency

- **SLI**: The proportion of API requests served faster than 250ms.
- **SLO**: 95% of requests served faster than 250ms over a 28-day rolling window.
- **Error Budget**: 5% of requests can be slower than 250ms.

## 3. MATRIZ Pipeline Latency

- **SLI**: The proportion of MATRIZ pipeline executions that complete in under 250ms.
- **SLO**: 95% of pipelines complete in under 250ms over a 28-day rolling window.
- **Error Budget**: 5% of pipelines can take longer than 250ms.
