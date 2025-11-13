# Observability Drill Runbook

## 1. Overview

This document outlines the procedures for conducting observability drills to test the monitoring, alerting, and incident response capabilities of the LUKHAS AI System. The goal is to proactively identify and address gaps in observability before they impact production.

## 2. Objectives

- **Verify Monitoring Coverage:** Ensure all critical components and services are monitored with the correct metrics.
- **Validate Alerting Rules:** Confirm that alerts are triggered under specific failure conditions and routed to the appropriate channels.
- **Measure Incident Response Times:** Measure the Mean Time to Detection (MTTD) and Mean Time to Acknowledgment (MTTA) for simulated incidents.
- **Assess Dashboard Accuracy:** Verify that observability dashboards update correctly and provide actionable insights during an incident.

## 3. Drill Scenarios

The following scenarios will be simulated as part of the observability drill.

### 3.1. Database Failure

- **Objective:** Simulate a complete failure of the primary database.
- **Simulation Steps:**
  1. Block network traffic to the database instance.
  2. Inject a database connection error in the application.
- **Expected Outcomes:**
  - A critical alert for "Database Unreachable" is triggered within 2 minutes.
  - The application health check status changes to "degraded" or "unhealthy."
  - The "Database Health" dashboard shows a spike in connection errors.

### 3.2. API Timeout

- **Objective:** Simulate a high-latency scenario for a critical API endpoint.
- **Simulation Steps:**
  1. Introduce an artificial delay (e.g., 10 seconds) in the API response.
- **Expected Outcomes:**
  - A warning alert for "High API Latency" is triggered within 5 minutes.
  - The "API Performance" dashboard shows an increase in p95 and p99 latency for the affected endpoint.

### 3.3. Memory Spike

- **Objective:** Simulate a memory leak or sudden increase in memory consumption in a service.
- **Simulation Steps:**
  1. Artificially increase memory usage in a container or process.
- **Expected Outcomes:**
  - A warning alert for "High Memory Utilization" is triggered when usage exceeds 80%.
  - The "Resource Utilization" dashboard reflects the memory spike.

## 4. Execution

The observability drills will be executed using the `scripts/observability/run_drill.py` script. The script provides functions to simulate each of the scenarios described above.

```bash
python3 scripts/observability/run_drill.py --scenario db_failure
```

## 5. Post-Drill Analysis

After each drill, the following actions should be taken:

1. **Review Alerting Performance:** Document whether alerts were triggered as expected and if they contained the necessary information.
2. **Analyze Dashboard Updates:** Confirm that dashboards provided a clear and accurate view of the simulated incident.
3. **Identify Gaps:** Create tickets for any identified gaps in monitoring, alerting, or dashboarding.
