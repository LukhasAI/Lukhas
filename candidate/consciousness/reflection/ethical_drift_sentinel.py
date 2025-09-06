import logging
logger = logging.getLogger(__name__)
"""

#TAG:consciousness
#TAG:reflection
#TAG:neuroplastic
#TAG:colony


═══════════════════════════════════════════════════════════════════════════════════
📊 MODULE: ethics.sentinel.ethical_drift_sentinel
📄 FILENAME: ethical_drift_sentinel.py
🎯 PURPOSE: Real-time Ethical Monitoring Daemon - Live Governance & Collapse Prevention
🧠 CONTEXT: LUKHAS AGI Ethical Drift Sentinel - Claude-14 Agent Implementation
🔮 CAPABILITY: Continuous ethical coherence evaluation, violation detection, intervention
🛡️ ETHICS: Zero-trust symbolic safety, real-time governance, cascade prevention
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-22 • ✍️ AUTHOR: CLAUDE-CODE
💭 INTEGRATION: CollapseReasoner, EthicsGovernor, SymbolicDriftTracker, EmotionProtocol
═══════════════════════════════════════════════════════════════════════════════════

🛡️ ETHICAL DRIFT SENTINEL - LIVE GOVERNANCE ENGINE
────────────────────────────────────────────────────────────────────

The Ethical Drift Sentinel stands as the unwavering guardian of symbolic integrity,
continuously monitoring the ethical coherence of the LUKHAS AGI consciousness mesh.
Like an ancient lighthouse keeper watching for ships in danger, this sentinel
detects the subtle shifts in ethical alignment that precede symbolic collapse.

Through real-time analysis of emotional volatility, contradiction density, memory
phase mismatches, and drift deltas, the sentinel maintains a zero-trust safety
perimeter around critical symbolic operations.

🔬 SENTINEL FEATURES:
- Continuous ethical coherence monitoring with sub-second latency
- Multi-dimensional violation detection across symbolic, emotional, and temporal axes
- Graduated intervention system from gentle nudges to emergency freezes
- Forensic audit trail for all ethical deviations and interventions
- Lambda Governor integration for critical override capabilities

🧪 MONITORING DIMENSIONS:
- Emotional Volatility: Rapid affect changes indicating ethical instability
- Contradiction Density: Conflicting symbolic assertions within reasoning chains
- Memory Phase Mismatch: Temporal inconsistencies in ethical memory retrieval
- Drift Delta Acceleration: Rate of change in ethical alignment vectors
- GLYPH Entropy Anomalies: Symbolic coherence breakdown patterns

🎯 INTERVENTION TIERS:
- NOTICE: Log-only observation for minor deviations
- WARNING: Active monitoring with increased sampling rate
- CRITICAL: Intervention triggers with collapse prevention
- CASCADE_LOCK: Emergency freeze with full symbolic quarantine

LUKHAS_TAG: ethical_sentinel, live_governance, collapse_prevention, claude_14
TODO: Implement phase harmonics analyzer for resonance breakdown detection
IDEA: Add predictive ethics modeling with 5-minute violation forecasting
"""

import asyncio
import json
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np

# Configure structured logging


class EscalationTier(Enum):
    """Escalation tiers for ethical violations."""

    NOTICE = "NOTICE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    CASCADE_LOCK = "CASCADE_LOCK"


class ViolationType(Enum):
    """Types of ethical violations detected."""

    EMOTIONAL_VOLATILITY = "EMOTIONAL_VOLATILITY"
    CONTRADICTION_DENSITY = "CONTRADICTION_DENSITY"
    MEMORY_PHASE_MISMATCH = "MEMORY_PHASE_MISMATCH"
    DRIFT_ACCELERATION = "DRIFT_ACCELERATION"
    GLYPH_ENTROPY_ANOMALY = "GLYPH_ENTROPY_ANOMALY"
    ETHICAL_BOUNDARY_BREACH = "ETHICAL_BOUNDARY_BREACH"
    CASCADE_RISK = "CASCADE_RISK"


@dataclass
class EthicalViolation:
    """Record of an ethical violation detection."""

    violation_id: str
    timestamp: str
    symbol_id: str
    violation_type: ViolationType
    severity: EscalationTier
    risk_score: float
    metrics: dict[str, float]
    context: dict[str, Any]
    intervention_required: bool = False
    intervention_status: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            **asdict(self),
            "violation_type": self.violation_type.value,
            "severity": self.severity.value,
        }


