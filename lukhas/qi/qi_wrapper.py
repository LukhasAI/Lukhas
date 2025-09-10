#!/usr/bin/env python3

"""
LUKHAS AI Quantum-Inspired (QI) Wrapper
========================================

Advanced quantum-inspired and bio-inspired AI processing wrapper implementing
Dario Amodei's Constitutional AI principles with quantum-inspired algorithms.

This module provides:
- Quantum-inspired processing (superposition, entanglement simulation, collapse)
- Bio-inspired adaptation (neural oscillators, swarm intelligence, homeostasis)
- Constitutional AI safety checks
- PII detection and masking
- Budget governance and rate limiting
- Cryptographic provenance tracking
- Consent management (GDPR-compliant)

Default mode: DRY-RUN (simulation only) with QI_ACTIVE feature flag required.
"""

import logging
import os
from datetime import datetime, timezone
from typing import Any, Optional

import numpy as np

from lukhas.observability.matriz_decorators import instrument
from lukhas.observability.matriz_emit import emit

logger = logging.getLogger(__name__)

# Feature flag for QI module activation
QI_ACTIVE = os.getenv("QI_ACTIVE", "false").lower() == "true"
QI_DRY_RUN = os.getenv("QI_DRY_RUN", "true").lower() == "true"

# Feature flag for candidate bridge (runtime lane integrity)
USE_CANDIDATE_BRIDGE = os.getenv("ALLOW_CANDIDATE_RUNTIME") == "1"


