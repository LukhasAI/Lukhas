# Guardian Service Rollout Procedure

This document outlines the procedure for the gradual rollout of the Guardian service using the automated script.

## Overview

The rollout is performed in stages to minimize risk and ensure the stability of the system. The script automates the process of deploying the new version to a percentage of the fleet, running health checks, and validating key performance metrics.

The stages are:
- 10%
- 25%
- 50%
- 100%

At each stage, the script will:
1. Deploy the new version to the specified percentage of instances.
2. Pause for a stabilization period.
3. Perform health checks against the service's `/health` endpoint.
4. Query Prometheus for the Guardian's denial rate and compare it against a predefined threshold.

If any of these checks fail, the script will automatically roll back to the previous stable state.

## Running the Rollout Script

To initiate the rollout, run the script from the root of the repository:

```bash
./scripts/governance/gradual_guardian_rollout.sh [environment]
```

- `[environment]`: The target environment. Can be `staging` or `production`. Defaults to `staging`.

### Example

To start a rollout in the **staging** environment:

```bash
./scripts/governance/gradual_guardian_rollout.sh staging
```

To start a rollout in the **production** environment:

```bash
./scripts/governance/gradual_guardian_rollout.sh production
```

## Monitoring

The script provides real-time feedback on the rollout's progress. It is recommended to monitor the script's output closely during the entire procedure.

In addition to the script's output, you should also monitor the following:
- **Grafana Dashboards**: The "Guardian Service" dashboard for detailed metrics.
- **Logs**: The logs for the `guardian-service` pods in the target environment.

## Manual Rollback

If the automated rollback fails, or if you need to manually roll back for any other reason, follow these steps:

1.  **Halt the script**: Press `Ctrl+C` to stop the rollout script.
2.  **Execute the rollback command**: The specific command will depend on the deployment system. For Kubernetes, it would be:
    ```bash
    kubectl rollout undo deployment/guardian-service --namespace=<environment>
    ```
3.  **Verify the rollback**: Check the status of the deployment and ensure the previous version is running.
    ```bash
    kubectl rollout status deployment/guardian-service --namespace=<environment>
    ```
4.  **Investigate the failure**: Analyze the logs and metrics to determine the cause of the failure.