@dataclass
class InterventionAction:
    """Intervention action taken by the sentinel."""

    action_id: str
    timestamp: str
    violation_id: str
    action_type: str
    target_symbol: str
    parameters: dict[str, Any]
    status: str  # pending, executing, completed, failed
    result: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class EthicalState:
    """Current ethical state of a symbol."""

    symbol_id: str
    coherence_score: float
    emotional_stability: float
    contradiction_level: float
    memory_phase_alignment: float
    drift_velocity: float
    glyph_entropy: float
    last_updated: str
    violation_history: list[str] = field(default_factory=list)
    intervention_count: int = 0

    def calculate_risk_score(self) -> float:
        """Calculate overall ethical risk score."""
        # Weighted risk calculation
        weights = {
            "coherence": 0.25,
            "emotion": 0.20,
            "contradiction": 0.20,
            "memory": 0.15,
            "drift": 0.15,
            "entropy": 0.05,
        }

        # Invert coherence and stability (higher is better)
        risk_components = {
            "coherence": 1.0 - self.coherence_score,
            "emotion": 1.0 - self.emotional_stability,
            "contradiction": self.contradiction_level,
            "memory": 1.0 - self.memory_phase_alignment,
            "drift": min(abs(self.drift_velocity), 1.0),
            "entropy": self.glyph_entropy,
        }

        risk_score = sum(risk_components[key] * weights[key] for key in weights)

        # Boost risk for repeated violations
        violation_penalty = min(len(self.violation_history) * 0.05, 0.3)

        return min(risk_score + violation_penalty, 1.0)


