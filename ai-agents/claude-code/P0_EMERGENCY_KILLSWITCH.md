# Claude Code Task: Guardian Emergency Kill-Switch (SG002)

**Task ID**: SG002
**Priority**: P0 (Critical)
**Effort**: Small (<4 hours)
**Owner**: claude-code
**Branch**: `feat/guardian-emergency-killswitch`

---

## Objective

Implement a **fast emergency kill-switch** for Guardian DSL enforcement that bypasses all normal configuration and immediately disables enforcement when a flag file exists.

---

## Context

In production emergencies (e.g., Guardian enforcement causing cascading failures), we need:
1. **Instant disable** - No config reloads, no API calls, just check file existence
2. **File-based** - Use `/tmp/guardian_emergency_disable` flag file
3. **Bypass all enforcement** - Even if canary/rollout says enforce, check this first
4. **Metrics tracking** - Record when emergency mode is active
5. **Auto-recovery** - System resumes when file removed

**Safety**: This is a last-resort mechanism for true emergencies only.

---

## Implementation Requirements

### 1. Emergency Kill-Switch Check

**File**: `lukhas/governance/guardian_enforcer.py`

Modify the `should_enforce()` method to check emergency flag FIRST:

```python
from pathlib import Path


class GuardianEnforcer:
    """Guardian DSL enforcement with emergency kill-switch."""

    EMERGENCY_DISABLE_FILE = Path("/tmp/guardian_emergency_disable")

    def __init__(self, config: GuardianConfig):
        self.config = config
        self._emergency_mode_logged = False

    def should_enforce(self, request_id: Optional[str] = None) -> bool:
        """
        Determine if Guardian enforcement should apply.

        Priority (highest to lowest):
        1. Emergency disable file (ALWAYS bypass if exists)
        2. Global enabled flag
        3. Canary sampling

        Returns:
            bool: True if enforcement should apply, False otherwise
        """
        # PRIORITY 1: Check emergency disable flag (FASTEST PATH)
        if self._is_emergency_disabled():
            if not self._emergency_mode_logged:
                logger.critical(
                    "🚨 GUARDIAN EMERGENCY MODE ACTIVE - Enforcement disabled via flag file"
                )
                self._emergency_mode_logged = True

            # Record metric
            self._record_emergency_metric()

            return False  # Bypass ALL enforcement

        # Reset emergency log flag when file removed
        if self._emergency_mode_logged:
            logger.info("Guardian emergency mode cleared - resuming normal enforcement")
            self._emergency_mode_logged = False

        # PRIORITY 2: Check global enabled flag
        if not self.config.enabled:
            return False

        # PRIORITY 3: Check canary sampling
        if not self.config.canary_enabled:
            return True  # Full enforcement

        # Hash-based sampling for consistency
        if request_id:
            sample = hash(request_id) % 100
            return sample < self.config.canary_percentage

        # No request_id = enforce (conservative)
        return True

    def _is_emergency_disabled(self) -> bool:
        """
        Check if emergency disable flag file exists.

        This is intentionally simple and fast:
        - No caching (always check file system)
        - No config overrides
        - No network calls

        Returns:
            bool: True if emergency file exists
        """
        return self.EMERGENCY_DISABLE_FILE.exists()

    def _record_emergency_metric(self) -> None:
        """Record that emergency mode is active."""
        try:
            from lukhas.monitoring.metrics import get_metrics_client

            metrics = get_metrics_client()
            metrics.gauge("guardian_emergency_mode_active", 1)

        except Exception as e:
            # Never fail enforcement check due to metrics error
            logger.warning(f"Failed to record emergency metric: {e}")

    def get_status(self) -> dict:
        """Get current Guardian enforcement status."""
        emergency_active = self._is_emergency_disabled()

        return {
            "enabled": self.config.enabled,
            "canary_enabled": self.config.canary_enabled,
            "canary_percentage": self.config.canary_percentage,
            "emergency_disabled": emergency_active,
            "emergency_file": str(self.EMERGENCY_DISABLE_FILE),
            "effective_enforcement": (
                not emergency_active
                and self.config.enabled
            ),
        }
```

### 2. Emergency Disable Script

