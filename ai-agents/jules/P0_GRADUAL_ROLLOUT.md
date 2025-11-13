# Jules Task: Gradual Guardian Enforcement Rollout (SG006)

**Task ID**: SG006
**Priority**: P0 (Critical)
**Effort**: Medium (4-16 hours)
**Owner**: Jules
**Branch**: `feat/guardian-gradual-rollout`

---

## Objective

Implement a **gradual rollout strategy** for Guardian DSL enforcement, transitioning from canary mode (10%) to full enforcement (100%) with safety checkpoints, automated rollback, and monitoring.

---

## Context

After enabling canary mode (SG001), we need a controlled path to full enforcement:
1. Start at 10% enforcement (canary mode)
2. Gradually increase to 25%, 50%, 75%, 100%
3. Monitor error rates and user impact at each stage
4. Automatic rollback if issues detected
5. Manual gates for human approval at critical thresholds

**Success Criteria**: Zero-downtime rollout with <0.5% error rate increase.

---

## Implementation Requirements

### 1. Rollout Configuration

**File**: `lukhas/governance/rollout_config.py`

```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, timedelta


@dataclass
class RolloutStage:
    """Configuration for a single rollout stage."""
    name: str
    percentage: int  # 0-100
    duration: timedelta  # Minimum time at this stage
    max_error_rate: float  # Rollback threshold (e.g., 0.005 = 0.5%)
    requires_approval: bool  # Human gate required?


@dataclass
class RolloutConfig:
    """Complete rollout configuration."""
    stages: List[RolloutStage]
    current_stage_index: int
    current_stage_started_at: Optional[datetime]
    rollback_on_error: bool = True

    @classmethod
    def default(cls) -> "RolloutConfig":
        """Default 5-stage rollout."""
        return cls(
            stages=[
                RolloutStage(
                    name="canary",
                    percentage=10,
                    duration=timedelta(hours=24),
                    max_error_rate=0.005,  # 0.5%
                    requires_approval=False
                ),
                RolloutStage(
                    name="quarter",
                    percentage=25,
                    duration=timedelta(hours=24),
                    max_error_rate=0.004,  # 0.4%
                    requires_approval=True  # Human gate
                ),
                RolloutStage(
                    name="half",
                    percentage=50,
                    duration=timedelta(hours=48),
                    max_error_rate=0.003,  # 0.3%
                    requires_approval=True  # Human gate
                ),
                RolloutStage(
                    name="most",
                    percentage=75,
                    duration=timedelta(hours=24),
                    max_error_rate=0.002,  # 0.2%
                    requires_approval=False
                ),
                RolloutStage(
                    name="full",
                    percentage=100,
                    duration=timedelta(hours=0),  # Final stage
                    max_error_rate=0.002,  # 0.2%
                    requires_approval=True  # Final human approval
                ),
            ],
            current_stage_index=0,  # Start at canary
            current_stage_started_at=None,
            rollback_on_error=True
        )

    def current_stage(self) -> RolloutStage:
        """Get current rollout stage."""
        return self.stages[self.current_stage_index]

    def can_advance(self, error_rate: float) -> tuple[bool, str]:
        """Check if we can advance to next stage."""
        current = self.current_stage()

        # Check error rate threshold
        if error_rate > current.max_error_rate:
            return False, f"Error rate {error_rate:.3%} exceeds threshold {current.max_error_rate:.3%}"

        # Check minimum duration
        if self.current_stage_started_at:
            elapsed = datetime.utcnow() - self.current_stage_started_at
            if elapsed < current.duration:
                remaining = current.duration - elapsed
                return False, f"Stage duration not met (remaining: {remaining})"

        # Check if already at final stage
        if self.current_stage_index >= len(self.stages) - 1:
            return False, "Already at final stage"

        # Check if next stage requires approval
        next_stage = self.stages[self.current_stage_index + 1]
        if next_stage.requires_approval:
            return True, f"Ready to advance to {next_stage.name} (requires approval)"

        return True, f"Ready to advance to {next_stage.name}"

    def advance(self) -> None:
        """Advance to next stage."""
        if self.current_stage_index < len(self.stages) - 1:
            self.current_stage_index += 1
            self.current_stage_started_at = datetime.utcnow()

    def rollback(self) -> None:
        """Rollback to previous stage."""
        if self.current_stage_index > 0:
            self.current_stage_index -= 1
            self.current_stage_started_at = datetime.utcnow()
```

