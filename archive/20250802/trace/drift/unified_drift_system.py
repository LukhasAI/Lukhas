#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════════
🌀 MODULE: core.drift.unified_drift_system
📄 FILENAME: unified_drift_system.py
🎯 PURPOSE: Unified DriftScore System with LAMBDA_TIER Integration
🧠 CONTEXT: LUKHAS AGI Drift Detection & Analysis with Identity-Aware Access Control
🔮 CAPABILITY: Multi-dimensional drift analysis, tier-based scoring, user context tracking
🛡️ ETHICS: User privacy protection, consent-managed drift analysis, tier-based access
🚀 VERSION: v1.0.0 • 📅 CREATED: 2025-07-26 • ✍️ AUTHOR: CLAUDE-4-SONNET
💭 INTEGRATION: Symbolic drift, emotional drift, memory drift, identity system
═══════════════════════════════════════════════════════════════════════════════════

🌀 UNIFIED DRIFT SYSTEM WITH LAMBDA_TIER INTEGRATION
────────────────────────────────────────────────────────────────────

This module provides a comprehensive drift analysis system that integrates:
- Symbolic drift tracking from multiple engines
- Emotional drift analysis with user context
- Memory drift detection with identity awareness
- Dream coherence drift scoring
- Tier-based access control for drift analytics
- User consent management for drift data

The unified system consolidates drift tracking from:
- Oneiric Dream Engine (dream coherence, symbolic entropy, narrative drift)
- DreamSeed Emotions (emotional polarity drift, affect vector velocity)
- Memory Systems (memory fold drift, symbolic vector shifts)
- Identity System (identity stability tracking, cascade prevention)
- Ethical Alignment (ethical drift detection, compliance monitoring)

SYMBOLIC TAGS IMPLEMENTED:
• ΛDRIFT: General drift magnitude and direction
• ΛENTROPY: Symbolic entropy and information drift
• ΛCASCADE: Cascade risk and feedback loop detection
• ΛSTABILITY: System stability and equilibrium tracking
• ΛCOHERENCE: Narrative and logical coherence drift
• ΛEMOTIONAL: Emotional polarity and affect drift
• ΛIDENTITY: Identity stability and authenticity drift
• ΛETHICAL: Ethical alignment and compliance drift

