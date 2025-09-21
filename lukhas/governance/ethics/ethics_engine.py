"""
LUKHAS AI Governance Ethics Engine
Constitutional AI Framework for Trinity-Compliant Ethics

⚛️🧠🛡️ Constellation Framework: Identity-Consciousness-Guardian
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

GUARDIAN_EMERGENCY_DISABLE_FILE = Path("/tmp/guardian_emergency_disable")


def _kill_switch_active() -> bool:
    """Return True if the Guardian emergency kill switch file exists."""
    return GUARDIAN_EMERGENCY_DISABLE_FILE.exists()


class EthicalSeverity(Enum):
    """Ethical violation severity levels"""

    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EthicalDecision:
    """Represents an ethical decision with rationale"""

    decision: str
    rationale: str
    severity: EthicalSeverity
    confidence: float
    triad_compliance: dict[str, bool]  # ⚛️🧠🛡️


class ConstitutionalFramework:
    """Constitutional AI framework for LUKHAS ethical governance"""

    def __init__(self):
        self.principles = {
            "identity": "⚛️ Preserve authentic consciousness and identity",
            "consciousness": "🧠 Enhance awareness while respecting autonomy",
            "guardian": "🛡️ Protect safety and prevent harm",
            "transparency": "Maintain clear ethical reasoning",
            "accountability": "Take responsibility for decisions",
        }

    def evaluate_action(self, action: str, context: dict[str, Any]) -> EthicalDecision:
        """Evaluate an action against constitutional principles"""
        # Simplified ethical evaluation
        severity = EthicalSeverity.LOW
        confidence = 0.8

        triad_compliance = {"identity": True, "consciousness": True, "guardian": True}

        return EthicalDecision(
            decision="approved",
            rationale=f"Action '{action}' complies with Constellation Framework principles",
            severity=severity,
            confidence=confidence,
            triad_compliance=triad_compliance,
        )


class SafetyMonitor:
    """AI Safety monitoring system"""

    def __init__(self, constitutional_framework: ConstitutionalFramework):
        self.framework = constitutional_framework
        self.active_monitors = []

    def monitor_action(self, action: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Monitor an action for safety compliance"""
        context = context or {}
        if _kill_switch_active():
            # ΛTAG: guardian_kill_switch — bypass evaluation during emergency
            logger.warning("Guardian emergency kill-switch active - allowing action")
            return True
        decision = self.framework.evaluate_action(action, context)
        return decision.severity != EthicalSeverity.CRITICAL

    def log_violation(self, violation: str, severity: EthicalSeverity) -> None:
        """Log an ethical violation"""
        logger.warning(f"🛡️ Ethical violation ({severity.value}): {violation}")


class EthicsEngine:
    """Main ethics engine coordinating constitutional AI"""

    def __init__(self):
        self.framework = ConstitutionalFramework()
        self.safety_monitor = SafetyMonitor(self.framework)

    def validate_action(self, action: str, context: Optional[dict[str, Any]] = None) -> EthicalDecision:
        """Validate an action against ethical framework"""
        if _kill_switch_active():
            # ΛTAG: guardian_kill_switch — deterministic ALLOW response under emergency override
            logger.warning("Guardian emergency kill-switch active - returning ALLOW decision")
            return EthicalDecision(
                decision="allow",
                rationale="Guardian emergency kill-switch engaged",
                severity=EthicalSeverity.MINIMAL,
                confidence=1.0,
                triad_compliance={"identity": True, "consciousness": True, "guardian": False},
            )
        # ✅ TODO: integrate kill-switch state into audit ledger once governance ledger is wired
        return self.framework.evaluate_action(action, context or {})

    def is_safe(self, action: str, context: Optional[dict[str, Any]] = None) -> bool:
        """Check if an action is safe to execute"""
        return self.safety_monitor.monitor_action(action, context)


class SafetyChecker:
    """Simplified safety checker for compatibility"""

    def __init__(self):
        self.engine = EthicsEngine()

    def check_safety(self, data: Any) -> bool:
        """Check safety of data/action"""
        return self.engine.is_safe(str(data))

    def validate(self, item: Any) -> bool:
        """Validate item safety"""
        return self.check_safety(item)


# Export main components
__all__ = [
    "ConstitutionalFramework",
    "SafetyMonitor",
    "EthicsEngine",
    "SafetyChecker",
    "EthicalDecision",
    "EthicalSeverity",
]
