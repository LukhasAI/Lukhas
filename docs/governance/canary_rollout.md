# Canary Rollout for the Guardian System

This document outlines the process for rolling out new features in the Guardian system using a canary release strategy.

## Overview

The canary rollout process allows us to test new features with a small percentage of live traffic before rolling them out to all users. This helps us to identify and fix any issues with the new feature in a controlled environment.

## Configuration

The canary rollout is controlled by the `canary_percentage` parameter in the `is_canary_enforced` function. This parameter determines the percentage of traffic that will be directed to the new feature.

To configure the canary rollout, you will need to modify the call to the `is_canary_enforced` function in the Guardian system's entry point. For example, to send 10% of traffic to the new feature, you would call the function like this:

```python
from lukhas.governance.guardian.canary import is_canary_enforced

if is_canary_enforced(canary_percentage=10.0):
    # Use the new feature
else:
    # Use the existing feature
```

## Metrics

The canary rollout process includes metrics tracking to help us monitor the performance of the new feature. The following metrics are available:

- `canary_requests_total`: The total number of requests that have been subject to the canary rollout process.
- `canary_enforced_total`: The total number of requests that have been directed to the new feature.

These metrics can be used to monitor the performance of the new feature and to identify any issues that may arise.
