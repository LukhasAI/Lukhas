---
status: wip
type: documentation
---
# Lambda Products Integration Test Report

**Date:** 2025-08-07T00:16:24.959898

## Summary

- **Total Tests:** 6
- **Passed:** 5
- **Failed:** 1
- **Success Rate:** 83.3%

## Integration Tests

### Plugin Registration Performance
**Status:** PASSED

**Metrics:**
- total_registrations: 1000
- total_time_ms: 5.54
- avg_time_ms: 0.006
- ops_per_sec: 180472.0

### Agent Orchestration
**Status:** PASSED

**Details:**
- agents_deployed: 5
- active_agents: 0

### Lukhas PWM Integration
**Status:** FAILED

**Details:**
- pwm_available: True
- products_registered: 0
- consciousness_connected: False

### API Endpoints
**Status:** PASSED

### Deployment Readiness
**Status:** PASSED