### 2. Rollout Manager

**File**: `lukhas/governance/rollout_manager.py`

```python
import asyncio
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .rollout_config import RolloutConfig, RolloutStage
from .guardian_enforcer import GuardianEnforcer
from lukhas.monitoring.metrics import MetricsClient

logger = logging.getLogger(__name__)


class RolloutManager:
    """Manages gradual Guardian enforcement rollout."""

    def __init__(
        self,
        config: RolloutConfig,
        enforcer: GuardianEnforcer,
        metrics: MetricsClient,
        state_path: Path = Path("/tmp/guardian_rollout_state.json")
    ):
        self.config = config
        self.enforcer = enforcer
        self.metrics = metrics
        self.state_path = state_path

        # Load persisted state
        self._load_state()

    def _load_state(self) -> None:
        """Load rollout state from disk."""
        if self.state_path.exists():
            import json
            state = json.loads(self.state_path.read_text())
            self.config.current_stage_index = state.get("current_stage_index", 0)
            started_at = state.get("current_stage_started_at")
            if started_at:
                self.config.current_stage_started_at = datetime.fromisoformat(started_at)

    def _save_state(self) -> None:
        """Persist rollout state to disk."""
        import json
        state = {
            "current_stage_index": self.config.current_stage_index,
            "current_stage_started_at": (
                self.config.current_stage_started_at.isoformat()
                if self.config.current_stage_started_at
                else None
            ),
            "updated_at": datetime.utcnow().isoformat()
        }
        self.state_path.write_text(json.dumps(state, indent=2))

    async def get_current_error_rate(self, window: timedelta = timedelta(hours=1)) -> float:
        """Calculate error rate from Prometheus metrics."""
        # Query Prometheus for Guardian enforcement errors
        # This is a simplified example - real implementation would query Prometheus API

        # Example: Calculate error rate from metrics
        total_requests = await self.metrics.query_counter(
            "guardian_enforcement_total",
            window=window
        )

        failed_requests = await self.metrics.query_counter(
            "guardian_enforcement_failed_total",
            window=window
        )

        if total_requests == 0:
            return 0.0

        return failed_requests / total_requests

    async def check_and_advance(self) -> tuple[bool, str]:
        """Check if we can advance and do so if possible."""
        current_stage = self.config.current_stage()

        # Get current error rate
        error_rate = await self.get_current_error_rate()

        # Record metrics
        self.metrics.gauge(
            "guardian_rollout_stage",
            self.config.current_stage_index,
            tags={"stage_name": current_stage.name}
        )
        self.metrics.gauge("guardian_rollout_error_rate", error_rate)

        # Check if rollback needed
        if error_rate > current_stage.max_error_rate and self.config.rollback_on_error:
            logger.error(
                f"Error rate {error_rate:.3%} exceeds threshold {current_stage.max_error_rate:.3%} "
                f"at stage {current_stage.name}. Initiating rollback."
            )
            self.rollback()
            return False, f"Rolled back due to high error rate: {error_rate:.3%}"

        # Check if we can advance
        can_advance, reason = self.config.can_advance(error_rate)

        if not can_advance:
            logger.info(f"Cannot advance: {reason}")
            return False, reason

        # Check if next stage requires approval
        next_stage = self.config.stages[self.config.current_stage_index + 1]
        if next_stage.requires_approval:
            logger.info(f"Stage {next_stage.name} requires manual approval. Not auto-advancing.")
            return False, f"Ready but requires approval: {reason}"

        # Advance!
        logger.info(f"Advancing from {current_stage.name} to {next_stage.name}")
        self.advance()

        return True, f"Advanced to stage {next_stage.name} ({next_stage.percentage}%)"

    def advance(self) -> None:
        """Advance to next stage and update enforcer."""
        self.config.advance()
        current_stage = self.config.current_stage()

        # Update Guardian enforcer percentage
        self.enforcer.config.canary_percentage = current_stage.percentage

        # Persist state
        self._save_state()

        # Record metrics
        self.metrics.increment(
            "guardian_rollout_advancement",
            tags={"to_stage": current_stage.name}
        )

        logger.info(
            f"Advanced to stage {current_stage.name}: {current_stage.percentage}% enforcement"
        )

    def rollback(self) -> None:
        """Rollback to previous stage."""
        old_stage = self.config.current_stage()
        self.config.rollback()
        new_stage = self.config.current_stage()

        # Update Guardian enforcer percentage
        self.enforcer.config.canary_percentage = new_stage.percentage

        # Persist state
        self._save_state()

        # Record metrics
        self.metrics.increment(
            "guardian_rollout_rollback",
            tags={"from_stage": old_stage.name, "to_stage": new_stage.name}
        )

        logger.warning(
            f"Rolled back from {old_stage.name} to {new_stage.name}: "
            f"{new_stage.percentage}% enforcement"
        )

    def manual_advance(self) -> tuple[bool, str]:
        """Manually advance to next stage (for human approval)."""
        current_stage = self.config.current_stage()

        if self.config.current_stage_index >= len(self.config.stages) - 1:
            return False, "Already at final stage"

        next_stage = self.config.stages[self.config.current_stage_index + 1]

        logger.info(
            f"Manual advancement from {current_stage.name} to {next_stage.name} "
            f"by authorized user"
        )

        self.advance()

        return True, f"Manually advanced to stage {next_stage.name}"

    def get_status(self) -> dict:
        """Get current rollout status."""
        current_stage = self.config.current_stage()

        elapsed = None
        if self.config.current_stage_started_at:
            elapsed = datetime.utcnow() - self.config.current_stage_started_at

        return {
            "current_stage": {
                "name": current_stage.name,
                "percentage": current_stage.percentage,
                "max_error_rate": current_stage.max_error_rate,
                "requires_approval": current_stage.requires_approval,
            },
            "stage_index": self.config.current_stage_index,
            "total_stages": len(self.config.stages),
            "elapsed_time": str(elapsed) if elapsed else None,
            "min_duration": str(current_stage.duration),
            "started_at": (
                self.config.current_stage_started_at.isoformat()
                if self.config.current_stage_started_at
                else None
            ),
        }
```

