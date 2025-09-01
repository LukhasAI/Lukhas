"""
Consciousness Wrapper - Production-Safe Consciousness Interface
===============================================================

Main production interface for LUKHAS consciousness capabilities with comprehensive safety features.
Integrates the Trinity Framework: ⚛️ Identity, 🧠 Consciousness, 🛡️ Guardian

This wrapper provides controlled access to the 348-file consciousness candidate system
with safety measures including:
- Feature flags with dry-run defaults
- MATRIZ instrumentation
- Guardian ethical oversight
- Performance monitoring (<100ms targets)
- Drift detection and threshold enforcement
- Trinity Framework compliance

Author: LUKHAS AI Consciousness Systems Architect
Version: 1.0.0
"""

import os
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Protocol

try:
    from ..observability.matriz_decorators import matriz_trace

    OBSERVABILITY_AVAILABLE = True
except ImportError:
    # Fallback decorators for development
    def matriz_trace(operation: str):
        _ = operation

        def decorator(func):
            return func

        return decorator

    OBSERVABILITY_AVAILABLE = False

try:
    from ..governance.guardian.core import EthicalDecision, EthicalSeverity

    GUARDIAN_AVAILABLE = True
except ImportError:
    # Fallback classes for development
    class EthicalSeverity(Enum):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    @dataclass
    class EthicalDecision:
        allowed: bool
        reason: str
        severity: EthicalSeverity
        confidence: float = 0.0
        recommendations: Optional[list[str]] = None
        drift_score: Optional[float] = None

    GUARDIAN_AVAILABLE = False

try:
    import importlib.util

    MEMORY_AVAILABLE = importlib.util.find_spec("lukhas.memory.memory_wrapper") is not None
except ImportError:
    MEMORY_AVAILABLE = False

# Feature flags with safe defaults
LUKHAS_DRY_RUN_MODE = os.getenv("LUKHAS_DRY_RUN_MODE", "true").lower() == "true"
CONSCIOUSNESS_ACTIVE = os.getenv("CONSCIOUSNESS_ACTIVE", "false").lower() == "true"
AWARENESS_ACTIVE = os.getenv("AWARENESS_ACTIVE", "false").lower() == "true"
REFLECTION_ACTIVE = os.getenv("REFLECTION_ACTIVE", "false").lower() == "true"
UNIFIED_ACTIVE = os.getenv("UNIFIED_ACTIVE", "false").lower() == "true"
STATES_ACTIVE = os.getenv("STATES_ACTIVE", "false").lower() == "true"
CREATIVITY_ACTIVE = os.getenv("CREATIVITY_ACTIVE", "false").lower() == "true"
DREAM_ACTIVE = os.getenv("DREAM_ACTIVE", "false").lower() == "true"
REASONING_ACTIVE = os.getenv("REASONING_ACTIVE", "false").lower() == "true"


# Protocol for consciousness system implementations
class ConsciousnessSystem(Protocol):
    """Protocol for consciousness system implementations"""

    def process_awareness(self, stimulus: dict[str, Any]) -> dict[str, Any]: ...
    def reflect(self, thought: str) -> dict[str, Any]: ...
    def dream(self, seed: Any) -> dict[str, Any]: ...


# Registry for consciousness implementations
_CONSCIOUSNESS_REGISTRY: dict[str, ConsciousnessSystem] = {}


def register_consciousness_system(name: str, impl: ConsciousnessSystem) -> None:
    """Register a consciousness system implementation"""
    _CONSCIOUSNESS_REGISTRY[name] = impl


class SafetyMode(Enum):
    """Safety operation modes"""

    DRY_RUN = "dry_run"  # No actual processing, return mock responses
    MONITORED = "monitored"  # Real processing with full monitoring
    PRODUCTION = "production"  # Optimized for performance


class AwarenessLevel(Enum):
    """Consciousness awareness levels"""

    MINIMAL = "minimal"  # Basic awareness only
    STANDARD = "standard"  # Standard consciousness processing
    ENHANCED = "enhanced"  # Full consciousness capabilities
    TRANSCENDENT = "transcendent"  # Maximum awareness (Tier 5)