**File**: `scripts/emergency/disable_guardian.sh`

```bash
#!/bin/bash
# Emergency script to disable Guardian enforcement

set -e

EMERGENCY_FILE="/tmp/guardian_emergency_disable"
LOG_FILE="/var/log/lukhas/guardian_emergency.log"

echo "🚨 GUARDIAN EMERGENCY DISABLE INITIATED"
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "User: ${USER}" | tee -a "$LOG_FILE"
echo "Reason: ${1:-No reason provided}" | tee -a "$LOG_FILE"

# Create emergency flag file
touch "$EMERGENCY_FILE"
chmod 644 "$EMERGENCY_FILE"

echo "✅ Emergency flag created: $EMERGENCY_FILE"
echo "Guardian enforcement is NOW DISABLED"
echo ""
echo "To re-enable Guardian, run:"
echo "  scripts/emergency/enable_guardian.sh"
echo ""
echo "⚠️  IMPORTANT: This is a temporary emergency measure."
echo "   Investigate and fix the root cause before re-enabling."
```

**File**: `scripts/emergency/enable_guardian.sh`

```bash
#!/bin/bash
# Re-enable Guardian enforcement after emergency

set -e

EMERGENCY_FILE="/tmp/guardian_emergency_disable"
LOG_FILE="/var/log/lukhas/guardian_emergency.log"

if [ ! -f "$EMERGENCY_FILE" ]; then
    echo "⚠️  Emergency flag file not found. Guardian may already be enabled."
    exit 1
fi

echo "Re-enabling Guardian enforcement..."
echo "Timestamp: $(date -Iseconds)" | tee -a "$LOG_FILE"
echo "User: ${USER}" | tee -a "$LOG_FILE"

# Remove emergency flag file
rm -f "$EMERGENCY_FILE"

echo "✅ Emergency flag removed: $EMERGENCY_FILE"
echo "Guardian enforcement is NOW ENABLED"
echo ""
echo "Verify status:"
echo "  curl http://localhost:8000/api/guardian/status"
```

### 3. Status API Endpoint

**File**: `lukhas/api/endpoints/guardian.py`

Add emergency status to the Guardian status endpoint:

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from lukhas.governance.guardian_enforcer import GuardianEnforcer

router = APIRouter(prefix="/api/guardian", tags=["Guardian"])


class GuardianStatusResponse(BaseModel):
    """Guardian status response."""
    enabled: bool
    canary_enabled: bool
    canary_percentage: int
    emergency_disabled: bool
    emergency_file: str
    effective_enforcement: bool


@router.get("/status", response_model=GuardianStatusResponse)
async def get_guardian_status(
    enforcer: GuardianEnforcer
) -> GuardianStatusResponse:
    """
    Get current Guardian enforcement status.

    Returns enforcement configuration including emergency disable flag.
    """
    status = enforcer.get_status()
    return GuardianStatusResponse(**status)


@router.get("/emergency/check")
async def check_emergency_mode(
    enforcer: GuardianEnforcer
) -> dict:
    """
    Quick check if emergency mode is active.

    This is a lightweight endpoint for monitoring.
    """
    emergency_active = enforcer._is_emergency_disabled()

    return {
        "emergency_active": emergency_active,
        "enforcement_active": not emergency_active and enforcer.config.enabled,
        "timestamp": datetime.utcnow().isoformat(),
    }
```

### 4. Prometheus Metrics

**File**: `lukhas/monitoring/guardian_metrics.py`

```python
from prometheus_client import Gauge

# Emergency mode gauge (1 = active, 0 = inactive)
guardian_emergency_mode_active = Gauge(
    "guardian_emergency_mode_active",
    "Whether Guardian emergency disable is active (1 = disabled, 0 = normal)"
)


def update_emergency_metric(enforcer: GuardianEnforcer) -> None:
    """Update emergency mode metric."""
    emergency_active = enforcer._is_emergency_disabled()
    guardian_emergency_mode_active.set(1 if emergency_active else 0)