### 3. Rollout Monitoring Loop

**File**: `lukhas/governance/rollout_monitor.py`

```python
import asyncio
import logging
from datetime import timedelta

from .rollout_manager import RolloutManager

logger = logging.getLogger(__name__)


async def run_rollout_monitor(
    manager: RolloutManager,
    check_interval: timedelta = timedelta(minutes=15)
):
    """Background task to monitor and advance rollout."""
    logger.info("Starting Guardian rollout monitor")

    while True:
        try:
            advanced, message = await manager.check_and_advance()

            if advanced:
                logger.info(f"Rollout advancement: {message}")

            # Log status periodically
            status = manager.get_status()
            logger.info(
                f"Rollout status: stage {status['current_stage']['name']} "
                f"({status['current_stage']['percentage']}%), "
                f"elapsed: {status['elapsed_time']}"
            )

        except Exception as e:
            logger.exception(f"Error in rollout monitor: {e}")

        # Wait before next check
        await asyncio.sleep(check_interval.total_seconds())
```

### 4. API Endpoints

**File**: `lukhas/api/endpoints/guardian_rollout.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from lukhas.governance.rollout_manager import RolloutManager
from lukhas.identity.auth import require_admin

router = APIRouter(prefix="/api/guardian/rollout", tags=["Guardian Rollout"])


class RolloutStatusResponse(BaseModel):
    """Rollout status response."""
    current_stage: dict
    stage_index: int
    total_stages: int
    elapsed_time: str | None
    min_duration: str
    started_at: str | None


class AdvanceResponse(BaseModel):
    """Rollout advancement response."""
    success: bool
    message: str
    new_stage: str
    new_percentage: int


@router.get("/status", response_model=RolloutStatusResponse)
async def get_rollout_status(
    manager: RolloutManager = Depends()
) -> RolloutStatusResponse:
    """Get current rollout status."""
    status = manager.get_status()
    return RolloutStatusResponse(**status)


@router.post("/advance", response_model=AdvanceResponse)
async def manual_advance(
    manager: RolloutManager = Depends(),
    user=Depends(require_admin)
) -> AdvanceResponse:
    """Manually advance to next stage (requires admin)."""
    success, message = manager.manual_advance()

    if not success:
        raise HTTPException(status_code=400, detail=message)

    new_stage = manager.config.current_stage()

    return AdvanceResponse(
        success=True,
        message=message,
        new_stage=new_stage.name,
        new_percentage=new_stage.percentage
    )


@router.post("/rollback", response_model=AdvanceResponse)
async def manual_rollback(
    manager: RolloutManager = Depends(),
    user=Depends(require_admin)
) -> AdvanceResponse:
    """Manually rollback to previous stage (requires admin)."""
    old_stage = manager.config.current_stage()
    manager.rollback()
    new_stage = manager.config.current_stage()

    return AdvanceResponse(
        success=True,
        message=f"Rolled back from {old_stage.name} to {new_stage.name}",
        new_stage=new_stage.name,
        new_percentage=new_stage.percentage
    )
```

