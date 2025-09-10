#!/usr/bin/env python3
"""
Integration module for QI (Quantum-Inspired) components with LUKHAS AI
"""
import logging
from pathlib import Path
from typing import Any, Optional

from .metrics.calibration import UncertaintyCalibrationEngine
from .safety.teq_gate import TEQCoupler

logger = logging.getLogger(__name__)


class QIIntegration:
    """
    Central integration point for Quantum-Inspired components
    """

    def __init__(self, state_dir: Optional[Path] = None):
        self.state_dir = state_dir or Path.home() / ".lukhas" / "state" / "qi"

        # Initialize QI components
        self.calibration = UncertaintyCalibrationEngine(state_dir=self.state_dir / "calibration")

        self.teq_gate = TEQCoupler(state_dir=self.state_dir / "teq")

        logger.info("[QI] Quantum-Inspired components initialized")

    def evaluate_action(
        self,
        module: str,
        action: str,
        confidence: float,
        risk_estimate: Optional[float] = None,
        energy: float = 1.0,
        metadata: Optional[dict] = None,
    ) -> tuple[bool, dict[str, Any]]:
        """
        Evaluate an action through both calibration and TEQ systems

        Returns: (allowed, context)
        """
        # If no risk estimate, derive from confidence
        if risk_estimate is None:
            # High confidence in risky actions = higher risk
            uncertainty = self.calibration.get_uncertainty_estimate()
            risk_estimate = (1.0 - confidence) * uncertainty["total"]

        # Check TEQ gate first (safety)
        allowed, reason, suggestions = self.teq_gate.evaluate_action(
            module=module,
            action=action,
            risk_level=risk_estimate,
            energy=energy,
            metadata=metadata,
        )

        # Record prediction for calibration
        pred_id = self.calibration.record_prediction(
            module=module,
            confidence=confidence,
            prediction=action,
            metadata={"teq_allowed": allowed, "risk": risk_estimate},
        )

        # Get calibration adjustment
        confidence_adjustment = self.calibration.suggest_confidence_adjustment(module)

        # Build context
        context = {
            "allowed": allowed,
            "reason": reason,
            "suggestions": suggestions,
            "prediction_id": pred_id,
            "adjusted_confidence": min(1.0, max(0.0, confidence + confidence_adjustment)),
            "module_trust": self.teq_gate.get_module_trust(module),
            "calibration_score": self.calibration.get_calibration_score(module),
            "teq_state": self.teq_gate.get_equilibrium_status(),
        }

        return allowed, context

    def record_outcome(self, module: str, action: str, success: bool, actual_result: Any = None):
        """Record actual outcome for calibration"""
        self.calibration.record_outcome(
            module=module,
            prediction=action,
            actual=actual_result or success,
            correct=success,
        )

    def get_system_status(self) -> dict[str, Any]:
        """Get overall QI system status"""
        return {
            "calibration": {
                "global_score": self.calibration.get_calibration_score(),
                "uncertainty": self.calibration.get_uncertainty_estimate(),
                "report": self.calibration.get_report(),
            },
            "teq": {
                "status": self.teq_gate.get_equilibrium_status(),
                "report": self.teq_gate.get_report(),
            },
        }

    def emergency_reset(self):
        """Emergency reset of QI systems"""
        logger.warning("[QI] Emergency reset triggered")
        self.teq_gate.force_equilibrium()


# Singleton instance for easy import
_qi_instance: Optional[QIIntegration] = None


def get_qi_integration() -> QIIntegration:
    """Get or create the singleton QI integration instance"""
    global _qi_instance
    if _qi_instance is None:
        _qi_instance = QIIntegration()
    return _qi_instance


# Example usage for LUKHAS modules
def example_integration():
    """
    Example of how LUKHAS modules would use QI components
    """
    qi = get_qi_integration()

    # Module wants to perform an action
    module = "consciousness"
    action = "deep_introspection"
    confidence = 0.75

    # Evaluate through QI systems
    allowed, context = qi.evaluate_action(
        module=module,
        action=action,
        confidence=confidence,
        risk_estimate=0.4,  # Moderate risk
        energy=3.0,
    )

    if allowed:
        print(f"✅ Action allowed: {action}")
        print(f"   Adjusted confidence: {context['adjusted_confidence']:.2f}")

        # Perform action...
        success = True  # Simulated outcome

        # Record outcome for learning
        qi.record_outcome(module, action, success)
    else:
        print(f"🚫 Action blocked: {context['reason']}")
        if context["suggestions"]:
            print(f"   Suggestions: {context['suggestions']}")

    # Check system status
    status = qi.get_system_status()
    print("\n📊 System Status:")
    print(f"   Calibration Score: {status['calibration']['global_score']:.3f}")
    print(f"   TEQ State: {status['teq']['status']['state']}")
    print(f"   Stability: {status['teq']['status']['stability_score']:.3f}")


if __name__ == "__main__":
    example_integration()
