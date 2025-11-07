# Datadog Runbook

This document provides instructions for managing Datadog monitoring in the LUKHAS project.

## Importing the Dashboard

To import the dashboard into Datadog:

1.  Navigate to "Dashboards" > "New Dashboard" in Datadog.
2.  Click the gear icon and select "Import dashboard JSON".
3.  Copy the contents of `docs/gonzo/monitoring/datadog_wavec_endocrine.json` and paste it into the text box.
4.  Click "Save".

## Configuring Alert Rules

To configure the alert rules:

1.  Navigate to "Monitors" > "New Monitor" in Datadog.
2.  For each alert defined in `docs/gonzo/monitoring/alert_rules.json`, create a new monitor with the specified query, message, and tags.
3.  Configure the notification settings for each monitor (e.g., PagerDuty, Slack).

## Adding New Metrics

To add a new metric to the monitoring:

1.  Instrument the code to export the new metric using the `scripts/monitoring/export_metrics.py` script.
2.  Update the Datadog dashboard JSON (`docs/gonzo/monitoring/datadog_wavec_endocrine.json`) to add a new widget for the metric.
3.  If necessary, add a new alert rule for the metric in `docs/gonzo/monitoring/alert_rules.json` and configure it in Datadog.

## Interpreting Dashboard Widgets

-   **WaveC Snapshot Count**: The number of WaveC snapshots being created. A sudden drop could indicate a problem.
-   **WaveC Rollback Rate**: The percentage of WaveC snapshots that are being rolled back. A high rate could indicate a problem with the code.
-   **WaveC Snapshot Latency**: The time it takes to create a WaveC snapshot. High latency could indicate a performance problem.
-   **Lane-Guard Failures**: The number of times the lane-guard has failed. This could indicate a problem with the import boundaries.