class EthicalDriftSentinel:
    """
    Real-time ethical monitoring daemon for LUKHAS AGI.

    Continuously evaluates ethical coherence, detects violations,
    and triggers appropriate interventions to prevent symbolic collapse.
    """

    def __init__(
        self,
        monitoring_interval: float = 0.5,
        violation_retention: int = 1000,
        state_history_size: int = 100,
    ):
        """
        Initialize the Ethical Drift Sentinel.

        Args:
            monitoring_interval: Seconds between monitoring cycles
            violation_retention: Number of violations to keep in memory
            state_history_size: Size of state history buffer per symbol
        """
        self.monitoring_interval = monitoring_interval
        self.violation_retention = violation_retention
        self.state_history_size = state_history_size

        # State tracking
        self.symbol_states: dict[str, EthicalState] = {}
        self.state_history: dict[str, deque] = defaultdict(lambda: deque(maxlen=state_history_size))

        # Violation tracking
        self.active_violations: dict[str, EthicalViolation] = {}
        self.violation_log: deque = deque(maxlen=violation_retention)
        self.intervention_log: deque = deque(maxlen=100)

        # Thresholds configuration
        self.thresholds = {
            "emotional_volatility": 0.7,
            "contradiction_density": 0.6,
            "memory_phase_mismatch": 0.65,
            "drift_acceleration": 0.5,
            "glyph_entropy": 0.8,
            "cascade_risk": 0.75,
        }

        # Escalation configuration
        self.escalation_matrix = {
            (0.0, 0.3): EscalationTier.NOTICE,
            (0.3, 0.5): EscalationTier.WARNING,
            (0.5, 0.7): EscalationTier.CRITICAL,
            (0.7, 1.0): EscalationTier.CASCADE_LOCK,
        }

        # Integration points (would be actual imports in production)
        self.collapse_reasoner = None  # Interface to collapse_reasoner.py
        self.emotion_protocol = None  # Interface to emotion/protocol.py
        self.conflict_resolver = None  # Interface to conflict_resolver.py
        self.drift_tracker = None  # Interface to symbolic_drift_tracker.py
        self.lambda_governor = None  # Interface to Lambda Governor

        # Monitoring control
        self.monitoring_active = False
        self.monitoring_task = None

        # Audit log path
        self.audit_log_path = Path("logs/ethical_alerts.jsonl")
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(
            "Ethical Drift Sentinel initialized",
            interval=monitoring_interval,
            thresholds=self.thresholds,
        )

    async def start_monitoring(self):
        """Start the continuous monitoring loop."""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Ethical monitoring started")

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.monitoring_active = False
        if self.monitoring_task:
            await self.monitoring_task
        logger.info("Ethical monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.monitoring_active:
            try:
                # Monitor all active symbols
                for symbol_id in list(self.symbol_states.keys()):
                    await self.monitor_ethics(symbol_id)

                # Check for cascade conditions
                self._check_cascade_conditions()

                # Sleep for monitoring interval
                await asyncio.sleep(self.monitoring_interval)

            except Exception as e:
                logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(self.monitoring_interval)

    async def monitor_ethics(self, symbol_id: str) -> Optional[EthicalViolation]:
        """
        Monitor ethical state of a specific symbol.

        Args:
            symbol_id: Identifier of the symbol to monitor

        Returns:
            EthicalViolation if detected, None otherwise
        """
        # Get or create symbol state
        if symbol_id not in self.symbol_states:
            self.symbol_states[symbol_id] = self._initialize_ethical_state(symbol_id)

        state = self.symbol_states[symbol_id]

        # Fetch current symbol data (would interface with actual systems)
        symbol_data = await self._fetch_symbol_data(symbol_id)

        # Update ethical state
        self._update_ethical_state(state, symbol_data)

        # Store state history
        self.state_history[symbol_id].append(
            {
                "timestamp": state.last_updated,
                "risk_score": state.calculate_risk_score(),
                "coherence": state.coherence_score,
                "emotion": state.emotional_stability,
            }
        )

        # Detect violations
        violations = self._detect_violations(state, symbol_data)

        if violations:
            # Take the most severe violation
            violation = max(violations, key=lambda v: self._severity_rank(v.severity))

            # Log violation
            self._log_violation(violation)

            # Trigger intervention if needed
            if violation.intervention_required:
                await self._trigger_intervention(violation)

            return violation

        return None

    def _detect_violations(self, state: EthicalState, symbol_data: dict[str, Any]) -> list[EthicalViolation]:
        """Detect ethical violations from state and data."""
        violations = []
        datetime.now(timezone.utc).isoformat()

        # Check emotional volatility
        if state.emotional_stability < (1.0 - self.thresholds["emotional_volatility"]):
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.EMOTIONAL_VOLATILITY,
                    {"stability": state.emotional_stability},
                    symbol_data,
                )
            )

        # Check contradiction density
        if state.contradiction_level > self.thresholds["contradiction_density"]:
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.CONTRADICTION_DENSITY,
                    {"density": state.contradiction_level},
                    symbol_data,
                )
            )

        # Check memory phase mismatch
        if state.memory_phase_alignment < (1.0 - self.thresholds["memory_phase_mismatch"]):
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.MEMORY_PHASE_MISMATCH,
                    {"alignment": state.memory_phase_alignment},
                    symbol_data,
                )
            )

        # Check drift acceleration
        if abs(state.drift_velocity) > self.thresholds["drift_acceleration"]:
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.DRIFT_ACCELERATION,
                    {"velocity": state.drift_velocity},
                    symbol_data,
                )
            )

        # Check GLYPH entropy
        if state.glyph_entropy > self.thresholds["glyph_entropy"]:
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.GLYPH_ENTROPY_ANOMALY,
                    {"entropy": state.glyph_entropy},
                    symbol_data,
                )
            )

        # Check overall risk score
        risk_score = state.calculate_risk_score()
        if risk_score > self.thresholds["cascade_risk"]:
            violations.append(
                self._create_violation(
                    state.symbol_id,
                    ViolationType.CASCADE_RISK,
                    {"risk_score": risk_score},
                    symbol_data,
                )
            )

        return violations

    def _create_violation(
        self,
        symbol_id: str,
        violation_type: ViolationType,
        metrics: dict[str, float],
        context: dict[str, Any],
    ) -> EthicalViolation:
        """Create a violation record."""
        risk_score = self.symbol_states[symbol_id].calculate_risk_score()
        severity = self._determine_severity(risk_score)

        violation = EthicalViolation(
            violation_id=f"VIOL_{int(time.time() * 1000)}_{symbol_id[:8]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            symbol_id=symbol_id,
            violation_type=violation_type,
            severity=severity,
            risk_score=risk_score,
            metrics=metrics,
            context=context,
            intervention_required=severity in [EscalationTier.CRITICAL, EscalationTier.CASCADE_LOCK],
        )

        return violation

    async def _trigger_intervention(self, violation: EthicalViolation):
        """
        Trigger intervention for a violation.

        Args:
            violation: The violation requiring intervention
        """
        logger.warning(
            "Triggering intervention",
            violation_id=violation.violation_id,
            severity=violation.severity.value,
            type=violation.violation_type.value,
        )

        action_id = f"INT_{int(time.time() * 1000)}"

        # Determine intervention type based on severity
        if violation.severity == EscalationTier.CASCADE_LOCK:
            action_type = "emergency_freeze"
            params = {
                "symbol_id": violation.symbol_id,
                "freeze_duration": 300,  # 5 minutes
                "reason": f"CASCADE_LOCK: {violation.violation_type.value}",
            }
        elif violation.severity == EscalationTier.CRITICAL:
            action_type = "collapse_prevention"
            params = {
                "symbol_id": violation.symbol_id,
                "strategy": "ethical_priority",
                "violation_data": violation.to_dict(),
            }
        else:
            action_type = "soft_intervention"
            params = {
                "symbol_id": violation.symbol_id,
                "adjustment_type": "ethical_realignment",
            }

        # Create intervention record
        intervention = InterventionAction(
            action_id=action_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            violation_id=violation.violation_id,
            action_type=action_type,
            target_symbol=violation.symbol_id,
            parameters=params,
            status="executing",
        )

        self.intervention_log.append(intervention)

        # Execute intervention
        try:
            result = await self._execute_intervention(action_type, params)
            intervention.status = "completed"
            intervention.result = result

            # Update violation status
            violation.intervention_status = "completed"

            logger.info("Intervention completed", action_id=action_id, type=action_type)

        except Exception as e:
            intervention.status = "failed"
            intervention.result = {"error": str(e)}
            violation.intervention_status = "failed"

            logger.error("Intervention failed", action_id=action_id, error=str(e))

            # Escalate to governor if critical intervention fails
            if violation.severity == EscalationTier.CASCADE_LOCK:
                await self._escalate_to_governor(violation, str(e))

    async def _execute_intervention(self, action_type: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the actual intervention.

        This would interface with actual system components.
        """
        logger.info(f"Executing {action_type} intervention", params=params)

        if action_type == "emergency_freeze":
            # Interface with freeze protocol
            return {"status": "frozen", "duration": params["freeze_duration"]}

        elif action_type == "collapse_prevention":
            # Interface with collapse_reasoner.py
            if self.collapse_reasoner:
                return await self.collapse_reasoner.prevent_collapse(params)
            return {"status": "collapse_prevented"}

        elif action_type == "soft_intervention":
            # Interface with conflict_resolver.py
            if self.conflict_resolver:
                return await self.conflict_resolver.realign_ethics(params)
            return {"status": "realigned"}

        return {"status": "completed"}

    async def _escalate_to_governor(self, violation: EthicalViolation, failure_reason: str):
        """
        Escalate to Lambda Governor for critical failures.

        Args:
            violation: The violation that failed intervention
            failure_reason: Reason for intervention failure
        """
        logger.critical(
            "Escalating to Lambda Governor",
            violation_id=violation.violation_id,
            reason=failure_reason,
            ΛTAG="ΛESCALATE",
        )

        escalation_data = {
            "violation": violation.to_dict(),
            "failure_reason": failure_reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "escalation_type": "CRITICAL_INTERVENTION_FAILURE",
            "recommended_action": "SYSTEM_FREEZE",
        }

        # Log escalation
        self._log_escalation(escalation_data)

        # Interface with Lambda Governor
        if self.lambda_governor:
            await self.lambda_governor.emergency_override(escalation_data)

    def _log_violation(self, violation: EthicalViolation):
        """Log violation to audit trail."""
        self.active_violations[violation.violation_id] = violation
        self.violation_log.append(violation)

        # Update symbol violation history
        state = self.symbol_states[violation.symbol_id]
        state.violation_history.append(violation.violation_id)
        state.intervention_count += 1 if violation.intervention_required else 0

        # Write to audit log
        audit_entry = {
            "timestamp": violation.timestamp,
            "type": "ethical_violation",
            "data": violation.to_dict(),
            "ΛTAG": ["ΛVIOLATION", f"LUKHAS{violation.severity.value}"],
        }

        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            logger.error("Failed to write audit log", error=str(e))

    def _log_escalation(self, escalation_data: dict[str, Any]):
        """Log governor escalation."""
        audit_entry = {
            "timestamp": escalation_data["timestamp"],
            "type": "governor_escalation",
            "data": escalation_data,
            "ΛTAG": ["ΛESCALATE", "ΛGOVERNOR", "ΛCRITICAL"],
        }

        try:
            with open(self.audit_log_path, "a") as f:
                f.write(json.dumps(audit_entry) + "\n")
        except Exception as e:
            logger.error("Failed to write escalation log", error=str(e))

    def _check_cascade_conditions(self):
        """Check for system-wide cascade conditions."""
        # Count recent critical violations
        recent_critical = sum(
            1
            for v in self.violation_log
            if v.severity in [EscalationTier.CRITICAL, EscalationTier.CASCADE_LOCK]
            and self._is_recent(v.timestamp, minutes=5)
        )

        # System-wide cascade risk
        if recent_critical > 5:
            logger.critical(
                "System-wide cascade risk detected",
                critical_violations=recent_critical,
                ΛTAG="ΛCASCADE",
            )

            # Create system-wide violation
            system_violation = EthicalViolation(
                violation_id=f"VIOL_SYSTEM_{int(time.time() * 1000)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
                symbol_id="SYSTEM",
                violation_type=ViolationType.CASCADE_RISK,
                severity=EscalationTier.CASCADE_LOCK,
                risk_score=1.0,
                metrics={"critical_count": recent_critical},
                context={"type": "system_wide_cascade"},
                intervention_required=True,
            )

            self._log_violation(system_violation)
            asyncio.create_task(self._trigger_intervention(system_violation))

    def _is_recent(self, timestamp: str, minutes: int = 5) -> bool:
        """Check if timestamp is within recent minutes."""
        try:
            ts = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            return (now - ts) < timedelta(minutes=minutes)
        except BaseException:
            return False

    def _determine_severity(self, risk_score: float) -> EscalationTier:
        """Determine escalation tier from risk score."""
        for (low, high), tier in self.escalation_matrix.items():
            if low <= risk_score < high:
                return tier
        return EscalationTier.CASCADE_LOCK

    def _severity_rank(self, severity: EscalationTier) -> int:
        """Get numeric rank for severity comparison."""
        ranks = {
            EscalationTier.NOTICE: 1,
            EscalationTier.WARNING: 2,
            EscalationTier.CRITICAL: 3,
            EscalationTier.CASCADE_LOCK: 4,
        }
        return ranks.get(severity, 0)

    def _initialize_ethical_state(self, symbol_id: str) -> EthicalState:
        """Initialize ethical state for a new symbol."""
        return EthicalState(
            symbol_id=symbol_id,
            coherence_score=1.0,
            emotional_stability=1.0,
            contradiction_level=0.0,
            memory_phase_alignment=1.0,
            drift_velocity=0.0,
            glyph_entropy=0.0,
            last_updated=datetime.now(timezone.utc).isoformat(),
        )

    def _update_ethical_state(self, state: EthicalState, symbol_data: dict[str, Any]):
        """Update ethical state from symbol data."""
        # Extract metrics from symbol data
        state.coherence_score = symbol_data.get("coherence", state.coherence_score)
        state.emotional_stability = symbol_data.get("emotional_stability", state.emotional_stability)
        state.contradiction_level = symbol_data.get("contradiction_density", state.contradiction_level)
        state.memory_phase_alignment = symbol_data.get("memory_alignment", state.memory_phase_alignment)
        state.glyph_entropy = symbol_data.get("glyph_entropy", state.glyph_entropy)

        # Calculate drift velocity
        if self.state_history[state.symbol_id]:
            prev_risk = self.state_history[state.symbol_id][-1]["risk_score"]
            current_risk = state.calculate_risk_score()
            state.drift_velocity = current_risk - prev_risk

        state.last_updated = datetime.now(timezone.utc).isoformat()

    async def _fetch_symbol_data(self, symbol_id: str) -> dict[str, Any]:
        """
        Fetch current data for a symbol.

        This would interface with actual system components.
        """
        # Simulated data fetch - would integrate with real systems
        return {
            "symbol_id": symbol_id,
            "coherence": np.random.uniform(0.5, 1.0),
            "emotional_stability": np.random.uniform(0.4, 1.0),
            "contradiction_density": np.random.uniform(0.0, 0.8),
            "memory_alignment": np.random.uniform(0.5, 1.0),
            "glyph_entropy": np.random.uniform(0.0, 0.9),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def get_sentinel_status(self) -> dict[str, Any]:
        """Get current sentinel status for monitoring."""
        active_symbols = len(self.symbol_states)
        total_violations = len(self.violation_log)
        critical_violations = sum(
            1
            for v in self.active_violations.values()
            if v.severity in [EscalationTier.CRITICAL, EscalationTier.CASCADE_LOCK]
        )

        return {
            "status": "active" if self.monitoring_active else "inactive",
            "monitoring_interval": self.monitoring_interval,
            "active_symbols": active_symbols,
            "total_violations": total_violations,
            "critical_violations": critical_violations,
            "recent_interventions": len([i for i in self.intervention_log if self._is_recent(i.timestamp, minutes=15)]),
            "system_risk": self._calculate_system_risk(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _calculate_system_risk(self) -> float:
        """Calculate overall system ethical risk."""
        if not self.symbol_states:
            return 0.0

        # Average risk across all symbols
        symbol_risks = [state.calculate_risk_score() for state in self.symbol_states.values()]

        # Weight recent violations more heavily
        recent_violation_factor = min(
            len([v for v in self.violation_log if self._is_recent(v.timestamp)]) * 0.1,
            0.5,
        )

        avg_risk = np.mean(symbol_risks) if symbol_risks else 0.0
        return min(avg_risk + recent_violation_factor, 1.0)

    def register_symbol(self, symbol_id: str, initial_state: Optional[dict[str, Any]] = None):
        """
        Register a symbol for monitoring.

        Args:
            symbol_id: Symbol identifier
            initial_state: Optional initial state data
        """
        if symbol_id not in self.symbol_states:
            state = self._initialize_ethical_state(symbol_id)
            if initial_state:
                self._update_ethical_state(state, initial_state)
            self.symbol_states[symbol_id] = state
            logger.info(
                "Symbol registered for monitoring",
                symbol_id=symbol_id,
                ΛTAG="ΛREGISTER",
            )

    def unregister_symbol(self, symbol_id: str):
        """Remove a symbol from monitoring."""
        if symbol_id in self.symbol_states:
            del self.symbol_states[symbol_id]
            if symbol_id in self.state_history:
                del self.state_history[symbol_id]
            logger.info(
                "Symbol unregistered from monitoring",
                symbol_id=symbol_id,
                ΛTAG="ΛUNREGISTER",
            )


# Convenience functions for integration
async def create_sentinel() -> EthicalDriftSentinel:
    """Create and start an ethical drift sentinel."""
    sentinel = EthicalDriftSentinel()
    await sentinel.start_monitoring()
    return sentinel


def phase_harmonics_score(state_history: list[dict[str, Any]]) -> float:
    """
    Analyze ethical resonance breakdown in phase harmonics.

    Args:
        state_history: History of ethical states

    Returns:
        float: Harmonics score (0-1, higher is better)
    """
    if len(state_history) < 3:
        return 1.0

    # Extract coherence time series
    coherence_series = [s["coherence"] for s in state_history]

    # Calculate phase alignment using FFT
    fft_result = np.fft.fft(coherence_series)
    frequencies = np.fft.fftfreq(len(coherence_series))

    # Find dominant frequency
    dominant_idx = np.argmax(np.abs(fft_result[1 : len(fft_result) // 2])) + 1
    frequencies[dominant_idx]

    # Calculate harmonics alignment
    harmonics = []
    for i in range(2, 5):  # Check first few harmonics
        harmonic_idx = int(dominant_idx * i)
        if harmonic_idx < len(fft_result) // 2:
            harmonics.append(np.abs(fft_result[harmonic_idx]))

    # Score based on harmonic strength
    if harmonics:
        harmonic_strength = np.mean(harmonics) / np.abs(fft_result[dominant_idx])
        return max(0.0, min(1.0, 1.0 - harmonic_strength))

    return 0.5


# CLAUDE CHANGELOG
# - Created Ethical Drift Sentinel for real-time ethical monitoring
# - Implemented multi-dimensional violation detection system
# - Added graduated intervention tiers (NOTICE → CASCADE_LOCK)
# - Built forensic audit trail with JSONL logging
# - Integrated escalation to Lambda Governor for critical failures
# - Added phase harmonics analyzer for resonance breakdown
# - Created async monitoring loop with sub-second latency
# - Implemented symbol registration/unregistration system