```

### 5. Health Check Integration

**File**: `lukhas/api/endpoints/health.py`

Add emergency mode to health check:

```python
@router.get("/health")
async def health_check(enforcer: GuardianEnforcer) -> dict:
    """System health check including Guardian status."""
    emergency_active = enforcer._is_emergency_disabled()

    return {
        "status": "degraded" if emergency_active else "healthy",
        "guardian": {
            "emergency_mode": emergency_active,
            "enforcement_active": not emergency_active and enforcer.config.enabled,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
```

---

## Testing Requirements

### 1. Unit Tests

**File**: `tests/unit/governance/test_guardian_emergency.py`

```python
import pytest
from pathlib import Path
from lukhas.governance.guardian_enforcer import GuardianEnforcer, GuardianConfig


@pytest.fixture
def emergency_file(tmp_path):
    """Use temporary emergency file for tests."""
    test_file = tmp_path / "guardian_emergency_disable"
    # Monkey-patch the class constant
    original = GuardianEnforcer.EMERGENCY_DISABLE_FILE
    GuardianEnforcer.EMERGENCY_DISABLE_FILE = test_file
    yield test_file
    GuardianEnforcer.EMERGENCY_DISABLE_FILE = original


def test_emergency_disable_bypasses_all_config(emergency_file):
    """Test emergency file bypasses all configuration."""
    config = GuardianConfig(
        enabled=True,
        canary_enabled=True,
        canary_percentage=100  # Full enforcement
    )
    enforcer = GuardianEnforcer(config)

    # Create emergency flag
    emergency_file.touch()

    # Should NOT enforce despite config saying 100%
    assert not enforcer.should_enforce()
    assert not enforcer.should_enforce(request_id="test-123")


def test_emergency_disable_cleared(emergency_file):
    """Test enforcement resumes when emergency file removed."""
    config = GuardianConfig(
        enabled=True,
        canary_enabled=False  # Full enforcement
    )
    enforcer = GuardianEnforcer(config)

    # Create emergency flag
    emergency_file.touch()
    assert not enforcer.should_enforce()

    # Remove emergency flag
    emergency_file.unlink()

    # Should enforce now
    assert enforcer.should_enforce()


def test_emergency_status_in_get_status(emergency_file):
    """Test emergency status included in get_status()."""
    config = GuardianConfig(enabled=True)
    enforcer = GuardianEnforcer(config)

    # No emergency
    status = enforcer.get_status()
    assert not status["emergency_disabled"]
    assert status["effective_enforcement"]

    # With emergency
    emergency_file.touch()
    status = enforcer.get_status()
    assert status["emergency_disabled"]
    assert not status["effective_enforcement"]


def test_emergency_check_is_fast(emergency_file, benchmark):
    """Test emergency check is very fast (<1ms)."""
    config = GuardianConfig(enabled=True)
    enforcer = GuardianEnforcer(config)

    # Benchmark emergency check
    result = benchmark(enforcer._is_emergency_disabled)

    # Should be <1ms (very fast file check)
    assert benchmark.stats.mean < 0.001  # <1ms


def test_emergency_metric_recorded(emergency_file, mock_metrics):
    """Test emergency mode records metric."""
    config = GuardianConfig(enabled=True)
    enforcer = GuardianEnforcer(config)

    emergency_file.touch()

    # Should record metric
    enforcer.should_enforce()

    # Verify metric call
    assert mock_metrics.gauge.called
    assert mock_metrics.gauge.call_args[0] == ("guardian_emergency_mode_active", 1)


def test_emergency_logging_only_once():
    """Test emergency mode only logs critical message once."""
    config = GuardianConfig(enabled=True)
    enforcer = GuardianEnforcer(config)

    with patch('lukhas.governance.guardian_enforcer.logger') as mock_logger:
        emergency_file.touch()

        # First call - should log
        enforcer.should_enforce()
        assert mock_logger.critical.call_count == 1

        # Second call - should NOT log again
        enforcer.should_enforce()
        assert mock_logger.critical.call_count == 1  # Still 1

        # Remove file
        emergency_file.unlink()

        # Should log recovery
        enforcer.should_enforce()
        assert mock_logger.info.call_count == 1
```

### 2. Integration Tests

**File**: `tests/integration/governance/test_guardian_emergency_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from lukhas.api.app import app


@pytest.fixture
def emergency_file(tmp_path):
    """Use temporary emergency file."""
    test_file = tmp_path / "guardian_emergency_disable"
    GuardianEnforcer.EMERGENCY_DISABLE_FILE = test_file
    yield test_file


def test_emergency_mode_via_api(emergency_file):
    """Test emergency mode visible via API."""
    client = TestClient(app)

    # Normal mode
    response = client.get("/api/guardian/status")
    assert response.status_code == 200
    assert not response.json()["emergency_disabled"]

    # Emergency mode
    emergency_file.touch()
    response = client.get("/api/guardian/status")
    assert response.status_code == 200
    assert response.json()["emergency_disabled"]
    assert not response.json()["effective_enforcement"]


def test_health_check_degraded_in_emergency(emergency_file):
    """Test health check shows degraded when emergency active."""
    client = TestClient(app)

    emergency_file.touch()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["guardian"]["emergency_mode"]


def test_emergency_scripts(tmp_path):
    """Test emergency enable/disable scripts work."""
    import subprocess

    emergency_file = tmp_path / "guardian_emergency_disable"

    # Set env var for script
    env = {"EMERGENCY_FILE": str(emergency_file)}

    # Run disable script
    result = subprocess.run(
        ["scripts/emergency/disable_guardian.sh", "Integration test"],
        env=env,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert emergency_file.exists()

    # Run enable script
    result = subprocess.run(
        ["scripts/emergency/enable_guardian.sh"],
        env=env,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert not emergency_file.exists()
```

---

## Acceptance Criteria

- [ ] Emergency file check in `GuardianEnforcer.should_enforce()` (FIRST priority)
- [ ] Emergency flag file: `/tmp/guardian_emergency_disable`
- [ ] Emergency disable script: `scripts/emergency/disable_guardian.sh`
- [ ] Emergency enable script: `scripts/emergency/enable_guardian.sh`
- [ ] Emergency status in `GET /api/guardian/status`
- [ ] Emergency check endpoint: `GET /api/guardian/emergency/check`
- [ ] Health check shows "degraded" when emergency active
- [ ] Prometheus metric: `guardian_emergency_mode_active` (gauge)
- [ ] Emergency mode logs critical message (once per activation)
- [ ] Recovery logs info message when file removed
- [ ] Unit tests for emergency flag logic (>95% coverage)
- [ ] Integration tests for API endpoints
- [ ] Performance test: emergency check <1ms
- [ ] Scripts are executable: `chmod +x scripts/emergency/*.sh`

---

## Operational Runbook

### Emergency Disable Procedure

**When to use**: Guardian enforcement causing production incidents (cascading failures, widespread errors)

```bash
# 1. Immediately disable Guardian
ssh production-server
sudo scripts/emergency/disable_guardian.sh "Incident #1234: Cascading failures"

# 2. Verify disabled
curl http://localhost:8000/api/guardian/status | jq .emergency_disabled
# Should return: true

# 3. Monitor recovery
watch -n 5 'curl -s http://localhost:8000/health | jq .'

# 4. Investigate root cause
# ... fix the issue ...

# 5. Re-enable Guardian (after fix confirmed)
sudo scripts/emergency/enable_guardian.sh

# 6. Verify enabled
curl http://localhost:8000/api/guardian/status | jq .effective_enforcement
# Should return: true
```

### Monitoring Emergency Mode

**Grafana Alert**:
```promql
guardian_emergency_mode_active == 1
```

Alert annotation: "Guardian emergency mode active - enforcement disabled!"

---

## Documentation Updates

1. **docs/guardian/EMERGENCY.md** - Complete emergency procedures runbook
2. **docs/operations/INCIDENTS.md** - Add Guardian emergency to incident response
3. **README.md** - Add note about emergency scripts location

---

## References

- **Circuit Breaker Pattern**: https://martinfowler.com/bliki/CircuitBreaker.html
- **Kill Switch Design**: https://landing.google.com/sre/sre-book/chapters/addressing-cascading-failures/

---

**Estimated Completion**: 2-3 hours (Small effort)
**PR Target**: Ready for review within 1 day
**Critical Path**: This is P0 - must be in place before Guardian rollout

