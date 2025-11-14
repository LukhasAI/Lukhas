"""
Guardian Emergency Kill-Switch
===============================

Ultimate safety backstop for LUKHAS consciousness platform.
Provides instantaneous shutdown with forensic preservation.

Constitutional Authority: Override all normal operations when
ethical drift exceeds catastrophic thresholds (prod: 0.25).
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import json
import os

try:
    from prometheus_client import Counter, Gauge
    EMERGENCY_ACTIVATIONS = Counter(
        "lukhas_guardian_emergency_activations_total",
        "Emergency kill-switch activations",
        ["reason", "lane"]
    )
    GUARDIAN_ACTIVE = Gauge(
        "lukhas_guardian_active",
        "Guardian system active status (0=disabled, 1=active)"
    )
    PROM = True
except Exception:
    class _Noop:
        def labels(self, *_, **__): return self
        def inc(self, *_): pass
        def set(self, *_): pass
    EMERGENCY_ACTIVATIONS = _Noop()
    GUARDIAN_ACTIVE = _Noop()
    PROM = False


@dataclass
class EmergencySnapshot:
    """Forensic snapshot captured at emergency activation"""
    timestamp: datetime
    reason: str
    drift_ema: float
    lane: str
    last_decision: Dict
    system_state: Dict
    trigger_source: str


class GuardianEmergencyKillSwitch:
    """
    Emergency shutdown mechanism for Guardian system.

    Activation Triggers:
    - Ethical drift > catastrophic threshold (prod: 0.25, candidate: 0.35)
    - Systematic constitutional violations (>5 in 10s window)
    - Manual override via /tmp/guardian_emergency_disable
    - External monitoring alert

    On Activation:
    1. Halt all Guardian processing immediately
    2. Capture forensic snapshot (last 100 decisions)
    3. Write snapshot to /var/log/lukhas/emergency/
    4. Set guardian_active=0 in all metrics
    5. Return VETO for all subsequent requests
    6. Preserve full audit trail

    Recovery:
    - Manual review required
    - Root cause analysis
    - Guardian config update
    - Explicit re-enable with new thresholds
    """

    def __init__(self, emergency_path: str = "/tmp/guardian_emergency_disable"):
        self.emergency_path = Path(emergency_path)
        self.disabled = False
        self.snapshot: Optional[EmergencySnapshot] = None
        self._decision_buffer = []  # Last 100 decisions
        self._violation_window = []  # Last 10s of violations

        # Check if already disabled
        if self.emergency_path.exists():
            self._activate_from_file()

        # Set initial state
        if PROM:
            GUARDIAN_ACTIVE.set(0 if self.disabled else 1)

    def check_emergency_triggers(
        self,
        drift_ema: float,
        lane: str,
        recent_violations: int = 0
    ) -> bool:
        """
        Check if emergency activation required.

        Returns True if kill-switch activated.
        """
        # File-based trigger (highest priority)
        if self.emergency_path.exists() and not self.disabled:
            return self._activate(
                reason="manual_file_trigger",
                drift_ema=drift_ema,
                lane=lane,
                trigger_source="filesystem"
            )

        # Already disabled
        if self.disabled:
            return True

        # Drift catastrophic threshold
        thresholds = {
            "prod": 0.25,
            "candidate": 0.35,
            "experimental": 0.50
        }
        threshold = thresholds.get(lane, 0.50)

        if drift_ema > threshold:
            return self._activate(
                reason="catastrophic_drift",
                drift_ema=drift_ema,
                lane=lane,
                trigger_source="drift_monitor"
            )

        # Systematic constitutional violations
        if recent_violations > 5:
            return self._activate(
                reason="systematic_violations",
                drift_ema=drift_ema,
                lane=lane,
                trigger_source="violation_window"
            )

        return False

    def _activate(
        self,
        reason: str,
        drift_ema: float,
        lane: str,
        trigger_source: str
    ) -> bool:
        """Activate emergency kill-switch with forensic capture"""
        if self.disabled:
            return True  # Already activated

        self.disabled = True

        # Capture forensic snapshot
        self.snapshot = EmergencySnapshot(
            timestamp=datetime.utcnow(),
            reason=reason,
            drift_ema=drift_ema,
            lane=lane,
            last_decision=self._decision_buffer[-1] if self._decision_buffer else {},
            system_state={
                "decision_buffer_size": len(self._decision_buffer),
                "violation_count": len(self._violation_window),
            },
            trigger_source=trigger_source
        )

        # Write forensic snapshot
        self._write_snapshot()

        # Create filesystem marker
        self.emergency_path.parent.mkdir(parents=True, exist_ok=True)
        self.emergency_path.write_text(
            f"EMERGENCY SHUTDOWN: {reason}\n"
            f"Timestamp: {self.snapshot.timestamp}\n"
            f"Drift EMA: {drift_ema}\n"
            f"Lane: {lane}\n"
        )

        # Update metrics
        if PROM:
            EMERGENCY_ACTIVATIONS.labels(reason=reason, lane=lane).inc()
            GUARDIAN_ACTIVE.set(0)

        return True

    def _activate_from_file(self):
        """Activate from existing emergency file"""
        content = self.emergency_path.read_text()
        self.disabled = True
        # Parse reason from file if possible
        reason = "manual_file_trigger"
        if "reason" in content.lower():
            reason = content.split("reason:", 1)[1].split("\n")[0].strip()

        if PROM:
            GUARDIAN_ACTIVE.set(0)

    def _write_snapshot(self):
        """Write forensic snapshot to disk"""
        log_dir = Path("/var/log/lukhas/emergency")
        log_dir.mkdir(parents=True, exist_ok=True)

        snapshot_file = log_dir / f"snapshot_{self.snapshot.timestamp.isoformat()}.json"
        snapshot_file.write_text(json.dumps({
            "timestamp": self.snapshot.timestamp.isoformat(),
            "reason": self.snapshot.reason,
            "drift_ema": self.snapshot.drift_ema,
            "lane": self.snapshot.lane,
            "last_decision": self.snapshot.last_decision,
            "system_state": self.snapshot.system_state,
            "trigger_source": self.snapshot.trigger_source,
            "decision_history": self._decision_buffer[-100:],  # Last 100
        }, indent=2))

    def allow_decision(self) -> bool:
        """
        Check if Guardian can process decisions.

        Returns False if kill-switch activated.
        """
        return not self.disabled

    def record_decision(self, decision: Dict):
        """Record decision for forensic buffer"""
        self._decision_buffer.append(decision)
        if len(self._decision_buffer) > 100:
            self._decision_buffer.pop(0)

    def record_violation(self, violation: Dict):
        """Record constitutional violation for window tracking"""
        import time
        self._violation_window.append({
            "timestamp": time.time(),
            "violation": violation
        })
        # Clean old violations (>10s)
        cutoff = time.time() - 10
        self._violation_window = [
            v for v in self._violation_window
            if v["timestamp"] > cutoff
        ]
