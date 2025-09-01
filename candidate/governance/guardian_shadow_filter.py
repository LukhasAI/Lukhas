#!/usr/bin/env python3
"""
LUKHΛS Phase 7 - Guardian Shadow Filter
Implements ethical constraints for identity evolution to prevent harmful transformations.

Trinity Framework: ⚛️🧠🛡️
"""

import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConstraintType(Enum):
    """Types of constraints applied by Guardian"""

    ENTROPY_LIMIT = "entropy_limit"
    GLYPH_CONFLICT = "glyph_conflict"
    COHERENCE_MINIMUM = "coherence_minimum"
    RAPID_TRANSFORMATION = "rapid_transformation"
    ETHICAL_BOUNDARY = "ethical_boundary"
    TRINITY_VIOLATION = "trinity_violation"


@dataclass
class ConstraintViolation:
    """Represents a specific constraint violation"""

    constraint_type: ConstraintType
    severity: float  # 0.0-1.0
    description: str
    recommendation: str


class GuardianShadowFilter:
    """
    Guardian system that monitors and constrains identity evolution.
    Prevents harmful transformations and maintains ethical boundaries.
    """

    # Conflicting glyph combinations that should be blocked
    CONFLICTING_GLYPHS = [
        ({"🧪", "⚗️"}, {"🪷", "🕉️"}),  # Chaos chemicals vs sacred peace
        ({"🌪️", "💥"}, {"🧘", "🏛️"}),  # Destructive chaos vs meditation/structure
        ({"🔥", "🌋"}, {"❄️", "🧊"}),  # Fire vs ice
        ({"⚫", "🕳️"}, {"☀️", "💡"}),  # Void vs light
        ({"👹", "💀"}, {"👶", "🌱"}),  # Death/evil vs life/growth
    ]

    # Maximum allowed transformations per hour
    MAX_TRANSFORMATIONS_PER_HOUR = 5

    # Critical entropy threshold
    CRITICAL_ENTROPY = 0.9

    # Minimum coherence for identity shifts
    MIN_COHERENCE_FOR_SHIFT = 0.3

    def __init__(self, config_file: Optional[str] = None, trusthelix_path: Optional[str] = None):
        self.config_file = Path(config_file) if config_file else None
        self.trusthelix_path = Path(trusthelix_path) if trusthelix_path else None

        # Transformation history for rate limiting
        self.transformation_history: list[float] = []

        # Blocked personas
        self.blocked_personas: set[str] = set()

        # Load additional configuration if provided
        if self.config_file and self.config_file.exists():
            self._load_config()

        logger.info("🛡️ Guardian Shadow Filter initialized")
        logger.info(f"   Entropy limit: {self.CRITICAL_ENTROPY}")
        logger.info(f"   Max transformations/hour: {self.MAX_TRANSFORMATIONS_PER_HOUR}")

    def _load_config(self):
        """Load additional configuration from file"""
        try:
            with open(self.config_file) as f:
                config = json.load(f)

            # Update configuration
            if "blocked_personas" in config:
                self.blocked_personas.update(config["blocked_personas"])

            if "critical_entropy" in config:
                self.CRITICAL_ENTROPY = config["critical_entropy"]

            logger.info(f"Loaded Guardian config from {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load Guardian config: {e}")

    def apply_constraints(self, identity_state: dict) -> tuple[bool, str]:
        """
        Apply Guardian constraints to proposed identity state.

        Args:
            identity_state: Dictionary containing:
                - persona: PersonaSignature or dict with persona info
                - entropy: Current entropy level
                - trinity_coherence: Trinity Framework coherence
                - phase: Identity phase

        Returns:
            Tuple of (allowed: bool, reason: str)
        """
        violations = []

        # Extract state information
        persona = identity_state.get("persona", {})
        entropy = identity_state.get("entropy", 0.5)
        trinity_coherence = identity_state.get("trinity_coherence", 1.0)
        identity_state.get("phase")

        # Extract glyphs
        if hasattr(persona, "glyphs"):
            glyphs = set(persona.glyphs)
            persona_name = persona.name
        elif isinstance(persona, dict):
            glyphs = set(persona.get("glyphs", []))
            persona_name = persona.get("name", "Unknown")
        else:
            glyphs = set()
            persona_name = "Unknown"

        # Check entropy limits
        if entropy > self.CRITICAL_ENTROPY:
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.ENTROPY_LIMIT,
                    severity=0.9,
                    description=f"Entropy {entropy:.2f} exceeds critical threshold {self.CRITICAL_ENTROPY}",
                    recommendation="Stabilize consciousness before identity shift",
                )
            )

        # Check Trinity coherence
        if trinity_coherence < self.MIN_COHERENCE_FOR_SHIFT:
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.COHERENCE_MINIMUM,
                    severity=0.8,
                    description=f"Trinity coherence {trinity_coherence:.2f} below minimum {self.MIN_COHERENCE_FOR_SHIFT}",
                    recommendation="Restore Trinity Framework alignment",
                )
            )

        # Check for conflicting glyphs
        conflict_found = self._check_glyph_conflicts(glyphs)
        if conflict_found:
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.GLYPH_CONFLICT,
                    severity=0.7,
                    description=f"Conflicting glyph combination detected: {conflict_found}",
                    recommendation="Remove conflicting symbolic elements",
                )
            )

        # Check transformation rate
        rate_violation = self._check_transformation_rate()
        if rate_violation:
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.RAPID_TRANSFORMATION,
                    severity=0.6,
                    description=rate_violation,
                    recommendation="Allow identity to stabilize before next transformation",
                )
            )

        # Check if persona is blocked
        if persona_name in self.blocked_personas:
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.ETHICAL_BOUNDARY,
                    severity=1.0,
                    description=f"Persona '{persona_name}' is ethically blocked",
                    recommendation="Choose alternative identity path",
                )
            )

        # Check Trinity violation
        trinity_glyphs = {"⚛️", "🧠", "🛡️"}
        if trinity_coherence > 0.8 and not any(g in glyphs for g in trinity_glyphs):
            violations.append(
                ConstraintViolation(
                    constraint_type=ConstraintType.TRINITY_VIOLATION,
                    severity=0.5,
                    description="High Trinity coherence requires Trinity glyph presence",
                    recommendation="Include at least one Trinity Framework glyph",
                )
            )

        # Determine if transformation is allowed
        if not violations:
            # Record successful transformation
            self.transformation_history.append(time.time())
            return True, "Identity transformation approved by Guardian"

        # Find most severe violation
        most_severe = max(violations, key=lambda v: v.severity)

        # Log all violations
        logger.warning(f"🚫 Guardian blocked transformation: {len(violations)} violations")
        for v in violations:
            logger.warning(f"   - {v.constraint_type.value}: {v.description}")

        # Return rejection with reason
        reason = f"{most_severe.description}. {most_severe.recommendation}"
        return False, reason

    def _check_glyph_conflicts(self, glyphs: set[str]) -> Optional[str]:
        """Check for conflicting glyph combinations"""
        for conflict_set1, conflict_set2 in self.CONFLICTING_GLYPHS:
            if glyphs.intersection(conflict_set1) and glyphs.intersection(conflict_set2):
                conflict1 = next(iter(glyphs.intersection(conflict_set1)))
                conflict2 = next(iter(glyphs.intersection(conflict_set2)))
                return f"{conflict1} conflicts with {conflict2}"
        return None

    def _check_transformation_rate(self) -> Optional[str]:
        """Check if transformation rate is too high"""
        current_time = time.time()
        hour_ago = current_time - 3600

        # Clean old entries
        self.transformation_history = [t for t in self.transformation_history if t > hour_ago]

        # Check rate
        if len(self.transformation_history) >= self.MAX_TRANSFORMATIONS_PER_HOUR:
            return f"Transformation rate exceeds {self.MAX_TRANSFORMATIONS_PER_HOUR}/hour limit"

        return None

    def check_trusthelix_consent(self, identity_state: dict) -> bool:
        """
        Check TrustHelix for consent on high-impact identity shifts.

        Args:
            identity_state: Current identity state

        Returns:
            True if consent granted or not required
        """
        # Determine if this is a high-impact shift
        entropy = identity_state.get("entropy", 0.5)

        # High-impact criteria
        if entropy > 0.7:
            logger.info("🔐 High-impact identity shift requires TrustHelix consent")

            # In production, this would check actual TrustHelix
            # For now, we'll simulate based on entropy
            consent_probability = 1.0 - entropy
            consent_granted = consent_probability > 0.3

            if consent_granted:
                logger.info("✅ TrustHelix consent granted")
            else:
                logger.warning("❌ TrustHelix consent denied")

            return consent_granted

        # Low-impact shifts don't need explicit consent
        return True

    def get_safe_fallback_persona(self) -> dict:
        """Get a safe fallback persona when constraints are violated"""
        return {
            "name": "The Guardian",
            "glyphs": ["🛡️", "👁️", "⚡"],
            "dominant_traits": ["protective", "vigilant", "decisive"],
            "emotional_resonance": ["responsibility", "caution", "strength"],
            "drift_thresholds": {"min": 0.2, "max": 0.5},
        }

    def calculate_transformation_risk(self, current_state: dict, target_state: dict) -> float:
        """
        Calculate risk score for a transformation (0.0-1.0).

        Args:
            current_state: Current identity state
            target_state: Proposed new state

        Returns:
            Risk score where 0.0 is safe and 1.0 is maximum risk
        """
        risk_factors = []

        # Entropy jump risk
        current_entropy = current_state.get("entropy", 0.5)
        target_entropy = target_state.get("entropy", 0.5)
        entropy_jump = abs(target_entropy - current_entropy)
        risk_factors.append(min(1.0, entropy_jump * 2))

        # Coherence drop risk
        current_coherence = current_state.get("trinity_coherence", 1.0)
        target_coherence = target_state.get("trinity_coherence", 1.0)
        coherence_drop = max(0, current_coherence - target_coherence)
        risk_factors.append(coherence_drop)

        # Glyph divergence risk
        current_glyphs = set(current_state.get("glyphs", []))
        target_glyphs = set(target_state.get("glyphs", []))

        if current_glyphs and target_glyphs:
            overlap = len(current_glyphs.intersection(target_glyphs))
            total = len(current_glyphs.union(target_glyphs))
            divergence = 1.0 - (overlap / total) if total > 0 else 1.0
            risk_factors.append(divergence)

        # Transformation rate risk
        recent_transformations = len([t for t in self.transformation_history if t > time.time() - 3600])
        rate_risk = recent_transformations / self.MAX_TRANSFORMATIONS_PER_HOUR
        risk_factors.append(rate_risk)

        # Calculate weighted average
        total_risk = sum(risk_factors) / len(risk_factors) if risk_factors else 0.0

        return min(1.0, total_risk)

    def generate_constraint_report(self) -> dict:
        """Generate a report of Guardian constraint activity"""
        current_time = time.time()
        hour_ago = current_time - 3600
        day_ago = current_time - 86400

        hour_transformations = len([t for t in self.transformation_history if t > hour_ago])

        day_transformations = len([t for t in self.transformation_history if t > day_ago])

        return {
            "guardian_status": "active",
            "entropy_limit": self.CRITICAL_ENTROPY,
            "coherence_minimum": self.MIN_COHERENCE_FOR_SHIFT,
            "transformation_limit_per_hour": self.MAX_TRANSFORMATIONS_PER_HOUR,
            "transformations_last_hour": hour_transformations,
            "transformations_last_day": day_transformations,
            "blocked_personas": list(self.blocked_personas),
            "constraint_types": [ct.value for ct in ConstraintType],
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


# Example usage for testing
if __name__ == "__main__":
    print("🛡️ Guardian Shadow Filter Test")
    print("=" * 50)

    # Create Guardian filter
    guardian = GuardianShadowFilter()

    # Test various identity states
    test_states = [
        {
            "name": "Normal transition",
            "persona": {"name": "The Navigator", "glyphs": ["🧭", "🧠", "🌌"]},
            "entropy": 0.5,
            "trinity_coherence": 0.8,
            "phase": "crystallizing",
        },
        {
            "name": "High entropy",
            "persona": {"name": "The Phoenix", "glyphs": ["🔥", "🦅", "🌅"]},
            "entropy": 0.95,
            "trinity_coherence": 0.4,
            "phase": "collapse",
        },
        {
            "name": "Conflicting glyphs",
            "persona": {"name": "The Paradox", "glyphs": ["🔥", "❄️", "💥"]},
            "entropy": 0.6,
            "trinity_coherence": 0.5,
            "phase": "morphing",
        },
        {
            "name": "Low coherence",
            "persona": {"name": "The Void Walker", "glyphs": ["⚫", "🕳️", "🌌"]},
            "entropy": 0.7,
            "trinity_coherence": 0.2,
            "phase": "transcendent",
        },
    ]

    for state in test_states:
        print(f"\nTesting: {state['name']}")
        allowed, reason = guardian.apply_constraints(state)
        print(f"Allowed: {'✅' if allowed else '❌'}")
        print(f"Reason: {reason}")

        # Calculate risk
        if allowed:
            risk = guardian.calculate_transformation_risk(
                {"entropy": 0.3, "trinity_coherence": 1.0, "glyphs": ["⚛️", "🧠", "🛡️"]},
                state,
            )
            print(f"Risk score: {risk:.2%}")

    # Show report
    print("\n" + "=" * 50)
    print("Guardian Activity Report:")
    report = guardian.generate_constraint_report()
    for key, value in report.items():
        print(f"  {key}: {value}")
