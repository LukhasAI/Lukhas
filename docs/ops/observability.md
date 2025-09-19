# Governance Observability Panels

The **LUKHAS Operations** Grafana dashboard now includes a dedicated governance row that surfaces real-time policy health. Import the `dashboards/lukhas_ops.json` file into Grafana (v9+) to provision the updated layout.

## Panels

| Panel | PromQL | Notes |
| --- | --- | --- |
| Policy Denials / min | `rate(lukhas_replay_policy_denials_total{lane=~"$lane"}[5m]) * 60` | Tracks replay denials per minute; thresholds flag sustained spikes above 5/min for candidate traffic. |
| Promotion Success Rate | `rate(lukhas_promotion_success_total{target_lane=~"$lane"}[5m]) / (rate(lukhas_promotion_attempts_total{target_lane=~"$lane"}[5m]) + 0.001)` | Highlights promotion funnel health. Values below 70% surface as yellow to prompt investigation. |

## Lane templating

The dashboard defines a `lane` templating variable bound to `LUKHAS_LANE`. Select the appropriate lane to scope the queries before exporting compliance snapshots.

## Import steps

1. Open Grafana → Dashboards → Import.
2. Upload `dashboards/lukhas_ops.json`.
3. Verify the **Governance** row renders both panels and that your Prometheus data source is selected.
4. Save the dashboard to persist the templating defaults for your lane.

## Required Prometheus metrics

Ensure the following metrics are scraped:

- `lukhas_replay_policy_denials_total`
- `lukhas_promotion_success_total`
- `lukhas_promotion_attempts_total`
- `lukhas_drift_ema` (for lane templating discovery)

These counters provide the policy ledger visibility demanded by governance auditors.