### 5. GitHub Actions Workflow

**File**: `.github/workflows/guardian-rollout-check.yml`

```yaml
name: Guardian Rollout Check

on:
  schedule:
    # Check rollout status every 30 minutes
    - cron: '*/30 * * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  check-rollout:
    runs-on: ubuntu-latest
    steps:
      - name: Check rollout status
        run: |
          # Query rollout API
          STATUS=$(curl -s https://api.lukhas.ai/api/guardian/rollout/status)

          echo "Current rollout status:"
          echo "$STATUS" | jq .

          # Extract current stage
          STAGE=$(echo "$STATUS" | jq -r '.current_stage.name')
          PERCENTAGE=$(echo "$STATUS" | jq -r '.current_stage.percentage')
          REQUIRES_APPROVAL=$(echo "$STATUS" | jq -r '.current_stage.requires_approval')

          echo "Stage: $STAGE ($PERCENTAGE%)"

          # Alert if stage requires approval
          if [ "$REQUIRES_APPROVAL" = "true" ]; then
            echo "⚠️ Stage $STAGE requires manual approval!"
            echo "::warning::Guardian rollout stage $STAGE requires human approval"
          fi

      - name: Notify on stage change
        if: success()
        uses: 8398a7/action-slack@v3
        with:
          status: custom
          text: |
            Guardian Rollout Status Check
            Stage: ${{ env.STAGE }} (${{ env.PERCENTAGE }}%)
            Requires Approval: ${{ env.REQUIRES_APPROVAL }}
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Testing Requirements

### 1. Unit Tests

**File**: `tests/unit/governance/test_rollout_manager.py`

```python
import pytest
from datetime import datetime, timedelta
from lukhas.governance.rollout_config import RolloutConfig, RolloutStage
from lukhas.governance.rollout_manager import RolloutManager


def test_rollout_config_default():
    """Test default rollout configuration."""
    config = RolloutConfig.default()

    assert len(config.stages) == 5
    assert config.current_stage_index == 0
    assert config.current_stage().percentage == 10  # Canary


