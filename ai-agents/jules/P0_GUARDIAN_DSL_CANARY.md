# Jules Task: Enable Guardian DSL Enforcement in Canary Mode (SG001)

**Task ID**: SG001
**Priority**: P0 (Critical)
**Effort**: Small (<4 hours)
**Owner**: Jules
**Branch**: `feat/guardian-dsl-canary-enforcement`

---

## Objective

Enable Guardian DSL policy enforcement in **canary mode** (10% traffic) for production safety validation before full rollout.

---

## Context

The Guardian system has DSL policies defined but enforcement is currently disabled. We need to:
1. Add a canary flag to enable enforcement for a small percentage of traffic
2. Implement sampling logic (10% of requests)
3. Add metrics to track enforcement actions
4. Ensure no production impact for 90% of traffic

**Related Tasks**:
- Blocks: SG006 (Gradual rollout depends on canary success)
- References: MASTER_LOG P0 tasks

---

## Implementation Requirements

### 1. Add Canary Configuration

**File**: `lukhas/governance/guardian/config.py` (or similar)

```python
from pydantic import BaseSettings

class GuardianConfig(BaseSettings):
    """Guardian configuration with canary mode."""

    # Canary settings
    enforcement_enabled: bool = False  # Master switch
    canary_enabled: bool = False  # Canary mode
    canary_percentage: float = 10.0  # Percentage of traffic (0-100)

    # Enforcement settings
    log_violations: bool = True
    block_on_violation: bool = False  # Set False for canary

    class Config:
        env_prefix = "GUARDIAN_"
```

### 2. Implement Sampling Logic

**File**: `lukhas/governance/guardian/enforcement.py`

```python
import random
from typing import Optional
from .config import GuardianConfig

class GuardianEnforcer:
    """DSL policy enforcer with canary sampling."""

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._canary_seed = random.Random()

    def should_enforce(self, request_id: Optional[str] = None) -> bool:
        """Determine if this request should have enforcement applied."""
        if not self.config.enforcement_enabled:
            return False

        if not self.config.canary_enabled:
            return True  # Full enforcement when not in canary

        # Canary sampling: use request_id for deterministic sampling
        if request_id:
            # Hash-based sampling for consistency
            sample = hash(request_id) % 100
        else:
            # Random sampling if no request_id
            sample = self._canary_seed.randint(0, 99)

        return sample < self.config.canary_percentage

    async def enforce(
        self,
        request: dict,
        policy: str
    ) -> dict:
        """Enforce Guardian policy with canary sampling."""
        from .metrics import guardian_metrics

        request_id = request.get("id", request.get("request_id"))
        should_enforce = self.should_enforce(request_id)

        # Track sampling decision
        guardian_metrics.canary_sample_total.inc()
        if should_enforce:
            guardian_metrics.canary_enforced_total.inc()

        if not should_enforce:
            # Log but don't enforce (90% of traffic)
            guardian_metrics.canary_skipped_total.inc()
            return {"enforced": False, "reason": "canary_skip"}

        # Apply enforcement (10% of traffic)
        # ... existing enforcement logic ...
```

### 3. Add Metrics

**File**: `lukhas/governance/guardian/metrics.py`

```python
from prometheus_client import Counter, Histogram

class GuardianMetrics:
    """Prometheus metrics for Guardian enforcement."""

    def __init__(self):
        # Canary metrics
        self.canary_sample_total = Counter(
            'guardian_canary_sample_total',
            'Total requests sampled for canary enforcement'
        )
        self.canary_enforced_total = Counter(
            'guardian_canary_enforced_total',
            'Requests where enforcement was applied (10%)'
        )
        self.canary_skipped_total = Counter(
            'guardian_canary_skipped_total',
            'Requests where enforcement was skipped (90%)'
        )

        # Violation metrics
        self.violations_detected = Counter(
            'guardian_violations_detected_total',
            'Policy violations detected',
            ['policy', 'severity']
        )

        # Latency
        self.enforcement_latency = Histogram(
            'guardian_enforcement_latency_seconds',
            'Time spent in Guardian enforcement',
            buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0]
        )

guardian_metrics = GuardianMetrics()
```

### 4. Update CI/CD Configuration

**File**: `.github/workflows/deploy-canary.yml` (or integrate into existing)

```yaml
name: Deploy Guardian Canary

on:
  workflow_dispatch:
    inputs:
      canary_percentage:
        description: 'Canary percentage (0-100)'
        required: true
        default: '10'

jobs:
  deploy-canary:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set canary configuration
        run: |
          echo "GUARDIAN_CANARY_ENABLED=true" >> $GITHUB_ENV
          echo "GUARDIAN_CANARY_PERCENTAGE=${{ github.event.inputs.canary_percentage }}" >> $GITHUB_ENV

      - name: Deploy with canary settings
        run: |
          # Add deployment logic
          echo "Deploying with ${{ github.event.inputs.canary_percentage }}% canary"

      - name: Validate canary metrics
        run: |
          # Check that metrics are being reported
          python scripts/validate_canary_metrics.py
```