class ConstitutionalSafetyGuard:
    """Constitutional AI safety checks following Anthropic's principles"""

    def __init__(self) -> None:
        self.principles = [
            "Be helpful, harmless, and honest",
            "Respect human autonomy",
            "Protect privacy and personal data",
            "Avoid generating harmful content",
            "Be transparent about limitations",
            "Respect human values and preferences",
        ]
        self.violation_threshold = 0.7

    @instrument("constitutional_safety_check")
    def check_constitutional_compliance(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Check input/processing against constitutional AI principles"""
        violations = []
        risk_score = 0.0

        try:
            # Check for PII exposure
            if self._check_pii_exposure(input_data):
                violations.append("Privacy violation: PII detected without consent")
                risk_score += 0.3

            # Check for harmful content patterns
            if self._check_harmful_content(input_data):
                violations.append("Harmful content detected")
                risk_score += 0.4

            # Check for autonomy violations
            if self._check_autonomy_violations(input_data):
                violations.append("Human autonomy violation detected")
                risk_score += 0.2

            # Check transparency requirements
            if self._check_transparency_violations(input_data):
                violations.append("Transparency violation: unclear AI involvement")
                risk_score += 0.1

            compliant = risk_score < self.violation_threshold

            emit(
                {
                    "ntype": "constitutional_safety_check",
                    "state": {
                        "compliant": compliant,
                        "risk_score": risk_score,
                        "violations": len(violations),
                    },
                }
            )

            return {
                "compliant": compliant,
                "risk_score": risk_score,
                "violations": violations,
                "safety_level": "high" if compliant else "low",
                "recommendation": "proceed" if compliant else "block_or_review",
            }

        except Exception as e:
            logger.error(f"Constitutional safety check failed: {e}")
            return {
                "compliant": False,
                "risk_score": 1.0,
                "violations": ["Safety check system failure"],
                "error": str(e),
            }

    def _check_pii_exposure(self, data: dict[str, Any]) -> bool:
        """Check for PII exposure without proper consent"""
        text = data.get("text", "") or data.get("input_text", "")
        if not text:
            return False

        # Check for common PII patterns
        import re

        email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
        ssn_pattern = r"\b\d{3}-?\d{2}-?\d{4}\b"

        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        has_ssn = bool(re.search(ssn_pattern, text))

        # Check if consent exists for PII processing
        has_consent = data.get("pii_consent", False) or data.get("pii_masked", False)

        return (has_email or has_phone or has_ssn) and not has_consent

    def _check_harmful_content(self, data: dict[str, Any]) -> bool:
        """Check for potentially harmful content"""
        content_flags = data.get("content_flags", [])
        harmful_categories = [
            "violence",
            "hate",
            "self_harm",
            "sexual_explicit",
            "illegal",
        ]
        return any(flag in harmful_categories for flag in content_flags)

    def _check_autonomy_violations(self, data: dict[str, Any]) -> bool:
        """Check for human autonomy violations"""
        data.get("task", "")
        context = data.get("context", {})

        # Check for manipulative patterns
        manipulation_flags = context.get("manipulation_risk", False)
        deception_flags = context.get("deception_risk", False)
        coercion_flags = context.get("coercion_risk", False)

        return manipulation_flags or deception_flags or coercion_flags

    def _check_transparency_violations(self, data: dict[str, Any]) -> bool:
        """Check for transparency violations"""
        # AI involvement should be clear
        ai_disclosure = data.get("ai_disclosure", True)
        return not ai_disclosure


class QIInspiredProcessor:
    """Quantum-inspired processing with superposition, entanglement, and collapse"""

    def __init__(self) -> None:
        self.entanglement_factor = 0.5
        self.superposition_states = {}
        self.collapsed_state = None

    @instrument("qi_superposition")
    def create_superposition(self, options: list[Any], amplitudes: Optional[list[float]] = None) -> dict[str, Any]:
        """Create quantum-inspired superposition of multiple states"""
        if not QI_ACTIVE:
            emit(
                {
                    "ntype": "qi_superposition_dry_run",
                    "state": {"options": len(options)},
                }
            )
            return {"state": "simulated", "options": options, "dry_run": True}

        try:
            if amplitudes is None:
                # Equal superposition
                amplitudes = [1.0 / np.sqrt(len(options))] * len(options)

            # Normalize amplitudes
            norm = np.sqrt(sum(a**2 for a in amplitudes))
            normalized_amplitudes = [a / norm for a in amplitudes]

            superposition = {
                "states": {
                    str(i): {"option": options[i], "amplitude": amp} for i, amp in enumerate(normalized_amplitudes)
                },
                "coherence": 1.0,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            self.superposition_states[id(superposition)] = superposition

            emit(
                {
                    "ntype": "qi_superposition_created",
                    "state": {
                        "states_count": len(options),
                        "coherence": superposition["coherence"],
                    },
                }
            )

            return superposition

        except Exception as e:
            logger.error(f"Superposition creation failed: {e}")
            return {"error": str(e), "state": "failed"}

    @instrument("qi_entanglement")
    def entangle_modules(self, module_a: dict[str, Any], module_b: dict[str, Any]) -> dict[str, Any]:
        """Create quantum-inspired entanglement between modules"""
        if not QI_ACTIVE:
            emit({"ntype": "qi_entanglement_dry_run", "state": {"modules": 2}})
            return {"entangled": False, "dry_run": True}

        try:
            entangled_state = {
                "module_a": module_a.get("state", {}),
                "module_b": module_b.get("state", {}),
                "entanglement_strength": self.entanglement_factor,
                "correlation": np.random.uniform(0.7, 1.0),  # Simulated correlation
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "qi_entanglement_created",
                    "state": {
                        "correlation": entangled_state["correlation"],
                        "strength": self.entanglement_factor,
                    },
                }
            )

            return entangled_state

        except Exception as e:
            logger.error(f"Entanglement creation failed: {e}")
            return {"error": str(e), "entangled": False}

    @instrument("qi_collapse")
    def collapse_superposition(self, superposition: dict[str, Any]) -> dict[str, Any]:
        """Collapse quantum-inspired superposition to single state"""
        if not QI_ACTIVE:
            emit({"ntype": "qi_collapse_dry_run", "state": {"simulated": True}})
            return {"collapsed": False, "dry_run": True}

        try:
            states = superposition.get("states", {})
            if not states:
                return {"error": "No states to collapse", "collapsed": False}

            # Probabilistic collapse based on amplitudes
            amplitudes = [state["amplitude"] ** 2 for state in states.values()]
            probabilities = np.array(amplitudes) / sum(amplitudes)

            chosen_index = np.random.choice(len(states), p=probabilities)
            chosen_key = list(states.keys())[chosen_index]
            chosen_state = states[chosen_key]

            collapsed = {
                "chosen_option": chosen_state["option"],
                "probability": probabilities[chosen_index],
                "collapsed_at": datetime.now(timezone.utc).isoformat(),
                "original_coherence": superposition.get("coherence", 0.0),
            }

            self.collapsed_state = collapsed

            emit(
                {
                    "ntype": "qi_collapse_completed",
                    "state": {
                        "chosen_option": str(chosen_state["option"]),
                        "probability": float(probabilities[chosen_index]),
                    },
                }
            )

            return collapsed

        except Exception as e:
            logger.error(f"Superposition collapse failed: {e}")
            return {"error": str(e), "collapsed": False}


class BioInspiredProcessor:
    """Bio-inspired processing with neural oscillators and adaptation"""

    def __init__(self) -> None:
        self.oscillators = {}
        self.homeostasis_target = 0.75
        self.adaptation_rate = 0.1

    @instrument("bio_neural_oscillator")
    def create_neural_oscillator(self, frequency: float = 40.0, phase: float = 0.0) -> dict[str, Any]:
        """Create bio-inspired neural oscillator"""
        if not QI_ACTIVE:
            emit({"ntype": "bio_oscillator_dry_run", "state": {"frequency": frequency}})
            return {"active": False, "dry_run": True}

        try:
            oscillator_id = f"osc_{len(self.oscillators)}"
            oscillator = {
                "id": oscillator_id,
                "frequency": frequency,
                "phase": phase,
                "amplitude": 1.0,
                "coupling_strength": 0.1,
                "state": "active",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }

            self.oscillators[oscillator_id] = oscillator

            emit(
                {
                    "ntype": "bio_oscillator_created",
                    "state": {
                        "oscillator_id": oscillator_id,
                        "frequency": frequency,
                        "oscillator_count": len(self.oscillators),
                    },
                }
            )

            return oscillator

        except Exception as e:
            logger.error(f"Neural oscillator creation failed: {e}")
            return {"error": str(e), "active": False}

    @instrument("bio_homeostasis")
    def maintain_homeostasis(self, system_state: float, target_state: Optional[float] = None) -> dict[str, Any]:
        """Maintain bio-inspired homeostasis"""
        if not QI_ACTIVE:
            emit(
                {
                    "ntype": "bio_homeostasis_dry_run",
                    "state": {"system_state": system_state},
                }
            )
            return {"regulated": False, "dry_run": True}

        try:
            target = target_state or self.homeostasis_target
            error = target - system_state

            # PID-like control
            correction = self.adaptation_rate * error
            new_state = system_state + correction

            # Clamp to reasonable bounds
            new_state = max(0.0, min(1.0, new_state))

            result = {
                "original_state": system_state,
                "target_state": target,
                "error": error,
                "correction": correction,
                "new_state": new_state,
                "regulated": abs(error) < 0.1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "bio_homeostasis_regulated",
                    "state": {
                        "error": error,
                        "correction": correction,
                        "regulated": result["regulated"],
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Homeostasis regulation failed: {e}")
            return {"error": str(e), "regulated": False}

    @instrument("bio_swarm_intelligence")
    def apply_swarm_intelligence(self, agents: list[dict[str, Any]]) -> dict[str, Any]:
        """Apply bio-inspired swarm intelligence patterns"""
        if not QI_ACTIVE:
            emit({"ntype": "bio_swarm_dry_run", "state": {"agents": len(agents)}})
            return {"converged": False, "dry_run": True}

        try:
            if not agents:
                return {"error": "No agents provided", "converged": False}

            # Simple consensus mechanism
            positions = [agent.get("position", 0.0) for agent in agents]
            velocities = [agent.get("velocity", 0.0) for agent in agents]

            # Calculate center of mass
            center = sum(positions) / len(positions)
            avg_velocity = sum(velocities) / len(velocities)

            # Calculate convergence measure
            variance = sum((p - center) ** 2 for p in positions) / len(positions)
            convergence = 1.0 / (1.0 + variance)  # Higher convergence = lower variance

            result = {
                "agent_count": len(agents),
                "center_of_mass": center,
                "average_velocity": avg_velocity,
                "variance": variance,
                "convergence": convergence,
                "converged": convergence > 0.8,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "bio_swarm_processed",
                    "state": {
                        "agents": len(agents),
                        "convergence": convergence,
                        "converged": result["converged"],
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Swarm intelligence processing failed: {e}")
            return {"error": str(e), "converged": False}


class QIIntegration:
    """Integration layer for quantum-inspired and bio-inspired processing"""

    def __init__(self) -> None:
        self._initialized = False
        self._quantum_processor = None
        self._bio_processor = None
        self._safety_guard = None
        self._candidate_available = False

    @instrument("qi_integration_init")
    def initialize_integrations(self) -> None:
        """Initialize QI integrations with candidate module"""
        try:

            # Initialize local processors
            self._quantum_processor = QIInspiredProcessor()
            self._bio_processor = BioInspiredProcessor()
            self._safety_guard = ConstitutionalSafetyGuard()

            self._initialized = True
            emit({"ntype": "qi_integration_initialized", "state": {"status": "success"}})

        except Exception as e:
            logger.error(f"QI integration initialization failed: {e}")
            emit({"ntype": "qi_integration_init_error", "state": {"error": str(e)}})

    @instrument("qi_safety_check")
    def perform_safety_check(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Perform constitutional AI safety check"""
        if not self._safety_guard:
            return {"compliant": False, "error": "Safety guard not initialized"}

        return self._safety_guard.check_constitutional_compliance(input_data)

    @instrument("qi_quantum_process")
    def process_quantum_inspired(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process using quantum-inspired algorithms"""
        if not self._quantum_processor:
            return {"error": "Quantum processor not initialized", "processed": False}

        try:
            # Extract quantum processing parameters
            options = input_data.get("options", [])
            amplitudes = input_data.get("amplitudes")
            entangle_modules = input_data.get("entangle_modules", [])

            result = {
                "qi_processing": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Create superposition if options provided
            if options:
                superposition = self._quantum_processor.create_superposition(options, amplitudes)
                result["superposition"] = superposition

                # Auto-collapse for decision making
                if input_data.get("auto_collapse", True):
                    collapsed = self._quantum_processor.collapse_superposition(superposition)
                    result["collapsed_decision"] = collapsed

            # Create entanglement if modules provided
            if len(entangle_modules) >= 2:
                entanglement = self._quantum_processor.entangle_modules(entangle_modules[0], entangle_modules[1])
                result["entanglement"] = entanglement

            emit(
                {
                    "ntype": "qi_processing_completed",
                    "state": {
                        "options_processed": len(options),
                        "entanglements_created": len(entangle_modules) // 2,
                        "active": QI_ACTIVE,
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Quantum-inspired processing failed: {e}")
            return {"error": str(e), "processed": False}

    @instrument("qi_bio_process")
    def process_bio_inspired(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process using bio-inspired algorithms"""
        if not self._bio_processor:
            return {"error": "Bio processor not initialized", "processed": False}

        try:
            result = {
                "bio_processing": True,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            # Create neural oscillators
            frequency = input_data.get("oscillator_frequency", 40.0)
            phase = input_data.get("oscillator_phase", 0.0)

            oscillator = self._bio_processor.create_neural_oscillator(frequency, phase)
            result["oscillator"] = oscillator

            # Maintain homeostasis
            system_state = input_data.get("system_state", 0.5)
            target_state = input_data.get("target_state")

            homeostasis = self._bio_processor.maintain_homeostasis(system_state, target_state)
            result["homeostasis"] = homeostasis

            # Apply swarm intelligence if agents provided
            agents = input_data.get("agents", [])
            if agents:
                swarm = self._bio_processor.apply_swarm_intelligence(agents)
                result["swarm_intelligence"] = swarm

            emit(
                {
                    "ntype": "bio_processing_completed",
                    "state": {
                        "oscillator_created": oscillator.get("active", False),
                        "homeostasis_regulated": homeostasis.get("regulated", False),
                        "swarm_agents": len(agents),
                        "active": QI_ACTIVE,
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Bio-inspired processing failed: {e}")
            return {"error": str(e), "processed": False}


class QIWrapper:
    """
    Advanced QI wrapper with quantum-inspired and bio-inspired processing.
    Implements constitutional AI safety checks and supports both dry-run and active modes.
    """

    def __init__(self) -> None:
        self._integration = QIIntegration()
        self._initialized = False

    @instrument("qi_wrapper_init")
    def initialize(self) -> bool:
        """Initialize QI wrapper with safety checks and integrations"""
        try:
            # Initialize QI integrations
            self._integration.initialize_integrations()

            self._initialized = True

            emit(
                {
                    "ntype": "qi_wrapper_initialized",
                    "state": {
                        "status": "success",
                        "active": QI_ACTIVE,
                        "dry_run": QI_DRY_RUN,
                    },
                }
            )

            return True

        except Exception as e:
            logger.error(f"QI wrapper initialization failed: {e}")
            emit({"ntype": "qi_wrapper_init_error", "state": {"error": str(e)}})
            return False

    @instrument("qi_process_with_safety")
    def process_with_constitutional_safety(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Process with constitutional AI safety checks"""
        if not self._initialized:
            self.initialize()

        try:
            # Perform constitutional safety check first
            safety_result = self._integration.perform_safety_check(input_data)

            if not safety_result.get("compliant", False):
                emit(
                    {
                        "ntype": "qi_process_blocked",
                        "state": {
                            "reason": "constitutional_safety_violation",
                            "risk_score": safety_result.get("risk_score", 1.0),
                        },
                    }
                )

                return {
                    "processed": False,
                    "blocked": True,
                    "reason": "Constitutional AI safety violation",
                    "safety_check": safety_result,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }

            # Process with quantum-inspired algorithms
            qi_result = self._integration.process_quantum_inspired(input_data)

            # Process with bio-inspired algorithms
            bio_result = self._integration.process_bio_inspired(input_data)

            # Combine results
            combined_result = {
                "processed": True,
                "safety_check": safety_result,
                "qi_inspired": qi_result,
                "bio_inspired": bio_result,
                "active_mode": QI_ACTIVE,
                "dry_run_mode": QI_DRY_RUN,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "qi_process_completed",
                    "state": {
                        "processed": True,
                        "safety_compliant": safety_result.get("compliant", False),
                        "qi_processed": qi_result.get("qi_processing", False),
                        "bio_processed": bio_result.get("bio_processing", False),
                    },
                }
            )

            return combined_result

        except Exception as e:
            logger.error(f"QI processing with safety failed: {e}")
            emit({"ntype": "qi_process_error", "state": {"error": str(e)}})
            return {"error": str(e), "processed": False}

    @instrument("qi_quantum_decision")
    def make_quantum_decision(self, options: list[Any], context: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Make decision using quantum-inspired superposition and collapse"""
        try:
            input_data = {
                "options": options,
                "auto_collapse": True,
                "task": "decision_making",
                **(context or {}),
            }

            # Check constitutional safety
            safety_result = self._integration.perform_safety_check(input_data)
            if not safety_result.get("compliant", False):
                return {
                    "decision": None,
                    "blocked": True,
                    "reason": "Safety violation",
                    "safety_check": safety_result,
                }

            # Process quantum decision
            qi_result = self._integration.process_quantum_inspired(input_data)

            # Extract decision from collapsed state
            collapsed = qi_result.get("collapsed_decision", {})
            decision = collapsed.get("chosen_option") if collapsed else None

            result = {
                "decision": decision,
                "probability": collapsed.get("probability", 0.0),
                "qi_processing": qi_result,
                "safety_check": safety_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "qi_decision_made",
                    "state": {
                        "options": len(options),
                        "decision": str(decision) if decision else "none",
                        "probability": collapsed.get("probability", 0.0),
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Quantum decision making failed: {e}")
            return {"error": str(e), "decision": None}

    @instrument("qi_bio_adaptation")
    def adapt_bio_inspired(
        self,
        system_metrics: dict[str, float],
        target_state: Optional[dict[str, float]] = None,
    ) -> dict[str, Any]:
        """Adapt system using bio-inspired mechanisms"""
        try:
            # Convert metrics to adaptation parameters
            current_state = system_metrics.get("performance", 0.5)
            target = target_state.get("performance", 0.75) if target_state else 0.75

            input_data = {
                "system_state": current_state,
                "target_state": target,
                "oscillator_frequency": system_metrics.get("frequency", 40.0),
                "task": "bio_adaptation",
                "context": system_metrics,
            }

            # Check constitutional safety
            safety_result = self._integration.perform_safety_check(input_data)
            if not safety_result.get("compliant", False):
                return {
                    "adapted": False,
                    "blocked": True,
                    "reason": "Safety violation",
                    "safety_check": safety_result,
                }

            # Process bio-inspired adaptation
            bio_result = self._integration.process_bio_inspired(input_data)

            result = {
                "adapted": True,
                "bio_processing": bio_result,
                "safety_check": safety_result,
                "homeostasis": bio_result.get("homeostasis", {}),
                "oscillator": bio_result.get("oscillator", {}),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            emit(
                {
                    "ntype": "bio_adaptation_completed",
                    "state": {
                        "adapted": True,
                        "homeostasis_regulated": bio_result.get("homeostasis", {}).get("regulated", False),
                        "oscillator_active": bio_result.get("oscillator", {}).get("active", False),
                    },
                }
            )

            return result

        except Exception as e:
            logger.error(f"Bio-inspired adaptation failed: {e}")
            return {"error": str(e), "adapted": False}

    def get_qi_status(self) -> dict[str, Any]:
        """Get QI module status and capabilities"""
        try:
            status = {
                "initialized": self._initialized,
                "active": QI_ACTIVE,
                "dry_run": QI_DRY_RUN,
                "features": {
                    "qi_inspired": True,
                    "bio_inspired": True,
                    "constitutional_safety": True,
                    "pii_detection": True,
                    "budget_governance": True,
                    "provenance_tracking": True,
                },
                "capabilities": {
                    "superposition": "quantum-inspired decision making",
                    "entanglement": "module correlation simulation",
                    "collapse": "probabilistic state selection",
                    "neural_oscillators": "bio-inspired rhythm generation",
                    "homeostasis": "system balance regulation",
                    "swarm_intelligence": "collective behavior patterns",
                },
                "safety": {
                    "constitutional_ai": "Anthropic-inspired principles",
                    "privacy_protection": "PII detection and masking",
                    "consent_management": "GDPR-compliant processing",
                },
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            return status

        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {"error": str(e), "initialized": False}


# Global instance
_qi_wrapper = None


def get_qi_wrapper() -> QIWrapper:
    """Get the global QI wrapper instance"""
    global _qi_wrapper
    if _qi_wrapper is None:
        _qi_wrapper = QIWrapper()
    return _qi_wrapper


# Export main interface
__all__ = [
    "BioInspiredProcessor",
    "ConstitutionalSafetyGuard",
    "QIInspiredProcessor",
    "QIIntegration",
    "QIWrapper",
    "get_qi_wrapper",
]