def test_rollout_can_advance_duration_not_met():
    """Test cannot advance if minimum duration not met."""
    config = RolloutConfig.default()
    config.current_stage_started_at = datetime.utcnow() - timedelta(hours=1)

    can_advance, reason = config.can_advance(error_rate=0.001)

    assert not can_advance
    assert "duration not met" in reason.lower()


def test_rollout_can_advance_error_rate_exceeded():
    """Test cannot advance if error rate exceeds threshold."""
    config = RolloutConfig.default()
    config.current_stage_started_at = datetime.utcnow() - timedelta(hours=25)

    can_advance, reason = config.can_advance(error_rate=0.01)  # 1% > 0.5%

    assert not can_advance
    assert "error rate" in reason.lower()


def test_rollout_advance():
    """Test advancing to next stage."""
    config = RolloutConfig.default()
    assert config.current_stage().name == "canary"

    config.advance()

    assert config.current_stage().name == "quarter"
    assert config.current_stage().percentage == 25


def test_rollout_rollback():
    """Test rolling back to previous stage."""
    config = RolloutConfig.default()
    config.advance()  # Move to quarter
    assert config.current_stage().name == "quarter"

    config.rollback()

    assert config.current_stage().name == "canary"
    assert config.current_stage().percentage == 10


@pytest.mark.asyncio
async def test_rollout_manager_auto_advance(mock_enforcer, mock_metrics):
    """Test automatic advancement when conditions met."""
    config = RolloutConfig.default()
    config.current_stage_started_at = datetime.utcnow() - timedelta(hours=25)

    manager = RolloutManager(config, mock_enforcer, mock_metrics)

    # Mock low error rate
    async def mock_error_rate(window):
        return 0.001  # 0.1% - below threshold

    manager.get_current_error_rate = mock_error_rate

    advanced, message = await manager.check_and_advance()

    # Should advance from canary (10%) to quarter (25%)
    # But quarter requires approval, so should NOT auto-advance
    assert not advanced
    assert "requires approval" in message.lower()


@pytest.mark.asyncio
async def test_rollout_manager_rollback_on_error(mock_enforcer, mock_metrics):
    """Test automatic rollback when error rate too high."""
    config = RolloutConfig.default()
    config.advance()  # Start at quarter (25%)
    config.current_stage_started_at = datetime.utcnow() - timedelta(hours=1)

    manager = RolloutManager(config, mock_enforcer, mock_metrics)

    # Mock high error rate
    async def mock_error_rate(window):
        return 0.01  # 1% - exceeds threshold

    manager.get_current_error_rate = mock_error_rate

    advanced, message = await manager.check_and_advance()

    # Should rollback to canary
    assert not advanced
    assert "rolled back" in message.lower()
    assert config.current_stage().name == "canary"


def test_manual_advance_requires_approval():
    """Test manual advancement for stages requiring approval."""
    config = RolloutConfig.default()
    manager = RolloutManager(config, mock_enforcer, mock_metrics)

    success, message = manager.manual_advance()

    assert success
    assert config.current_stage().name == "quarter"
```

### 2. Integration Tests

**File**: `tests/integration/governance/test_rollout_integration.py`

```python
import pytest
import asyncio
from datetime import timedelta
from lukhas.governance.rollout_manager import RolloutManager
from lukhas.governance.rollout_config import RolloutConfig


@pytest.mark.asyncio
async def test_full_rollout_cycle(live_enforcer, live_metrics):
    """Test complete rollout from canary to full."""
    config = RolloutConfig.default()

    # Speed up for testing
    for stage in config.stages:
        stage.duration = timedelta(seconds=5)

    manager = RolloutManager(config, live_enforcer, live_metrics)

    # Mock always-low error rate
    async def mock_error_rate(window):
        return 0.0001  # 0.01%

    manager.get_current_error_rate = mock_error_rate

    # Advance through stages
    stages_visited = [config.current_stage().name]

    for i in range(len(config.stages) - 1):
        # Wait for minimum duration
        await asyncio.sleep(6)

        # For stages requiring approval, manually advance
        if config.stages[i + 1].requires_approval:
            success, _ = manager.manual_advance()
            assert success
        else:
            advanced, _ = await manager.check_and_advance()
            if not advanced:
                # Retry once (might need approval)
                manager.manual_advance()

        stages_visited.append(config.current_stage().name)

    # Should have visited all stages
    assert stages_visited == ["canary", "quarter", "half", "most", "full"]
    assert config.current_stage().percentage == 100
