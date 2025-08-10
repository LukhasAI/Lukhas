"""
══════════════════════════════════════════════════════════════════════════════════
║ 🛡️ LUKHAS AI - BIO-SYMBOLIC FALLBACK SYSTEMS
║ Comprehensive fallback mechanisms ensuring system resilience
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠══════════════════════════════════════════════════════════════════════════════════
║ Module: fallback_systems.py
║ Path: bio/symbolic/fallback_systems.py
║ Version: 1.0.0 | Created: 2025-07-28
║ Authors: LUKHAS Bio-Symbolic Team | Claude Code
╚══════════════════════════════════════════════════════════════════════════════════
"""

import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("ΛTRACE.bio.fallback")


class FallbackLevel(Enum):
    """Fallback severity levels."""

    MINIMAL = "minimal"  # Basic functionality preserved
    MODERATE = "moderate"  # Reduced functionality
    SEVERE = "severe"  # Emergency mode
    CRITICAL = "critical"  # Last resort


class FallbackReason(Enum):
    """Reasons for triggering fallbacks."""

    COLONY_FAILURE = "colony_failure"
    DATA_CORRUPTION = "data_corruption"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    DEPENDENCY_UNAVAILABLE = "dependency_unavailable"
    MEMORY_EXHAUSTION = "memory_exhaustion"
    NETWORK_FAILURE = "network_failure"
    QUANTUM_DECOHERENCE = "quantum_decoherence"


@dataclass
class FallbackEvent:
    """Record of a fallback activation."""

    timestamp: datetime
    level: FallbackLevel
    reason: FallbackReason
    component: str
    original_error: str
    fallback_action: str
    recovery_time_ms: Optional[float] = None
    success: bool = True