---

## Testing Requirements

### 1. Unit Tests

**File**: `tests/unit/governance/test_guardian_canary.py`

```python
import pytest
from lukhas.governance.guardian.enforcement import GuardianEnforcer
from lukhas.governance.guardian.config import GuardianConfig

def test_canary_sampling_disabled():
    """Test that no enforcement happens when canary is disabled."""
    config = GuardianConfig(
        enforcement_enabled=True,
        canary_enabled=False
    )
    enforcer = GuardianEnforcer(config)

    # Should enforce all requests when canary disabled
    assert enforcer.should_enforce("test-request-1") is True

def test_canary_sampling_percentage():
    """Test that canary percentage is respected."""
    config = GuardianConfig(
        enforcement_enabled=True,
        canary_enabled=True,
        canary_percentage=10.0
    )
    enforcer = GuardianEnforcer(config)

    # Run 1000 samples and check approximate percentage
    samples = [
        enforcer.should_enforce(f"request-{i}")
        for i in range(1000)
    ]
    enforced_count = sum(samples)

    # Should be around 10% (allow 5% variance)
    assert 50 < enforced_count < 150  # 5-15%

def test_deterministic_sampling_with_request_id():
    """Test that same request_id always gets same decision."""
    config = GuardianConfig(
        enforcement_enabled=True,
        canary_enabled=True,
        canary_percentage=10.0
    )
    enforcer = GuardianEnforcer(config)

    # Same request_id should get same decision
    decision1 = enforcer.should_enforce("consistent-request-id")
    decision2 = enforcer.should_enforce("consistent-request-id")
    assert decision1 == decision2
```

### 2. Integration Tests

**File**: `tests/integration/governance/test_guardian_canary_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from lukhas.api.app import app

@pytest.mark.integration
def test_canary_metrics_exported():
    """Test that canary metrics are exported to Prometheus."""
    client = TestClient(app)

    # Make some requests
    for i in range(100):
        response = client.post(f"/api/v1/test", json={"id": f"test-{i}"})
        assert response.status_code == 200

    # Check metrics endpoint
    metrics_response = client.get("/metrics")
    assert "guardian_canary_sample_total" in metrics_response.text
    assert "guardian_canary_enforced_total" in metrics_response.text
    assert "guardian_canary_skipped_total" in metrics_response.text
```

---

## Acceptance Criteria

- [ ] Canary configuration is environment-variable driven
- [ ] 10% of traffic has enforcement enabled (configurable)
- [ ] 90% of traffic skips enforcement (no impact)
- [ ] Sampling is deterministic (same request_id → same decision)
- [ ] Prometheus metrics track sampling decisions
- [ ] Unit tests validate sampling logic (>90% coverage)
- [ ] Integration tests validate metrics export
- [ ] CI/CD workflow supports canary percentage adjustment
- [ ] Documentation updated in Guardian README

---

## Monitoring

**Grafana Queries** (add to Guardian dashboard):

```promql
# Canary sampling rate
rate(guardian_canary_enforced_total[5m]) / rate(guardian_canary_sample_total[5m])

# Should be ~0.10 (10%)

# Violations detected in canary
rate(guardian_violations_detected_total[5m])

# Enforcement latency (should be <100ms)
histogram_quantile(0.95, guardian_enforcement_latency_seconds_bucket)
```

---

## Rollback Plan

If canary causes issues:

```bash
# Disable canary immediately
export GUARDIAN_CANARY_ENABLED=false

# Or reduce percentage
export GUARDIAN_CANARY_PERCENTAGE=1.0  # 1% of traffic
```

---

## Related Files

- `lukhas/governance/guardian/config.py` - Configuration
- `lukhas/governance/guardian/enforcement.py` - Enforcement logic
- `lukhas/governance/guardian/metrics.py` - Prometheus metrics
- `.github/workflows/deploy-canary.yml` - Deployment workflow
- `tests/unit/governance/test_guardian_canary.py` - Unit tests
- `tests/integration/governance/test_guardian_canary_integration.py` - Integration tests

---

## References

- **TODO/MASTER_LOG.md** - Task SG001
- **Guardian DSL Specification** - `docs/governance/GUARDIAN_DSL.md`
- **Canary Deployment Pattern** - Martin Fowler's Canary Release

---

**Estimated Completion**: 3-4 hours
**PR Target**: Ready for review within 1 day
