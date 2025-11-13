# Canary Deployment Strategy

This document outlines the canary deployment strategy for LUKHAS AI, which is designed to minimize risk and ensure a safe and reliable rollout of new features.

## Overview

The canary deployment process is automated using a GitHub Actions workflow that triggers on the push of a release candidate tag (e.g., `v1.2.3-rc1`). The workflow builds a new Docker image, pushes it to the Azure Container Registry, and then executes a canary deployment script that gradually shifts traffic to the new revision in Azure Container Apps.

## Prerequisites

Before using this canary deployment workflow, you must ensure that your Azure Container App is configured to be in **Multiple revision mode**. This can be set in the Azure portal or via the Azure CLI. If the app is in "Single revision mode", the canary deployment will fail.

## Workflow

The canary deployment workflow is defined in the `.github/workflows/canary-deployment.yml` file. It consists of two main jobs:

1.  **`build_and_push`**: This job is responsible for building the Docker image and pushing it to the Azure Container Registry. The image is tagged with the commit SHA to ensure traceability.

2.  **`canary_deploy`**: This job is triggered after the `build_and_push` job is complete. It logs in to Azure and then executes the `scripts/deployment/canary_deploy.sh` script to perform the gradual rollout.

## Deployment Script

The `scripts/deployment/canary_deploy.sh` script is the core of the canary deployment process. It performs the following steps:

1.  **Identifies Revisions**: The script identifies the new canary revision and the current stable revision in Azure Container Apps.

2.  **Initial Health Check**: Before shifting any traffic, the script performs a health check on the canary revision to ensure it's healthy and ready to receive traffic.

3.  **Gradual Traffic Rollout**: The script gradually shifts traffic to the canary revision in predefined stages (10%, 25%, 50%, 100%).

4.  **Health Checks**: After each traffic shift, the script performs a health check on the canary revision. If a health check fails, the script immediately triggers a rollback.

5.  **Rollback**: If a health check fails at any point during the deployment, the script rolls back the deployment by shifting 100% of the traffic back to the stable revision.

## Rollback Procedure

The rollback procedure is automated and is triggered under the following conditions:

*   The initial health check of the canary revision fails.
*   A health check fails after a traffic shift.

The rollback procedure consists of a single step:

1.  **Shift Traffic to Stable**: The script shifts 100% of the traffic back to the stable revision.

This ensures that any issues with the canary revision are immediately mitigated and that users are not affected.