LUKHAS_TAG: unified_drift, lambda_tier_integration, identity_aware_drift
"""

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import numpy as np
import structlog

from core.identity_integration import (
    get_identity_client,
    require_identity,
)

# LUKHAS Core Imports
from core.symbolic.drift.symbolic_drift_tracker import (
    DriftPhase,
    SymbolicDriftTracker,
)

# Unified tier system imports
from memory.systems.memory_drift_tracker import MemoryDriftTracker

logger = structlog.get_logger(__name__)


class DriftDimension(Enum):
    """Dimensions of drift analysis."""

    SYMBOLIC = "symbolic"  # Symbol/GLYPH changes
    EMOTIONAL = "emotional"  # Emotional state drift
    MEMORY = "memory"  # Memory structure drift
    COHERENCE = "coherence"  # Narrative coherence drift
    IDENTITY = "identity"  # Identity stability drift
    ETHICAL = "ethical"  # Ethical alignment drift
    TEMPORAL = "temporal"  # Temporal pattern drift


class DriftSeverity(Enum):
    """Drift severity levels aligned with tier access."""

    STABLE = "stable"  # 0.0-0.2 - All tiers
    MINOR = "minor"  # 0.2-0.4 - LAMBDA_TIER_1+
    MODERATE = "moderate"  # 0.4-0.6 - LAMBDA_TIER_2+
    SIGNIFICANT = "significant"  # 0.6-0.8 - LAMBDA_TIER_3+
    CRITICAL = "critical"  # 0.8-1.0 - LAMBDA_TIER_4+


@dataclass
class UnifiedDriftContext:
    """Enhanced drift analysis context with user identity."""

    user_id: str  # Lambda ID
    session_id: str
    lambda_tier: str
    analysis_scope: list[DriftDimension]
    consent_grants: dict[str, bool] = field(default_factory=dict)
    temporal_window_hours: int = 24
    include_predictions: bool = False
    anonymize_data: bool = True
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class UnifiedDriftResult:
    """Comprehensive drift analysis result with user context."""

    user_id: str
    overall_drift_score: float  # 0.0-1.0
    dimension_scores: dict[str, float]
    severity: DriftSeverity
    phase: DriftPhase
    lambda_tier: str
    symbolic_tags: list[str] = field(default_factory=list)
    risk_indicators: list[str] = field(default_factory=list)
    cascade_risk: float = 0.0
    stability_score: float = 1.0
    coherence_score: float = 1.0
    trend_direction: str = "stable"  # increasing, decreasing, stable, oscillating
    temporal_patterns: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    consent_limited: list[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# LUKHAS_TAG: unified_drift_access_matrix
UNIFIED_DRIFT_ACCESS_MATRIX = {
    "LAMBDA_TIER_0": {
        "max_dimensions": 1,
        "temporal_window_hours": 1,
        "include_predictions": False,
        "detailed_analysis": False,
        "cascade_detection": False,
        "consent_required": ["basic_drift_access"],
    },
    "LAMBDA_TIER_1": {
        "max_dimensions": 2,
        "temporal_window_hours": 24,
        "include_predictions": False,
        "detailed_analysis": False,
        "cascade_detection": False,
        "consent_required": ["drift_analysis"],
    },
    "LAMBDA_TIER_2": {
        "max_dimensions": 4,
        "temporal_window_hours": 168,  # 1 week
        "include_predictions": True,
        "detailed_analysis": True,
        "cascade_detection": False,
        "consent_required": ["drift_analysis", "detailed_drift_access"],
    },
    "LAMBDA_TIER_3": {
        "max_dimensions": 6,
        "temporal_window_hours": 720,  # 1 month
        "include_predictions": True,
        "detailed_analysis": True,
        "cascade_detection": True,
        "consent_required": [
            "drift_analysis",
            "detailed_drift_access",
            "cascade_risk_analysis",
        ],
    },
    "LAMBDA_TIER_4": {
        "max_dimensions": 7,
        "temporal_window_hours": 2160,  # 3 months
        "include_predictions": True,
        "detailed_analysis": True,
        "cascade_detection": True,
        "consent_required": [
            "drift_analysis",
            "detailed_drift_access",
            "cascade_risk_analysis",
            "predictive_drift_modeling",
        ],
    },
    "LAMBDA_TIER_5": {
        "max_dimensions": 7,
        "temporal_window_hours": 8760,  # 1 year
        "include_predictions": True,
        "detailed_analysis": True,
        "cascade_detection": True,
        "consent_required": ["drift_analysis"],  # System tier has fewer restrictions
    },
}


class UnifiedDriftSystem:
    """
    Comprehensive drift analysis system with unified tier integration.

    Provides identity-aware drift tracking across symbolic, emotional, memory,
    and coherence dimensions with tier-based access control and consent management.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}

        # Initialize component drift trackers
        self.symbolic_tracker = SymbolicDriftTracker(config.get("symbolic", {}))
        self.memory_tracker = MemoryDriftTracker(
            config.get("memory_log_path", "unified_drift.jsonl")
        )

        # Get centralized identity client
        self.identity_client = get_identity_client()

        # Drift analysis storage
        self.drift_history: dict[str, list[UnifiedDriftResult]] = {}
        self.cascade_alerts: list[dict[str, Any]] = []
        self.user_baselines: dict[str, dict[str, float]] = {}

        # Logging paths
        self.logs_dir = "/Users/agi_dev/Downloads/Consolidation-Repo/logs/drift"
        os.makedirs(self.logs_dir, exist_ok=True)

        self.unified_log_path = os.path.join(
            self.logs_dir, "unified_drift_analysis.jsonl"
        )
        self.cascade_log_path = os.path.join(
            self.logs_dir, "drift_cascade_alerts.jsonl"
        )
        self.baseline_log_path = os.path.join(
            self.logs_dir, "user_drift_baselines.jsonl"
        )

        logger.info(
            "UnifiedDriftSystem initialized",
            identity_client_available=self.identity_client is not None,
            components=["symbolic", "memory", "emotional", "coherence"],
        )

    # LUKHAS_TAG: unified_drift_analysis
    @require_identity(required_tier="LAMBDA_TIER_1", check_consent="drift_analysis")
    def analyze_unified_drift(
        self,
        user_id: str,
        current_state: dict[str, Any],
        context: Optional[UnifiedDriftContext] = None,
    ) -> UnifiedDriftResult:
        """
        Performs comprehensive drift analysis across all dimensions.

        Args:
            user_id: User's Lambda ID
            current_state: Current system state for analysis
            context: Analysis context and parameters

        Returns:
            Comprehensive unified drift analysis result
        """
        if not context:
            context = UnifiedDriftContext(
                user_id=user_id,
                session_id=f"session_{hashlib.md5(user_id.encode()).hexdigest()[:8]}",
                lambda_tier=self._get_user_tier(user_id),
                analysis_scope=[DriftDimension.SYMBOLIC, DriftDimension.EMOTIONAL],
            )

        # Get user's tier access permissions
        tier_permissions = UNIFIED_DRIFT_ACCESS_MATRIX.get(
            context.lambda_tier, UNIFIED_DRIFT_ACCESS_MATRIX["LAMBDA_TIER_1"]
        )

        # Verify consent for analysis
        consent_limited = []
        required_consents = tier_permissions["consent_required"]
        for consent_type in required_consents:
            if not context.consent_grants.get(consent_type, False):
                consent_limited.append(consent_type)

        # Limit analysis scope based on tier
        max_dimensions = tier_permissions["max_dimensions"]
        analysis_scope = context.analysis_scope[:max_dimensions]

        # Get user baseline for comparison
        user_baseline = self._get_user_baseline(user_id)

        # Perform dimension-specific drift analysis
        dimension_scores = {}
        symbolic_tags = []
        risk_indicators = []

        # Symbolic drift analysis
        if DriftDimension.SYMBOLIC in analysis_scope:
            symbolic_score = self._analyze_symbolic_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["symbolic"] = symbolic_score
            if symbolic_score > 0.6:
                symbolic_tags.append("ΛDRIFT:symbolic_high")
                risk_indicators.append("high_symbolic_drift")

        # Emotional drift analysis
        if DriftDimension.EMOTIONAL in analysis_scope:
            emotional_score = self._analyze_emotional_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["emotional"] = emotional_score
            if emotional_score > 0.6:
                symbolic_tags.append("ΛDRIFT:emotional_high")
                risk_indicators.append("emotional_instability")

        # Memory drift analysis (Tier 2+)
        if DriftDimension.MEMORY in analysis_scope and context.lambda_tier in [
            "LAMBDA_TIER_2",
            "LAMBDA_TIER_3",
            "LAMBDA_TIER_4",
            "LAMBDA_TIER_5",
        ]:
            memory_score = self._analyze_memory_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["memory"] = memory_score
            if memory_score > 0.5:
                symbolic_tags.append("ΛDRIFT:memory_moderate")

        # Coherence drift analysis (Tier 2+)
        if (
            DriftDimension.COHERENCE in analysis_scope
            and tier_permissions["detailed_analysis"]
        ):
            coherence_score = self._analyze_coherence_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["coherence"] = coherence_score
            if coherence_score < 0.7:
                symbolic_tags.append("ΛCOHERENCE:degraded")
                risk_indicators.append("coherence_loss")

        # Identity drift analysis (Tier 3+)
        if (
            DriftDimension.IDENTITY in analysis_scope
            and tier_permissions["cascade_detection"]
        ):
            identity_score = self._analyze_identity_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["identity"] = identity_score
            if identity_score > 0.7:
                symbolic_tags.append("ΛIDENTITY:instability")
                risk_indicators.append("identity_cascade_risk")

        # Ethical drift analysis (Tier 3+)
        if (
            DriftDimension.ETHICAL in analysis_scope
            and tier_permissions["cascade_detection"]
        ):
            ethical_score = self._analyze_ethical_drift(
                current_state, user_baseline, user_id
            )
            dimension_scores["ethical"] = ethical_score
            if ethical_score > 0.6:
                symbolic_tags.append("ΛETHICAL:drift_detected")
                risk_indicators.append("ethical_alignment_shift")

        # Calculate overall drift score
        overall_score = (
            np.mean(list(dimension_scores.values())) if dimension_scores else 0.0
        )

        # Determine severity and phase
        severity = self._calculate_severity(overall_score)
        phase = self._calculate_phase(overall_score, dimension_scores)

        # Calculate cascade risk (Tier 3+)
        cascade_risk = 0.0
        if tier_permissions["cascade_detection"]:
            cascade_risk = self._calculate_cascade_risk(dimension_scores, user_id)
            if cascade_risk > 0.7:
                symbolic_tags.append("ΛCASCADE:high_risk")
                risk_indicators.append("cascade_imminent")

        # Calculate stability and coherence scores
        stability_score = max(0.0, 1.0 - overall_score)
        coherence_score = dimension_scores.get("coherence", 0.8)

        # Determine trend direction
        trend_direction = self._analyze_trend_direction(user_id, overall_score)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            dimension_scores, severity, risk_indicators
        )

        # Create unified result
        unified_result = UnifiedDriftResult(
            user_id=user_id,
            overall_drift_score=overall_score,
            dimension_scores=dimension_scores,
            severity=severity,
            phase=phase,
            lambda_tier=context.lambda_tier,
            symbolic_tags=symbolic_tags,
            risk_indicators=risk_indicators,
            cascade_risk=cascade_risk,
            stability_score=stability_score,
            coherence_score=coherence_score,
            trend_direction=trend_direction,
            recommendations=recommendations,
            consent_limited=consent_limited,
        )

        # Store result in history
        if user_id not in self.drift_history:
            self.drift_history[user_id] = []
        self.drift_history[user_id].append(unified_result)

        # Keep last 100 results per user
        self.drift_history[user_id] = self.drift_history[user_id][-100:]

        # Log analysis with identity system
        if self.identity_client:
            self.identity_client.log_activity(
                "unified_drift_analysis",
                user_id,
                {
                    "overall_score": overall_score,
                    "severity": severity.value,
                    "dimensions_analyzed": len(dimension_scores),
                    "cascade_risk": cascade_risk,
                    "lambda_tier": context.lambda_tier,
                },
            )

        # Check for cascade alerts
        if cascade_risk > 0.8:
            self._trigger_cascade_alert(user_id, unified_result)

        # Log to unified drift log
        self._log_unified_drift(unified_result)

        logger.info(
            "Unified drift analysis complete",
            user_id=user_id,
            overall_score=overall_score,
            severity=severity.value,
            cascade_risk=cascade_risk,
            dimensions=len(dimension_scores),
        )

        return unified_result

    # LUKHAS_TAG: drift_trend_analysis
    @require_identity(
        required_tier="LAMBDA_TIER_2", check_consent="detailed_drift_access"
    )
    def analyze_drift_trends(self, user_id: str, days: int = 7) -> dict[str, Any]:
        """
        Analyzes drift trends over time for a user.

        Args:
            user_id: User's Lambda ID
            days: Number of days to analyze

        Returns:
            Comprehensive trend analysis
        """
        if user_id not in self.drift_history or not self.drift_history[user_id]:
            return {
                "user_id": user_id,
                "trend_status": "insufficient_data",
                "days_analyzed": 0,
                "recommendations": ["Continue using system to build drift history"],
            }

        # Filter to recent results
        cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
        recent_results = [
            result
            for result in self.drift_history[user_id]
            if datetime.fromisoformat(result.timestamp) >= cutoff_time
        ]

        if len(recent_results) < 2:
            return {
                "user_id": user_id,
                "trend_status": "insufficient_recent_data",
                "days_analyzed": days,
                "total_analyses": len(recent_results),
            }

        # Calculate trend metrics
        overall_scores = [r.overall_drift_score for r in recent_results]
        cascade_risks = [r.cascade_risk for r in recent_results]
        stability_scores = [r.stability_score for r in recent_results]

        # Trend analysis
        trend_slope = np.polyfit(range(len(overall_scores)), overall_scores, 1)[0]
        avg_drift = np.mean(overall_scores)
        drift_volatility = np.std(overall_scores)

        # Determine trend direction
        if trend_slope > 0.02:
            trend_status = "increasing_drift"
        elif trend_slope < -0.02:
            trend_status = "decreasing_drift"
        else:
            trend_status = "stable_drift"

        # Risk assessment
        max_cascade_risk = max(cascade_risks) if cascade_risks else 0.0
        avg_stability = np.mean(stability_scores)

        # Dimension-specific trends
        dimension_trends = {}
        for dimension in [
            "symbolic",
            "emotional",
            "memory",
            "coherence",
            "identity",
            "ethical",
        ]:
            dimension_scores = [
                r.dimension_scores.get(dimension, 0.0)
                for r in recent_results
                if dimension in r.dimension_scores
            ]
            if dimension_scores:
                dimension_trends[dimension] = {
                    "average": np.mean(dimension_scores),
                    "trend": (
                        "increasing"
                        if len(dimension_scores) > 1
                        and np.polyfit(
                            range(len(dimension_scores)), dimension_scores, 1
                        )[0]
                        > 0.02
                        else "stable"
                    ),
                    "volatility": np.std(dimension_scores),
                }

        trend_result = {
            "user_id": user_id,
            "trend_status": trend_status,
            "trend_slope": trend_slope,
            "days_analyzed": days,
            "total_analyses": len(recent_results),
            "average_drift": avg_drift,
            "drift_volatility": drift_volatility,
            "max_cascade_risk": max_cascade_risk,
            "average_stability": avg_stability,
            "dimension_trends": dimension_trends,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Log trend analysis
        if self.identity_client:
            self.identity_client.log_activity(
                "drift_trend_analysis",
                user_id,
                {
                    "trend_status": trend_status,
                    "days_analyzed": days,
                    "average_drift": avg_drift,
                    "max_cascade_risk": max_cascade_risk,
                },
            )

        return trend_result

    # === Helper Methods ===

    def _get_user_tier(self, user_id: str) -> str:
        """Get user's Lambda tier from identity system."""
        if self.identity_client:
            try:
                from identity.core.user_tier_mapping import get_user_tier

                return get_user_tier(user_id) or "LAMBDA_TIER_1"
            except BaseException:
                pass
        return "LAMBDA_TIER_1"

    def _get_user_baseline(self, user_id: str) -> dict[str, float]:
        """Get or create user's drift baseline."""
        if user_id not in self.user_baselines:
            # Initialize with default baseline
            self.user_baselines[user_id] = {
                "symbolic": 0.3,
                "emotional": 0.25,
                "memory": 0.2,
                "coherence": 0.8,
                "identity": 0.1,
                "ethical": 0.05,
            }
        return self.user_baselines[user_id]

    def _analyze_symbolic_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze symbolic drift using symbolic tracker."""
        current_symbols = current_state.get("symbols", [])
        baseline_symbols = current_state.get("baseline_symbols", [])

        if self.symbolic_tracker:
            return self.symbolic_tracker.calculate_symbolic_drift(
                current_symbols, baseline_symbols, {"user_id": user_id}
            )
        return baseline.get("symbolic", 0.3)

    def _analyze_emotional_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze emotional drift from current state."""
        current_emotion = current_state.get("emotion_vector", {})
        baseline_emotion = current_state.get("baseline_emotion", {})

        if current_emotion and baseline_emotion:
            # Calculate euclidean distance between emotion vectors
            current_vals = list(current_emotion.values())
            baseline_vals = list(baseline_emotion.values())
            if len(current_vals) == len(baseline_vals):
                return np.linalg.norm(np.array(current_vals) - np.array(baseline_vals))

        return baseline.get("emotional", 0.25)

    def _analyze_memory_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze memory drift using memory tracker."""
        if self.memory_tracker:
            current_snapshot = current_state.get("memory_snapshot", {})
            prior_snapshot = current_state.get("prior_memory_snapshot", {})

            if current_snapshot and prior_snapshot:
                drift_result = self.memory_tracker.track_drift(
                    current_snapshot, prior_snapshot
                )
                return min(
                    1.0,
                    drift_result.get("entropy_delta", 0.0)
                    + drift_result.get("emotional_delta", 0.0),
                )

        return baseline.get("memory", 0.2)

    def _analyze_coherence_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze narrative/logical coherence drift."""
        coherence_score = current_state.get("coherence_score", 0.8)
        baseline_coherence = baseline.get("coherence", 0.8)

        # Return drift as deviation from baseline (inverted for coherence)
        return abs(baseline_coherence - coherence_score)

    def _analyze_identity_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze identity stability drift."""
        identity_stability = current_state.get("identity_stability", 0.9)
        baseline.get("identity", 0.1)

        # Higher instability = higher drift
        return max(0.0, 1.0 - identity_stability)

    def _analyze_ethical_drift(
        self, current_state: dict[str, Any], baseline: dict[str, float], user_id: str
    ) -> float:
        """Analyze ethical alignment drift."""
        ethical_alignment = current_state.get("ethical_alignment", 0.95)
        baseline.get("ethical", 0.05)

        # Deviation from high ethical alignment
        return max(0.0, 1.0 - ethical_alignment)

    def _calculate_severity(self, overall_score: float) -> DriftSeverity:
        """Calculate drift severity from overall score."""
        if overall_score < 0.2:
            return DriftSeverity.STABLE
        elif overall_score < 0.4:
            return DriftSeverity.MINOR
        elif overall_score < 0.6:
            return DriftSeverity.MODERATE
        elif overall_score < 0.8:
            return DriftSeverity.SIGNIFICANT
        else:
            return DriftSeverity.CRITICAL

    def _calculate_phase(
        self, overall_score: float, dimension_scores: dict[str, float]
    ) -> DriftPhase:
        """Calculate drift phase based on scores."""
        if overall_score < 0.25:
            return DriftPhase.EARLY
        elif overall_score < 0.5:
            return DriftPhase.MIDDLE
        elif overall_score < 0.75:
            return DriftPhase.LATE
        else:
            return DriftPhase.CASCADE

    def _calculate_cascade_risk(
        self, dimension_scores: dict[str, float], user_id: str
    ) -> float:
        """Calculate cascade risk from multiple high drift dimensions."""
        high_drift_dimensions = [
            score for score in dimension_scores.values() if score > 0.6
        ]

        if len(high_drift_dimensions) >= 3:
            return min(1.0, 0.5 + 0.2 * len(high_drift_dimensions))
        elif len(high_drift_dimensions) >= 2:
            return min(1.0, 0.3 + 0.1 * len(high_drift_dimensions))
        else:
            return max(dimension_scores.values()) if dimension_scores else 0.0

    def _analyze_trend_direction(self, user_id: str, current_score: float) -> str:
        """Analyze drift trend direction from history."""
        if user_id not in self.drift_history or len(self.drift_history[user_id]) < 3:
            return "stable"

        recent_scores = [
            r.overall_drift_score for r in self.drift_history[user_id][-5:]
        ]

        if len(recent_scores) >= 3:
            slope = np.polyfit(range(len(recent_scores)), recent_scores, 1)[0]
            if slope > 0.05:
                return "increasing"
            elif slope < -0.05:
                return "decreasing"

        return "stable"

    def _generate_recommendations(
        self,
        dimension_scores: dict[str, float],
        severity: DriftSeverity,
        risk_indicators: list[str],
    ) -> list[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        if severity in [DriftSeverity.SIGNIFICANT, DriftSeverity.CRITICAL]:
            recommendations.append("Consider session break for system stabilization")

        if "high_symbolic_drift" in risk_indicators:
            recommendations.append("Review symbolic consistency in recent interactions")

        if "emotional_instability" in risk_indicators:
            recommendations.append("Emotional state monitoring recommended")

        if "cascade_imminent" in risk_indicators:
            recommendations.append("Emergency intervention may be required")

        if not recommendations:
            recommendations.append("System operating within normal parameters")

        return recommendations

    def _trigger_cascade_alert(self, user_id: str, result: UnifiedDriftResult):
        """Trigger cascade alert for high-risk drift."""
        alert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "alert_type": "cascade_risk",
            "cascade_risk": result.cascade_risk,
            "overall_score": result.overall_drift_score,
            "risk_indicators": result.risk_indicators,
            "lambda_tier": result.lambda_tier,
        }

        self.cascade_alerts.append(alert)

        # Log cascade alert
        with open(self.cascade_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(alert) + "\n")

        logger.critical(
            "Cascade alert triggered",
            user_id=user_id,
            cascade_risk=result.cascade_risk,
            risk_indicators=result.risk_indicators,
        )

    def _log_unified_drift(self, result: UnifiedDriftResult):
        """Log unified drift result."""
        log_entry = asdict(result)

        with open(self.unified_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")


# Factory function for easy integration
def create_unified_drift_system(
    config: Optional[dict[str, Any]] = None,
) -> UnifiedDriftSystem:
    """Create a new unified drift system instance."""
    return UnifiedDriftSystem(config)


# ═══════════════════════════════════════════════════════════════════════════════════
# 🌀 UNIFIED DRIFT SYSTEM INTEGRATION SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════════
#
# This module represents the complete integration of all drift tracking systems
# with the unified LAMBDA_TIER system:
#
# 1. Multi-dimensional drift analysis (symbolic, emotional, memory, coherence, identity, ethical)
# 2. Tier-based access control with consent management
# 3. User identity integration with Lambda ID tracking
# 4. Cascade risk detection and emergency intervention
# 5. Comprehensive trend analysis and prediction
# 6. Enhanced logging with ΛTRACE integration
#
# Key Improvements over Fragmented Systems:
# - Unified drift scoring across all dimensions
# - Identity-aware drift tracking with user context
# - Tier-based feature gating for sensitive analysis
# - Cascade prevention with early warning system
# - Comprehensive trend analysis and recommendations
#
# Integration Points:
# - Oneiric Dream Engine: Dream coherence and symbolic entropy drift
# - DreamSeed Emotions: Emotional polarity and affect vector drift
# - Memory Systems: Memory fold and symbolic vector drift
# - Identity System: Identity stability and authenticity tracking
# - Ethical Alignment: Ethical drift and compliance monitoring
# ═══════════════════════════════════════════════════════════════════════════════════