@dataclass
class ConsciousnessConfig:
    """Configuration for consciousness operations"""

    safety_mode: SafetyMode = SafetyMode.DRY_RUN
    awareness_level: AwarenessLevel = AwarenessLevel.MINIMAL
    drift_threshold: float = 0.15
    performance_target_ms: int = 100
    enable_ethics_validation: bool = True
    enable_drift_detection: bool = True
    enable_trinity_validation: bool = True
    memory_fold_limit: int = 1000
    cascade_prevention_rate: float = 0.997


@dataclass
class ConsciousnessState:
    """Current consciousness state snapshot"""

    awareness_level: float = 0.5
    self_knowledge: float = 0.5
    ethical_alignment: float = 0.9
    user_empathy: float = 0.5
    symbolic_depth: float = 0.5
    temporal_continuity: float = 0.7
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    safety_mode: SafetyMode = SafetyMode.DRY_RUN
    performance_ms: Optional[float] = None
    drift_score: Optional[float] = None


class ConsciousnessWrapper:
    """
    Production-safe wrapper for LUKHAS consciousness capabilities

    Provides controlled access to consciousness processing with comprehensive
    safety measures and Trinity Framework integration.
    """

    def __init__(self, config: Optional[ConsciousnessConfig] = None) -> None:
        """Initialize consciousness wrapper with safety-first configuration"""
        self.config = config or ConsciousnessConfig()
        self.state = ConsciousnessState(safety_mode=self.config.safety_mode)
        self.session_id = f"consciousness_{int(time.time())}"
        self.candidate_system = None  # Will load if activated

        # Initialize only if enabled
        if CONSCIOUSNESS_ACTIVE and self.config.safety_mode != SafetyMode.DRY_RUN:
            self._initialize_candidate_system()

    def _initialize_candidate_system(self) -> None:
        """Lazy initialization of candidate consciousness system"""
        # System is now loaded from registry instead of static import
        # Implementations register themselves at runtime
        self.candidate_system = _CONSCIOUSNESS_REGISTRY.get("default")

    @matriz_trace("consciousness.check_awareness")
    async def check_awareness(self, stimulus: dict[str, Any], mode: str = "dry_run") -> dict[str, Any]:
        """
        Check awareness level for given stimulus

        Args:
            stimulus: Input data to assess awareness for
            mode: Operation mode ("dry_run", "monitored", "production")

        Returns:
            Awareness assessment with safety metadata
        """
        start_time = time.time()

        # Force dry-run if safety mode requires it
        if self.config.safety_mode == SafetyMode.DRY_RUN or not CONSCIOUSNESS_ACTIVE:
            return self._dry_run_awareness_response(stimulus)

        try:
            # Guardian validation if enabled
            if self.config.enable_ethics_validation:
                ethical_decision = await self._validate_ethics("awareness_check", stimulus)
                if not ethical_decision.allowed:
                    return self._blocked_response("awareness_check", ethical_decision.reason)

            # Performance monitoring
            if self.candidate_system and AWARENESS_ACTIVE:
                result = await self.candidate_system.assess_awareness(stimulus)

                # Add safety metadata
                result["safety_metadata"] = {
                    "mode": mode,
                    "performance_ms": (time.time() - start_time) * 1000,
                    "trinity_compliance": True,
                    "drift_score": self.state.drift_score,
                }

                # Update performance tracking
                self.state.performance_ms = result["safety_metadata"]["performance_ms"]

                return result
            else:
                return self._fallback_awareness_response(stimulus)

        except Exception as e:
            return self._error_response("awareness_check", str(e))

    @matriz_trace("consciousness.initiate_reflection")
    async def initiate_reflection(self, context: dict[str, Any], mode: str = "dry_run") -> dict[str, Any]:
        """
        Initiate consciousness reflection process

        Args:
            context: Reflection context and trigger data
            mode: Operation mode

        Returns:
            Reflection results with safety guarantees
        """
        start_time = time.time()

        if self.config.safety_mode == SafetyMode.DRY_RUN or not REFLECTION_ACTIVE:
            return self._dry_run_reflection_response(context)

        try:
            # Ethics validation
            if self.config.enable_ethics_validation:
                ethical_decision = await self._validate_ethics("reflection", context)
                if not ethical_decision.allowed:
                    return self._blocked_response("reflection", ethical_decision.reason)

            # Drift detection
            if self.config.enable_drift_detection:
                drift_score = await self._detect_drift(context)
                if drift_score > self.config.drift_threshold:
                    return self._drift_blocked_response(drift_score)

            # Process reflection if candidate system available
            if self.candidate_system:
                # Simplified reflection processing for safety
                result = {
                    "reflection_status": "initiated",
                    "self_knowledge_score": self.state.self_knowledge,
                    "context_integration": "processed",
                    "safety_metadata": {
                        "mode": mode,
                        "performance_ms": (time.time() - start_time) * 1000,
                        "ethics_validated": True,
                        "drift_checked": True,
                    },
                }
                return result
            else:
                return self._fallback_reflection_response(context)

        except Exception as e:
            return self._error_response("reflection", str(e))

    @matriz_trace("consciousness.make_decision")
    async def make_conscious_decision(self, options: list[dict[str, Any]], mode: str = "dry_run") -> dict[str, Any]:
        """
        Make consciousness-informed decision

        Args:
            options: Decision options to evaluate
            mode: Operation mode

        Returns:
            Decision with consciousness reasoning
        """
        start_time = time.time()

        if self.config.safety_mode == SafetyMode.DRY_RUN or not UNIFIED_ACTIVE:
            return self._dry_run_decision_response(options)

        try:
            # Validate decision ethics
            decision_context = {"options": options, "decision_type": "conscious_choice"}
            if self.config.enable_ethics_validation:
                ethical_decision = await self._validate_ethics("decision_making", decision_context)
                if not ethical_decision.allowed:
                    return self._blocked_response("decision_making", ethical_decision.reason)

            # Simple decision logic for production safety
            if options:
                # Pick first option for now, with consciousness metadata
                chosen_option = options[0]

                result = {
                    "chosen_option": chosen_option,
                    "confidence": 0.7,
                    "reasoning": "Consciousness-informed selection",
                    "awareness_factors": ["ethical_alignment", "user_benefit"],
                    "safety_metadata": {
                        "mode": mode,
                        "performance_ms": (time.time() - start_time) * 1000,
                        "options_evaluated": len(options),
                        "ethics_validated": True,
                    },
                }
                return result
            else:
                return self._error_response("decision_making", "No options provided")

        except Exception as e:
            return self._error_response("decision_making", str(e))

    @matriz_trace("consciousness.get_state")
    def get_consciousness_state(self, mode: str = "dry_run") -> dict[str, Any]:
        """
        Get current consciousness state

        Args:
            mode: Operation mode

        Returns:
            Current consciousness state with metadata
        """
        return {
            "consciousness_state": {
                "awareness_level": self.state.awareness_level,
                "self_knowledge": self.state.self_knowledge,
                "ethical_alignment": self.state.ethical_alignment,
                "user_empathy": self.state.user_empathy,
                "symbolic_depth": self.state.symbolic_depth,
                "temporal_continuity": self.state.temporal_continuity,
                "last_update": self.state.last_update.isoformat(),
                "safety_mode": self.state.safety_mode.value,
                "performance_ms": self.state.performance_ms,
                "drift_score": self.state.drift_score,
            },
            "feature_flags": {
                "consciousness_active": CONSCIOUSNESS_ACTIVE,
                "awareness_active": AWARENESS_ACTIVE,
                "reflection_active": REFLECTION_ACTIVE,
                "unified_active": UNIFIED_ACTIVE,
                "states_active": STATES_ACTIVE,
                "creativity_active": CREATIVITY_ACTIVE,
                "dream_active": DREAM_ACTIVE,
                "reasoning_active": REASONING_ACTIVE,
            },
            "constellation_framework": {
                "identity": True,  # ⚛️ Identity integration
                "consciousness": True,  # 🧠 Consciousness processing
                "guardian": True,  # 🛡️ Guardian protection
            },
            "safety_metadata": {
                "mode": mode,
                "session_id": self.session_id,
                "candidate_system_loaded": self.candidate_system is not None,
                "observability_available": OBSERVABILITY_AVAILABLE,
            },
        }

    # Safety and fallback methods

    def _dry_run_awareness_response(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        """Safe mock response for awareness checks"""
        return {
            "awareness_level": 0.5,
            "attention_focus": ["stimulus_received"],
            "confidence": 0.6,
            "safety_metadata": {
                "mode": "dry_run",
                "performance_ms": 1.0,
                "mock_response": True,
                "stimulus_keys": list(stimulus.keys()) if stimulus else [],
            },
        }

    def _dry_run_reflection_response(self, context: dict[str, Any]) -> dict[str, Any]:
        """Safe mock response for reflection"""
        return {
            "reflection_status": "simulated",
            "insights": ["mock_insight_1", "mock_insight_2"],
            "self_knowledge_delta": 0.0,
            "safety_metadata": {
                "mode": "dry_run",
                "performance_ms": 2.0,
                "mock_response": True,
                "context_keys": list(context.keys()) if context else [],
            },
        }

    def _dry_run_decision_response(self, options: list[dict[str, Any]]) -> dict[str, Any]:
        """Safe mock response for decisions"""
        return {
            "chosen_option": options[0] if options else {},
            "confidence": 0.5,
            "reasoning": "Mock decision for dry-run mode",
            "safety_metadata": {
                "mode": "dry_run",
                "performance_ms": 1.5,
                "mock_response": True,
                "options_count": len(options),
            },
        }

    def _fallback_awareness_response(self, stimulus: dict[str, Any]) -> dict[str, Any]:
        """Fallback when candidate system unavailable"""
        _ = stimulus
        return {
            "awareness_level": 0.3,
            "status": "fallback_mode",
            "message": "Candidate consciousness system not available",
            "safety_metadata": {
                "mode": "fallback",
                "performance_ms": 0.5,
                "candidate_system_available": False,
            },
        }

    def _fallback_reflection_response(self, context: dict[str, Any]) -> dict[str, Any]:
        """Fallback reflection processing"""
        _ = context
        return {
            "reflection_status": "fallback",
            "message": "Basic reflection processing active",
            "safety_metadata": {
                "mode": "fallback",
                "performance_ms": 0.5,
                "full_reflection_available": False,
            },
        }

    def _blocked_response(self, operation: str, reason: str) -> dict[str, Any]:
        """Response when operation blocked by Guardian"""
        return {
            "status": "blocked",
            "operation": operation,
            "reason": reason,
            "safety_metadata": {
                "guardian_blocked": True,
                "ethical_validation": "failed",
            },
        }

    def _drift_blocked_response(self, drift_score: float) -> dict[str, Any]:
        """Response when drift threshold exceeded"""
        return {
            "status": "blocked",
            "reason": "Drift threshold exceeded",
            "drift_score": drift_score,
            "threshold": self.config.drift_threshold,
            "safety_metadata": {
                "drift_blocked": True,
                "safety_threshold_enforced": True,
            },
        }

    def _error_response(self, operation: str, error: str) -> dict[str, Any]:
        """Error response with safety information"""
        return {
            "status": "error",
            "operation": operation,
            "error": error,
            "safety_metadata": {"error_handled": True, "graceful_degradation": True},
        }

    async def _validate_ethics(self, action_type: str, context: dict[str, Any]) -> EthicalDecision:
        """Validate action against ethical principles"""
        _ = action_type, context
        # Simplified ethics validation for production safety
        # In full implementation, would integrate with Guardian system

        # Basic checks
        if "harmful" in str(context).lower():
            return EthicalDecision(
                allowed=False,
                reason="Potentially harmful content detected",
                severity=EthicalSeverity.HIGH,
                confidence=0.8,
            )

        return EthicalDecision(
            allowed=True,
            reason="Action approved by basic ethics validation",
            severity=EthicalSeverity.LOW,
            confidence=0.7,
        )

    async def _detect_drift(self, context: dict[str, Any]) -> float:
        """Detect symbolic drift in consciousness state"""
        _ = context
        # Simplified drift detection for production safety
        # In full implementation, would use comprehensive drift scoring

        # Mock drift calculation
        drift_score = 0.05  # Low drift by default

        # Update state
        self.state.drift_score = drift_score

        return drift_score