```

---

## Acceptance Criteria

- [ ] `RolloutConfig` and `RolloutStage` dataclasses implemented
- [ ] 5-stage rollout (10% → 25% → 50% → 75% → 100%)
- [ ] `RolloutManager` with state persistence to `/tmp/guardian_rollout_state.json`
- [ ] Automatic advancement when conditions met (duration + error rate)
- [ ] Automatic rollback when error rate exceeds threshold
- [ ] Manual advancement API for stages requiring approval
- [ ] Error rate calculation from Prometheus metrics
- [ ] Rollout status API endpoint (`GET /api/guardian/rollout/status`)
- [ ] Manual advance/rollback endpoints (admin-only)
- [ ] Background monitoring loop with 15-minute check interval
- [ ] GitHub Actions workflow for rollout status checks
- [ ] Prometheus metrics: `guardian_rollout_stage`, `guardian_rollout_error_rate`
- [ ] Unit tests for all rollout logic (>90% coverage)
- [ ] Integration tests for full rollout cycle
- [ ] Slack notifications on stage changes and approval requirements

---

## Rollout Plan

### Phase 1: Implementation (Day 1)
1. Implement `RolloutConfig` and `RolloutStage`
2. Implement `RolloutManager` with state persistence
3. Add error rate calculation from Prometheus
4. Implement automatic advancement logic

### Phase 2: API & Monitoring (Day 2)
1. Add API endpoints for status, manual advance, rollback
2. Implement background monitoring loop
3. Add GitHub Actions workflow
4. Add Slack notifications

### Phase 3: Testing (Day 3)
1. Write comprehensive unit tests
2. Write integration tests for full cycle
3. Manual testing with live metrics

### Phase 4: Documentation & Runbook (Day 4)
1. Document rollout procedures in `docs/guardian/ROLLOUT.md`
2. Create runbook for handling rollback scenarios
3. Document manual approval process

---

## Monitoring

### Grafana Dashboard

Add panel to Guardian dashboard:

```promql
# Current rollout stage
guardian_rollout_stage

# Error rate during rollout
guardian_rollout_error_rate

# Stage advancements over time
increase(guardian_rollout_advancement_total[1h])

# Rollbacks over time (should be rare!)
increase(guardian_rollout_rollback_total[1h])
```

### Alerts

```yaml
- alert: GuardianRolloutStuck
  expr: |
    time() - guardian_rollout_stage_started_at > 86400 * 3  # 3 days
  annotations:
    summary: "Guardian rollout has been at stage {{ $labels.stage_name }} for >3 days"

- alert: GuardianRolloutRollback
  expr: |
    increase(guardian_rollout_rollback_total[15m]) > 0
  annotations:
    summary: "Guardian rollout rolled back from {{ $labels.from_stage }}"
```

---

## Documentation Updates

Update the following docs:

1. **docs/guardian/ROLLOUT.md** - Rollout procedures and approval process
2. **docs/governance/README.md** - Add rollout architecture section
3. **docs/operations/RUNBOOKS.md** - Add rollout incident runbook

---

## References

- **Canary Deployment Pattern**: https://martinfowler.com/bliki/CanaryRelease.html
- **Progressive Delivery**: https://www.split.io/glossary/progressive-delivery/
- **Feature Flags Best Practices**: https://launchdarkly.com/blog/dos-and-donts-of-feature-flag-management/

---

**Estimated Completion**: 3-4 days (Medium effort)
**PR Target**: Ready for review within 1 week
**Success Metric**: Zero-downtime rollout to 100% enforcement with <0.5% error increase

