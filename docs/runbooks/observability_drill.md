---
status: wip
type: documentation
owner: unknown
module: runbooks
redirect: false
moved_to: null
---

# Observability Drill Runbook

## 1. Objective
This runbook outlines the procedure for conducting an observability drill on the LUKHAS AI system. The primary goal is to test and verify the effectiveness of our monitoring, alerting, and logging systems in detecting, diagnosing, and responding to system failures.

## 2. Participants
- **Drill Leader**: (Name/Team) - Responsible for overseeing the drill.
- **On-call Engineer**: (Name/Team) - Responsible for responding to the simulated incident.

## 3. Prerequisites
- The LUKHAS application is running in a staging or pre-production environment.
- The full observability stack is deployed and operational:
  - **Prometheus**: Scraping metrics from the application.
  - **Grafana**: Dashboards are set up for key application and system metrics.
  - **Alertmanager**: Configured to send alerts to a designated channel (e.g., a test Slack channel).
  - **Loki**: Aggregating logs from the application.

## 4. Drill Scenario: High API Latency
This drill will simulate a sudden increase in response time for a critical API endpoint. This will test our ability to detect performance degradation, which might not immediately result in errors but can severely impact user experience and system stability.

- **Target Component**: `api` service.
- **Target Endpoint**: `/feedback/health` (as it's used in the healthcheck).
- **Simulated Failure**: Introduce an artificial delay to mimic slow processing.

## 5. Execution Steps

### Step 1: Establish Baseline (5 mins)
1.  Navigate to the primary LUKHAS application dashboard in Grafana.
2.  Observe the current values for the following metrics for the `/feedback/health` endpoint:
    - `lukhas_ai_response_time_seconds_p95` (or similar histogram).
    - `lukhas_ai_requests_total` for status codes `200`.
3.  Take a screenshot or note down the current values. All metrics should be within normal operating ranges.

### Step 2: Simulate Failure (5 mins)
1.  **Action**: Introduce a 2-second delay into the `/feedback/health` endpoint handler in the application code.
    *   *Note for engineer*: A simple way to do this is to add `time.sleep(2)` in the relevant request handler function.
2.  Deploy the change to the environment where the drill is being conducted.

### Step 3: Observe and Detect (10 mins)
1.  Continuously monitor the Grafana dashboard.
2.  **Look for**:
    - A significant increase in the `lukhas_ai_response_time_seconds` histogram for the `/feedback/health` endpoint. The p95 latency should rise to over 2 seconds.
    - The `healthcheck` on the `api` service in `docker-compose.yml` might start failing if the timeout (10s) is breached, leading to container restarts. This would be visible in Docker logs and potentially as an alert.
3.  Note the time it takes for the metric changes to become clearly visible on the dashboard.

### Step 4: Verify Alerting (10 mins)
1.  Wait for an alert to be triggered by Alertmanager.
2.  **Verify**:
    - An alert for "High API Latency" or a similar rule is received in the configured notification channel.
    - The alert contains relevant information, such as the affected service, endpoint, and current latency.
    - The alert should provide a link to the relevant Grafana dashboard or runbook.
3.  Note the time it takes from failure simulation to alert reception.

### Step 5: Diagnose with Logs (10 mins)
1.  Access the Loki logs via Grafana's "Explore" view.
2.  Use a LogQL query to find logs related to the `/feedback/health` endpoint. Example query: `{job="api"} | json | line_format "{{.message}}"`
3.  Look for any log messages indicating slow processing or healthcheck failures.
4.  Assess if the logs provide enough context to diagnose the issue.

### Step 6: Rollback and Recovery (10 mins)
1.  **Action**: Revert the code change that introduced the delay.
2.  Deploy the fix to the environment.
3.  Monitor the Grafana dashboard and Alertmanager.
4.  **Verify**:
    - The `lukhas_ai_response_time_seconds` metric returns to the baseline level.
    - The "High API Latency" alert is resolved and a recovery notification is sent.
5.  Note the time it takes for the system to recover.

## 6. Success Criteria
The drill is considered successful if:
- [ ] The high latency is clearly visible on the Grafana dashboard within **5 minutes** of the failure simulation.
- [ ] An alert is received in the designated channel within **10 minutes**.
- [ ] Relevant logs for the affected endpoint can be easily located and queried in Loki/Grafana.
- [ ] The on-call engineer can correctly identify the root cause (or at least the affected component and endpoint) using the provided observability tools.

## 7. Post-Drill Analysis
- **What went well?**
- **What could be improved?**
- **Were there any gaps in metrics, dashboards, alerts, or logs?**
- **Action Items**:
  - (Ticket ID) - (Description of follow-up action)
  - (Ticket ID) - (Description of follow-up action)

---
*This runbook provides a template for running observability drills. The specific failure scenarios can be adapted and expanded over time to cover other potential issues.*