class BioSymbolicFallbackManager:
    """
    Comprehensive fallback management for bio-symbolic processing.
    Ensures system continues operating even under adverse conditions.
    """

    def __init__(self):
        self.fallback_history = deque(maxlen=1000)
        self.component_health = defaultdict(lambda: 1.0)
        self.fallback_strategies = self._initialize_fallback_strategies()
        self.emergency_values = self._initialize_emergency_values()
        self.circuit_breakers = defaultdict(
            lambda: {"failures": 0, "last_failure": None}
        )

        # Fallback thresholds
        self.thresholds = {
            "coherence_minimum": 0.3,
            "processing_time_max_ms": 50,
            "memory_usage_max_mb": 512,
            "error_rate_max": 0.1,
            "circuit_breaker_threshold": 5,
        }

        # Service registry for hub functionality
        self.services: Dict[str, Any] = {}

        logger.info("🛡️ BioSymbolicFallbackManager initialized")

    def register_service(self, name: str, service: Any) -> None:
        """Register a service with the hub"""
        self.services[name] = service
        logger.debug(f"🛡️ Registered service '{name}' with fallback manager")

    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service"""
        return self.services.get(name)

    def _initialize_fallback_strategies(
        self,
    ) -> Dict[str, Dict[FallbackLevel, Callable]]:
        """Initialize fallback strategies for each component."""
        return {
            "preprocessing": {
                FallbackLevel.MINIMAL: self._fallback_preprocessing_minimal,
                FallbackLevel.MODERATE: self._fallback_preprocessing_moderate,
                FallbackLevel.SEVERE: self._fallback_preprocessing_severe,
                FallbackLevel.CRITICAL: self._fallback_preprocessing_critical,
            },
            "thresholds": {
                FallbackLevel.MINIMAL: self._fallback_thresholds_minimal,
                FallbackLevel.MODERATE: self._fallback_thresholds_moderate,
                FallbackLevel.SEVERE: self._fallback_thresholds_severe,
                FallbackLevel.CRITICAL: self._fallback_thresholds_critical,
            },
            "mapping": {
                FallbackLevel.MINIMAL: self._fallback_mapping_minimal,
                FallbackLevel.MODERATE: self._fallback_mapping_moderate,
                FallbackLevel.SEVERE: self._fallback_mapping_severe,
                FallbackLevel.CRITICAL: self._fallback_mapping_critical,
            },
            "filtering": {
                FallbackLevel.MINIMAL: self._fallback_filtering_minimal,
                FallbackLevel.MODERATE: self._fallback_filtering_moderate,
                FallbackLevel.SEVERE: self._fallback_filtering_severe,
                FallbackLevel.CRITICAL: self._fallback_filtering_critical,
            },
            "orchestrator": {
                FallbackLevel.MINIMAL: self._fallback_orchestrator_minimal,
                FallbackLevel.MODERATE: self._fallback_orchestrator_moderate,
                FallbackLevel.SEVERE: self._fallback_orchestrator_severe,
                FallbackLevel.CRITICAL: self._fallback_orchestrator_critical,
            },
        }

    def _initialize_emergency_values(self) -> Dict[str, Any]:
        """Initialize emergency fallback values."""
        return {
            "coherence_metrics": {
                "overall_coherence": 0.5,
                "preprocessing_quality": 0.7,
                "threshold_confidence": 0.6,
                "mapping_confidence": 0.5,
                "anomaly_confidence": 0.6,
                "quantum_alignment": 0.4,
                "colony_consensus": 0.5,
                "temporal_stability": 0.6,
            },
            "bio_data_defaults": {
                "heart_rate": 70,
                "temperature": 37.0,
                "energy_level": 0.5,
                "cortisol": 10,
                "ph": 7.4,
                "glucose": 100,
                "atp_level": 0.6,
            },
            "glyph_mappings": {
                "primary_glyph": ("ΛHOMEO_BALANCED", 0.6),
                "active_glyphs": [("ΛHOMEO_BALANCED", 0.6)],
                "glyph_probabilities": {"ΛHOMEO_BALANCED": 0.6},
            },
            "processing_results": {
                "quality_assessment": "MODERATE",
                "processing_time_ms": 5.0,
                "timestamp": None,  # Will be set dynamically
                "fallback_mode": True,
            },
        }

    async def handle_component_failure(
        self,
        component: str,
        error: Exception,
        context: Dict[str, Any],
        original_task: str,
    ) -> Dict[str, Any]:
        """
        Handle component failure with appropriate fallback strategy.

        Args:
            component: Name of failed component
            error: Original error that triggered fallback
            context: Processing context
            original_task: Original task that failed

        Returns:
            Fallback result that maintains system functionality
        """
        start_time = datetime.utcnow()

        # Determine fallback level based on error severity and component health
        fallback_level = self._determine_fallback_level(component, error, context)
        reason = self._determine_fallback_reason(error)

        logger.warning(
            f"🛡️ Activating {fallback_level.value} fallback for {component}: {str(error)[:100]}"
        )

        # Check circuit breaker
        if self._should_circuit_break(component):
            fallback_level = FallbackLevel.CRITICAL
            logger.error(f"🔴 Circuit breaker activated for {component}")

        # Execute fallback strategy
        try:
            fallback_strategy = self.fallback_strategies[component][fallback_level]
            fallback_result = await fallback_strategy(context, original_task, error)

            # Calculate recovery time
            recovery_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Record fallback event
            fallback_event = FallbackEvent(
                timestamp=start_time,
                level=fallback_level,
                reason=reason,
                component=component,
                original_error=str(error),
                fallback_action=fallback_strategy.__name__,
                recovery_time_ms=recovery_time,
                success=True,
            )

            self.fallback_history.append(fallback_event)

            # Update component health
            self._update_component_health(component, fallback_level, success=True)

            # Add fallback metadata to result
            fallback_result["fallback_metadata"] = {
                "activated": True,
                "level": fallback_level.value,
                "reason": reason.value,
                "recovery_time_ms": recovery_time,
                "original_error": str(error),
            }

            logger.info(
                f"✅ Fallback recovery successful for {component} in {recovery_time:.1f}ms"
            )

            return fallback_result

        except Exception as fallback_error:
            # Fallback itself failed - escalate to critical
            logger.error(f"❌ Fallback failed for {component}: {str(fallback_error)}")

            recovery_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            fallback_event = FallbackEvent(
                timestamp=start_time,
                level=fallback_level,
                reason=reason,
                component=component,
                original_error=str(error),
                fallback_action=f"FAILED_{fallback_strategy.__name__}",
                recovery_time_ms=recovery_time,
                success=False,
            )

            self.fallback_history.append(fallback_event)

            # Escalate to critical fallback
            return await self._critical_system_fallback(
                component, context, original_task
            )

    def _determine_fallback_level(
        self, component: str, error: Exception, context: Dict[str, Any]
    ) -> FallbackLevel:
        """Determine appropriate fallback level based on error and component health."""
        component_health = self.component_health[component]

        # Critical errors always trigger severe/critical fallback
        critical_errors = (ImportError, MemoryError, SystemError)
        if isinstance(error, critical_errors):
            return FallbackLevel.CRITICAL

        # Component health-based escalation
        if component_health < 0.3:
            return FallbackLevel.CRITICAL
        elif component_health < 0.5:
            return FallbackLevel.SEVERE
        elif component_health < 0.7:
            return FallbackLevel.MODERATE
        else:
            return FallbackLevel.MINIMAL

    def _determine_fallback_reason(self, error: Exception) -> FallbackReason:
        """Determine the reason for fallback based on error type."""
        error_type = type(error).__name__

        error_mapping = {
            "ImportError": FallbackReason.DEPENDENCY_UNAVAILABLE,
            "ModuleNotFoundError": FallbackReason.DEPENDENCY_UNAVAILABLE,
            "MemoryError": FallbackReason.MEMORY_EXHAUSTION,
            "TimeoutError": FallbackReason.PERFORMANCE_DEGRADATION,
            "ConnectionError": FallbackReason.NETWORK_FAILURE,
            "ValueError": FallbackReason.DATA_CORRUPTION,
            "KeyError": FallbackReason.DATA_CORRUPTION,
            "AttributeError": FallbackReason.COLONY_FAILURE,
        }

        return error_mapping.get(error_type, FallbackReason.COLONY_FAILURE)

    def _should_circuit_break(self, component: str) -> bool:
        """Check if circuit breaker should activate for component."""
        breaker = self.circuit_breakers[component]

        if breaker["failures"] >= self.thresholds["circuit_breaker_threshold"]:
            # Check if enough time has passed for recovery attempt
            if breaker["last_failure"]:
                time_since_failure = datetime.utcnow() - breaker["last_failure"]
                if time_since_failure < timedelta(minutes=5):
                    return True

        return False

    def _update_component_health(
        self, component: str, fallback_level: FallbackLevel, success: bool
    ):
        """Update component health based on fallback outcome."""
        current_health = self.component_health[component]

        if success:
            # Gradual recovery
            recovery_factor = {
                FallbackLevel.MINIMAL: 0.95,
                FallbackLevel.MODERATE: 0.9,
                FallbackLevel.SEVERE: 0.8,
                FallbackLevel.CRITICAL: 0.7,
            }[fallback_level]

            self.component_health[component] = min(
                current_health + 0.1, recovery_factor
            )

            # Reset circuit breaker on success
            if self.component_health[component] > 0.8:
                self.circuit_breakers[component] = {"failures": 0, "last_failure": None}
        else:
            # Degrade health
            degradation = {
                FallbackLevel.MINIMAL: 0.1,
                FallbackLevel.MODERATE: 0.2,
                FallbackLevel.SEVERE: 0.3,
                FallbackLevel.CRITICAL: 0.4,
            }[fallback_level]

            self.component_health[component] = max(current_health - degradation, 0.1)

            # Update circuit breaker
            self.circuit_breakers[component]["failures"] += 1
            self.circuit_breakers[component]["last_failure"] = datetime.utcnow()

    # Preprocessing Fallback Strategies
    async def _fallback_preprocessing_minimal(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Minimal preprocessing fallback - use simple validation."""
        bio_data = context.get("bio_data", {})

        # Simple range validation without advanced processing
        validated_data = {}
        for key, value in bio_data.items():
            if isinstance(value, (int, float)):
                # Simple clipping to reasonable ranges
                if key == "heart_rate":
                    validated_data[key] = max(40, min(value, 200))
                elif key == "temperature":
                    validated_data[key] = max(35.0, min(value, 42.0))
                else:
                    validated_data[key] = value
            else:
                validated_data[key] = self.emergency_values["bio_data_defaults"].get(
                    key, 0.5
                )

        return {
            "task_id": task_id,
            "preprocessed_data": validated_data,
            "quality_score": 0.6,
            "quality_tag": "ΛQUALITY_FALLBACK_MINIMAL",
            "outlier_scores": dict.fromkeys(validated_data.keys(), 0.1),
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "preprocessing_fallback",
        }

    async def _fallback_preprocessing_moderate(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Moderate preprocessing fallback - use statistical methods."""
        bio_data = context.get("bio_data", {})

        # Use mean/median imputation for missing values
        validated_data = {}
        for key, value in bio_data.items():
            if value is None or (isinstance(value, str) and not value.isdigit()):
                validated_data[key] = self.emergency_values["bio_data_defaults"][key]
            else:
                validated_data[key] = float(value)

        # Simple outlier detection using IQR method
        outlier_scores = {}
        for key, value in validated_data.items():
            # Simplified outlier detection
            expected = self.emergency_values["bio_data_defaults"][key]
            deviation = (
                abs(value - expected) / expected if expected != 0 else abs(value)
            )
            outlier_scores[key] = min(deviation, 1.0)

        return {
            "task_id": task_id,
            "preprocessed_data": validated_data,
            "quality_score": 0.5,
            "quality_tag": "ΛQUALITY_FALLBACK_MODERATE",
            "outlier_scores": outlier_scores,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "preprocessing_fallback",
        }

    async def _fallback_preprocessing_severe(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Severe preprocessing fallback - use emergency defaults."""
        # Use all emergency default values
        validated_data = self.emergency_values["bio_data_defaults"].copy()

        return {
            "task_id": task_id,
            "preprocessed_data": validated_data,
            "quality_score": 0.3,
            "quality_tag": "ΛQUALITY_FALLBACK_SEVERE",
            "outlier_scores": dict.fromkeys(validated_data.keys(), 0.5),
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "preprocessing_fallback",
        }

    async def _fallback_preprocessing_critical(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Critical preprocessing fallback - absolute minimum."""
        return {
            "task_id": task_id,
            "preprocessed_data": {"heart_rate": 70},
            "quality_score": 0.1,
            "quality_tag": "ΛQUALITY_FALLBACK_CRITICAL",
            "outlier_scores": {"heart_rate": 0.8},
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "preprocessing_fallback",
        }

    # Threshold Fallback Strategies
    async def _fallback_thresholds_minimal(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Minimal threshold fallback - use static thresholds."""
        return {
            "task_id": task_id,
            "thresholds": {
                "tier1": {"heart_rate": {"low": 0.3, "high": 0.7, "critical": 0.9}},
                "tier2": {"stress_state": {"low": 0.4, "high": 0.7, "critical": 0.85}},
                "tier3": {"coherence": {"low": 0.5, "high": 0.7, "critical": 0.85}},
                "tier4": {"entanglement": {"low": 0.6, "high": 0.8, "critical": 0.95}},
            },
            "confidence": 0.6,
            "context_modifiers": {},
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "thresholds_fallback",
        }

    async def _fallback_thresholds_moderate(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Moderate threshold fallback - conservative thresholds."""
        return {
            "task_id": task_id,
            "thresholds": {
                "tier1": {"heart_rate": {"low": 0.4, "high": 0.6, "critical": 0.8}}
            },
            "confidence": 0.4,
            "context_modifiers": {},
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "thresholds_fallback",
        }

    async def _fallback_thresholds_severe(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Severe threshold fallback - very conservative."""
        return {
            "task_id": task_id,
            "thresholds": {
                "tier1": {"heart_rate": {"low": 0.5, "high": 0.5, "critical": 0.7}}
            },
            "confidence": 0.2,
            "context_modifiers": {},
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "thresholds_fallback",
        }

    async def _fallback_thresholds_critical(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Critical threshold fallback - emergency mode."""
        return {
            "task_id": task_id,
            "thresholds": {"tier1": {}},
            "confidence": 0.1,
            "context_modifiers": {},
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "thresholds_fallback",
        }

    # Mapping Fallback Strategies
    async def _fallback_mapping_minimal(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Minimal mapping fallback - simple rule-based mapping."""
        bio_data = context.get("bio_data", {})

        # Simple rule-based GLYPH selection
        primary_glyph = ("ΛHOMEO_BALANCED", 0.6)

        if "heart_rate" in bio_data:
            hr = bio_data["heart_rate"]
            if hr > 100:
                primary_glyph = ("ΛRHYTHM_ACTIVE", 0.7)
            elif hr < 60:
                primary_glyph = ("ΛRHYTHM_DEEP", 0.7)

        return {
            "task_id": task_id,
            "primary_glyph": primary_glyph,
            "active_glyphs": [primary_glyph],
            "glyph_probabilities": {primary_glyph[0]: primary_glyph[1]},
            "context_features": {"fallback": "minimal"},
            "confidence": 0.6,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "mapping_fallback",
        }

    async def _fallback_mapping_moderate(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Moderate mapping fallback - default balanced state."""
        return {
            "task_id": task_id,
            "primary_glyph": ("ΛHOMEO_BALANCED", 0.5),
            "active_glyphs": [("ΛHOMEO_BALANCED", 0.5)],
            "glyph_probabilities": {"ΛHOMEO_BALANCED": 0.5},
            "context_features": {"fallback": "moderate"},
            "confidence": 0.4,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "mapping_fallback",
        }

    async def _fallback_mapping_severe(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Severe mapping fallback - minimal GLYPH."""
        return {
            "task_id": task_id,
            "primary_glyph": ("ΛPOWER_CONSERVE", 0.3),
            "active_glyphs": [("ΛPOWER_CONSERVE", 0.3)],
            "glyph_probabilities": {"ΛPOWER_CONSERVE": 0.3},
            "context_features": {"fallback": "severe"},
            "confidence": 0.2,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "mapping_fallback",
        }

    async def _fallback_mapping_critical(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Critical mapping fallback - emergency GLYPH."""
        return {
            "task_id": task_id,
            "primary_glyph": None,
            "active_glyphs": [],
            "glyph_probabilities": {},
            "context_features": {"fallback": "critical"},
            "confidence": 0.1,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "mapping_fallback",
        }

    # Filtering Fallback Strategies
    async def _fallback_filtering_minimal(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Minimal filtering fallback - assume no anomalies."""
        bio_data = context.get("bio_data", {})

        return {
            "task_id": task_id,
            "anomalies_detected": False,
            "anomaly_count": 0,
            "anomaly_details": [],
            "recovered_data": bio_data,
            "detection_confidence": 0.6,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "filtering_fallback",
        }

    async def _fallback_filtering_moderate(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Moderate filtering fallback - conservative anomaly detection."""
        bio_data = context.get("bio_data", {})

        return {
            "task_id": task_id,
            "anomalies_detected": True,
            "anomaly_count": 1,
            "anomaly_details": [{"type": "UNKNOWN", "severity": 0.3}],
            "recovered_data": bio_data,
            "detection_confidence": 0.4,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "filtering_fallback",
        }

    async def _fallback_filtering_severe(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Severe filtering fallback - assume anomalies present."""
        return {
            "task_id": task_id,
            "anomalies_detected": True,
            "anomaly_count": 3,
            "anomaly_details": [
                {"type": "SYSTEM_ERROR", "severity": 0.8},
                {"type": "DATA_QUALITY", "severity": 0.6},
                {"type": "PROCESSING_ERROR", "severity": 0.7},
            ],
            "recovered_data": self.emergency_values["bio_data_defaults"],
            "detection_confidence": 0.2,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "filtering_fallback",
        }

    async def _fallback_filtering_critical(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Critical filtering fallback - system failure mode."""
        return {
            "task_id": task_id,
            "anomalies_detected": True,
            "anomaly_count": 99,
            "anomaly_details": [{"type": "SYSTEM_FAILURE", "severity": 1.0}],
            "recovered_data": {},
            "detection_confidence": 0.1,
            "timestamp": datetime.utcnow().isoformat(),
            "colony_id": "filtering_fallback",
        }

    # Orchestrator Fallback Strategies
    async def _fallback_orchestrator_minimal(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Minimal orchestrator fallback - use emergency coherence values."""
        coherence_metrics = self.emergency_values["coherence_metrics"].copy()

        # Create CoherenceMetrics-like object
        class FallbackCoherenceMetrics:
            def __init__(self, values):
                for key, value in values.items():
                    setattr(self, key, value)

        return {
            "task_id": task_id,
            "coherence_metrics": FallbackCoherenceMetrics(coherence_metrics),
            "bio_symbolic_state": self.emergency_values["glyph_mappings"].copy(),
            "colony_results": {"fallback": "orchestrator_minimal"},
            "processing_time_ms": 5.0,
            "pipeline_config": {"fallback_mode": True},
            "quality_assessment": "MODERATE",
            "recommendations": ["System in fallback mode - check component health"],
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": "orchestrator_fallback",
        }

    async def _fallback_orchestrator_moderate(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Moderate orchestrator fallback - reduced functionality."""
        coherence_values = self.emergency_values["coherence_metrics"].copy()
        for key in coherence_values:
            coherence_values[key] *= 0.8  # Reduce all coherence values

        class FallbackCoherenceMetrics:
            def __init__(self, values):
                for key, value in values.items():
                    setattr(self, key, value)

        return {
            "task_id": task_id,
            "coherence_metrics": FallbackCoherenceMetrics(coherence_values),
            "bio_symbolic_state": {"primary_glyph": None, "active_glyphs": []},
            "colony_results": {"fallback": "orchestrator_moderate"},
            "processing_time_ms": 8.0,
            "pipeline_config": {"fallback_mode": True},
            "quality_assessment": "POOR",
            "recommendations": ["System degraded - immediate attention required"],
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": "orchestrator_fallback",
        }

    async def _fallback_orchestrator_severe(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Severe orchestrator fallback - emergency mode."""
        coherence_values = dict.fromkeys(
            self.emergency_values["coherence_metrics"], 0.2
        )

        class FallbackCoherenceMetrics:
            def __init__(self, values):
                for key, value in values.items():
                    setattr(self, key, value)

        return {
            "task_id": task_id,
            "coherence_metrics": FallbackCoherenceMetrics(coherence_values),
            "bio_symbolic_state": {"emergency_mode": True},
            "colony_results": {"fallback": "orchestrator_severe"},
            "processing_time_ms": 15.0,
            "pipeline_config": {"fallback_mode": True, "emergency_mode": True},
            "quality_assessment": "CRITICAL",
            "recommendations": ["EMERGENCY: System failure - restart required"],
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": "orchestrator_fallback",
        }

    async def _fallback_orchestrator_critical(
        self, context: Dict[str, Any], task_id: str, error: Exception
    ) -> Dict[str, Any]:
        """Critical orchestrator fallback - last resort."""

        class FallbackCoherenceMetrics:
            overall_coherence = 0.1
            preprocessing_quality = 0.1
            threshold_confidence = 0.1
            mapping_confidence = 0.1
            anomaly_confidence = 0.1
            quantum_alignment = 0.1
            colony_consensus = 0.1
            temporal_stability = 0.1

        return {
            "task_id": task_id,
            "coherence_metrics": FallbackCoherenceMetrics(),
            "bio_symbolic_state": {"system_failure": True},
            "colony_results": {"fallback": "orchestrator_critical"},
            "processing_time_ms": 30.0,
            "pipeline_config": {"fallback_mode": True, "critical_failure": True},
            "quality_assessment": "SYSTEM_FAILURE",
            "recommendations": [
                "CRITICAL SYSTEM FAILURE - IMMEDIATE INTERVENTION REQUIRED"
            ],
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_id": "orchestrator_fallback_critical",
        }

    async def _critical_system_fallback(
        self, component: str, context: Dict[str, Any], task_id: str
    ) -> Dict[str, Any]:
        """Last resort system fallback when all else fails."""
        logger.critical(f"🚨 CRITICAL SYSTEM FALLBACK activated for {component}")

        return {
            "task_id": task_id,
            "system_status": "CRITICAL_FAILURE",
            "component": component,
            "fallback_metadata": {
                "activated": True,
                "level": "CRITICAL_SYSTEM_FAILURE",
                "reason": "ALL_FALLBACKS_FAILED",
                "timestamp": datetime.utcnow().isoformat(),
            },
            "emergency_response": "SYSTEM_SHUTDOWN_RECOMMENDED",
            "contact_support": True,
        }

    def get_system_health_report(self) -> Dict[str, Any]:
        """Generate comprehensive system health report."""
        total_fallbacks = len(self.fallback_history)
        recent_fallbacks = [
            event
            for event in self.fallback_history
            if event.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]

        fallback_by_level = defaultdict(int)
        fallback_by_component = defaultdict(int)

        for event in self.fallback_history:
            fallback_by_level[event.level.value] += 1
            fallback_by_component[event.component] += 1

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": (
                min(self.component_health.values()) if self.component_health else 1.0
            ),
            "component_health": dict(self.component_health),
            "total_fallbacks": total_fallbacks,
            "recent_fallbacks_1h": len(recent_fallbacks),
            "fallbacks_by_level": dict(fallback_by_level),
            "fallbacks_by_component": dict(fallback_by_component),
            "circuit_breakers": {
                component: data["failures"]
                for component, data in self.circuit_breakers.items()
                if data["failures"] > 0
            },
            "recommendations": self._generate_health_recommendations(),
        }

    def _generate_health_recommendations(self) -> List[str]:
        """Generate health recommendations based on system state."""
        recommendations = []

        # Check component health
        for component, health in self.component_health.items():
            if health < 0.3:
                recommendations.append(
                    f"URGENT: {component} component health critical ({health:.1%})"
                )
            elif health < 0.5:
                recommendations.append(
                    f"WARNING: {component} component health degraded ({health:.1%})"
                )

        # Check circuit breakers
        for component, data in self.circuit_breakers.items():
            if data["failures"] >= self.thresholds["circuit_breaker_threshold"]:
                recommendations.append(
                    f"ALERT: Circuit breaker activated for {component}"
                )

        # Check recent fallback activity
        recent_fallbacks = [
            event
            for event in self.fallback_history
            if event.timestamp > datetime.utcnow() - timedelta(minutes=30)
        ]

        if len(recent_fallbacks) > 10:
            recommendations.append(
                "HIGH ALERT: Excessive fallback activity in last 30 minutes"
            )

        if not recommendations:
            recommendations.append("System health appears normal")

        return recommendations


# Global fallback manager instance
_fallback_manager = None


def get_fallback_manager() -> BioSymbolicFallbackManager:
    """Get the global fallback manager instance."""
    global _fallback_manager
    if _fallback_manager is None:
        _fallback_manager = BioSymbolicFallbackManager()
    return _fallback_manager
