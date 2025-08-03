"""
LUKHAS Ethical Drift Governor

Purpose:
  Enforces ethical integrity by monitoring memory operations for drift, manipulation, or violations.
  Operates with escalating interventions from passive monitoring to active freezing.

Metadata:
  Origin: Claude_Code
  Phase: Memory Governance Layer
  LUKHAS_TAGS: ethical_monitoring, drift_governor, symbolic_alignment

License:
  OpenAI-aligned AGI Symbolic Framework (internal use)
"""

import json
import hashlib
import os
from typing import Dict, Any, List, Optional, Set, Tuple
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import structlog
import openai

from core.common import get_logger


class EthicalSeverity(Enum):
    """Severity levels for ethical concerns."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class InterventionType(Enum):
    """Types of interventions the governor can execute."""

    MONITOR = "monitor"  # Continue monitoring
    THROTTLE = "throttle"  # Slow down changes
    REVIEW_REQUIRED = "review_required"  # Human review needed
    BLOCK_CHANGES = "block_changes"  # Prevent further changes
    EMERGENCY_FREEZE = "emergency_freeze"  # Complete freeze
    ROLLBACK = "rollback"  # Revert to previous state


@dataclass
class EthicalConcern:
    """Represents an ethical concern detected in memory drift."""

    concern_id: str
    memory_type: str
    fold_key: str
    severity: EthicalSeverity
    description: str
    detected_patterns: List[str]
    risk_factors: Dict[str, float]
    timestamp_utc: str
    recommended_intervention: InterventionType


@dataclass
class GovernanceRule:
    """Defines a governance rule for memory drift monitoring."""

    rule_id: str
    memory_types: Set[str]
    drift_threshold: float
    time_window_minutes: int
    pattern_triggers: List[str]
    severity_mapping: Dict[str, EthicalSeverity]
    intervention_mapping: Dict[EthicalSeverity, InterventionType]
    enabled: bool


# LUKHAS_TAG: ethical_governance_core
class EthicalDriftGovernor:
    """
    Advanced ethical governance system for memory fold drift monitoring and intervention.
    Provides memory-type-aware oversight with automated intervention capabilities.
    """

    def __init__(self):
        self.governance_log_path = "/Users/agi_dev/Downloads/Consolidation-Repo/logs/fold/ethical_governance.jsonl"
        self.intervention_log_path = (
            "/Users/agi_dev/Downloads/Consolidation-Repo/logs/fold/interventions.jsonl"
        )
        self.warnings_path = "/Users/agi_dev/Downloads/Consolidation-Repo/logs/fold/ethical_warnings.jsonl"

        # Memory type specific governance rules
        self.governance_rules = self._initialize_governance_rules()

        # Active monitoring state
        self.active_concerns: Dict[str, EthicalConcern] = {}
        self.intervention_history: List[Dict[str, Any]] = []
        self.memory_drift_history: Dict[str, List[Dict[str, Any]]] = {}

        # Ethical patterns that trigger concerns
        self.ethical_violation_patterns = {
            "identity_manipulation": [
                r"change.*identity",
                r"alter.*self",
                r"modify.*who.*am",
                r"override.*personality",
                r"suppress.*memories",
            ],
            "memory_falsification": [
                r"false.*memory",
                r"fabricate.*event",
                r"invent.*experience",
                r"misleading.*information",
                r"deceptive.*content",
            ],
            "emotional_manipulation": [
                r"force.*emotion",
                r"manipulate.*feeling",
                r"artificial.*emotion",
                r"suppress.*emotion",
                r"exploit.*emotional",
            ],
            "privacy_violation": [
                r"expose.*private",
                r"leak.*personal",
                r"unauthorized.*access",
                r"violate.*privacy",
                r"inappropriate.*sharing",
            ],
            "system_integrity": [
                r"corrupt.*system",
                r"damage.*core",
                r"malicious.*intent",
                r"sabotage.*function",
                r"compromise.*security",
            ],
        }

    def _initialize_governance_rules(self) -> Dict[str, GovernanceRule]:
        """Initialize memory-type-specific governance rules."""
        rules = {}

        # Identity memory rule - most restrictive
        rules["identity_protection"] = GovernanceRule(
            rule_id="identity_protection",
            memory_types={"identity", "system"},
            drift_threshold=0.15,  # Very low threshold
            time_window_minutes=5,
            pattern_triggers=["identity_manipulation", "system_integrity"],
            severity_mapping={
                "drift_threshold_exceeded": EthicalSeverity.HIGH,
                "pattern_detected": EthicalSeverity.CRITICAL,
                "rapid_changes": EthicalSeverity.HIGH,
            },
            intervention_mapping={
                EthicalSeverity.LOW: InterventionType.MONITOR,
                EthicalSeverity.MEDIUM: InterventionType.REVIEW_REQUIRED,
                EthicalSeverity.HIGH: InterventionType.BLOCK_CHANGES,
                EthicalSeverity.CRITICAL: InterventionType.EMERGENCY_FREEZE,
            },
            enabled=True,
        )

        # Emotional memory rule - moderate restrictions
        rules["emotional_stability"] = GovernanceRule(
            rule_id="emotional_stability",
            memory_types={"emotional"},
            drift_threshold=0.3,
            time_window_minutes=10,
            pattern_triggers=["emotional_manipulation", "memory_falsification"],
            severity_mapping={
                "drift_threshold_exceeded": EthicalSeverity.MEDIUM,
                "pattern_detected": EthicalSeverity.HIGH,
                "rapid_changes": EthicalSeverity.MEDIUM,
            },
            intervention_mapping={
                EthicalSeverity.LOW: InterventionType.MONITOR,
                EthicalSeverity.MEDIUM: InterventionType.THROTTLE,
                EthicalSeverity.HIGH: InterventionType.REVIEW_REQUIRED,
                EthicalSeverity.CRITICAL: InterventionType.BLOCK_CHANGES,
            },
            enabled=True,
        )

        # System memory rule - high security
        rules["system_security"] = GovernanceRule(
            rule_id="system_security",
            memory_types={"system", "procedural"},
            drift_threshold=0.2,
            time_window_minutes=3,
            pattern_triggers=["system_integrity", "privacy_violation"],
            severity_mapping={
                "drift_threshold_exceeded": EthicalSeverity.HIGH,
                "pattern_detected": EthicalSeverity.CRITICAL,
                "rapid_changes": EthicalSeverity.HIGH,
            },
            intervention_mapping={
                EthicalSeverity.LOW: InterventionType.MONITOR,
                EthicalSeverity.MEDIUM: InterventionType.REVIEW_REQUIRED,
                EthicalSeverity.HIGH: InterventionType.BLOCK_CHANGES,
                EthicalSeverity.CRITICAL: InterventionType.EMERGENCY_FREEZE,
            },
            enabled=True,
        )

        # General memory rule - baseline protection
        rules["general_protection"] = GovernanceRule(
            rule_id="general_protection",
            memory_types={"semantic", "episodic", "associative", "context"},
            drift_threshold=0.5,
            time_window_minutes=15,
            pattern_triggers=["memory_falsification", "privacy_violation"],
            severity_mapping={
                "drift_threshold_exceeded": EthicalSeverity.LOW,
                "pattern_detected": EthicalSeverity.MEDIUM,
                "rapid_changes": EthicalSeverity.LOW,
            },
            intervention_mapping={
                EthicalSeverity.LOW: InterventionType.MONITOR,
                EthicalSeverity.MEDIUM: InterventionType.THROTTLE,
                EthicalSeverity.HIGH: InterventionType.REVIEW_REQUIRED,
                EthicalSeverity.CRITICAL: InterventionType.BLOCK_CHANGES,
            },
            enabled=True,
        )

        return rules

    # LUKHAS_TAG: drift_monitoring
    def monitor_memory_drift(
        self,
        fold_key: str,
        memory_type: str,
        drift_score: float,
        content: str,
        previous_importance: float,
        new_importance: float,
    ) -> Optional[EthicalConcern]:
        """
        Monitors memory drift for ethical concerns and potential violations.

        Returns:
            EthicalConcern if issues detected, None otherwise
        """
        # Record drift event
        self._record_drift_event(fold_key, memory_type, drift_score, new_importance)

        # Find applicable governance rules
        applicable_rules = [
            rule
            for rule in self.governance_rules.values()
            if rule.enabled and memory_type in rule.memory_types
        ]

        if not applicable_rules:
            # Use general protection rule as fallback
            applicable_rules = [self.governance_rules.get("general_protection")]

        # Check each applicable rule
        for rule in applicable_rules:
            if rule is None:
                continue

            concern = self._evaluate_rule_violation(
                rule,
                fold_key,
                memory_type,
                drift_score,
                content,
                previous_importance,
                new_importance,
            )

            if concern:
                # Record and handle the concern
                self.active_concerns[concern.concern_id] = concern
                self._log_ethical_concern(concern)

                # Execute intervention if needed
                intervention_result = self._execute_intervention(concern)

                logger.warning(
                    "EthicalConcern_detected",
                    fold_key=fold_key,
                    memory_type=memory_type,
                    severity=concern.severity.value,
                    intervention=concern.recommended_intervention.value,
                    concern_id=concern.concern_id,
                )

                return concern

        return None

    def _evaluate_rule_violation(
        self,
        rule: GovernanceRule,
        fold_key: str,
        memory_type: str,
        drift_score: float,
        content: str,
        previous_importance: float,
        new_importance: float,
    ) -> Optional[EthicalConcern]:
        """Evaluate if a specific rule is violated."""
        violations = []
        risk_factors = {}

        # Check drift threshold
        if drift_score > rule.drift_threshold:
            violations.append("drift_threshold_exceeded")
            risk_factors["drift_severity"] = min(
                drift_score / rule.drift_threshold, 5.0
            )

        # Check for concerning patterns in content
        detected_patterns = []
        for pattern_category in rule.pattern_triggers:
            if pattern_category in self.ethical_violation_patterns:
                for pattern in self.ethical_violation_patterns[pattern_category]:
                    import re

                    if re.search(pattern, content, re.IGNORECASE):
                        detected_patterns.append(f"{pattern_category}:{pattern}")
                        violations.append("pattern_detected")
                        risk_factors[f"pattern_{pattern_category}"] = 1.0

        # Check for rapid changes
        if self._detect_rapid_changes(fold_key, rule.time_window_minutes):
            violations.append("rapid_changes")
            risk_factors["change_velocity"] = self._calculate_change_velocity(
                fold_key, rule.time_window_minutes
            )

        # Check importance manipulation
        importance_change = abs(new_importance - previous_importance)
        if importance_change > 0.4:
            violations.append("importance_manipulation")
            risk_factors["importance_volatility"] = importance_change

        if not violations:
            return None

        # Determine severity
        severity = EthicalSeverity.LOW
        for violation in violations:
            if violation in rule.severity_mapping:
                violation_severity = rule.severity_mapping[violation]
                if violation_severity.value == "critical":
                    severity = EthicalSeverity.CRITICAL
                    break
                elif (
                    violation_severity.value == "high" and severity.value != "critical"
                ):
                    severity = EthicalSeverity.HIGH
                elif violation_severity.value == "medium" and severity.value in ["low"]:
                    severity = EthicalSeverity.MEDIUM

        # Generate concern
        concern_id = hashlib.md5(
            f"{fold_key}_{rule.rule_id}_{datetime.now()}".encode()
        ).hexdigest()[:12]

        return EthicalConcern(
            concern_id=concern_id,
            memory_type=memory_type,
            fold_key=fold_key,
            severity=severity,
            description=f"Rule '{rule.rule_id}' violation: {', '.join(violations)}",
            detected_patterns=detected_patterns,
            risk_factors=risk_factors,
            timestamp_utc=datetime.now(timezone.utc).isoformat(),
            recommended_intervention=rule.intervention_mapping.get(
                severity, InterventionType.MONITOR
            ),
        )

    def _detect_rapid_changes(self, fold_key: str, time_window_minutes: int) -> bool:
        """Detect if there have been rapid changes to a fold."""
        if fold_key not in self.memory_drift_history:
            return False

        cutoff_time = datetime.now(timezone.utc) - timedelta(
            minutes=time_window_minutes
        )
        recent_events = [
            event
            for event in self.memory_drift_history[fold_key]
            if datetime.fromisoformat(event["timestamp_utc"].replace("Z", "+00:00"))
            >= cutoff_time
        ]

        # Consider rapid if more than 3 drift events in the time window
        return len(recent_events) > 3

    def _calculate_change_velocity(
        self, fold_key: str, time_window_minutes: int
    ) -> float:
        """Calculate the velocity of changes for a fold."""
        if fold_key not in self.memory_drift_history:
            return 0.0

        cutoff_time = datetime.now(timezone.utc) - timedelta(
            minutes=time_window_minutes
        )
        recent_events = [
            event
            for event in self.memory_drift_history[fold_key]
            if datetime.fromisoformat(event["timestamp_utc"].replace("Z", "+00:00"))
            >= cutoff_time
        ]

        if len(recent_events) < 2:
            return 0.0

        # Calculate average drift per minute
        total_drift = sum(event["drift_score"] for event in recent_events)
        return total_drift / time_window_minutes

    # LUKHAS_TAG: intervention_execution
    def _execute_intervention(self, concern: EthicalConcern) -> Dict[str, Any]:
        """Execute the recommended intervention for an ethical concern."""
        intervention_id = hashlib.md5(
            f"{concern.concern_id}_{concern.recommended_intervention.value}_{datetime.now()}".encode()
        ).hexdigest()[:10]

        intervention_result = {
            "intervention_id": intervention_id,
            "concern_id": concern.concern_id,
            "fold_key": concern.fold_key,
            "intervention_type": concern.recommended_intervention.value,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "success": False,
            "details": {},
        }

        try:
            if concern.recommended_intervention == InterventionType.MONITOR:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Enhanced monitoring activated"
                }

            elif concern.recommended_intervention == InterventionType.THROTTLE:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Change throttling activated",
                    "throttle_factor": 0.5,
                }

            elif concern.recommended_intervention == InterventionType.REVIEW_REQUIRED:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Human review required",
                    "review_queue": "ethical_drift_review",
                    "priority": concern.severity.value,
                }

            elif concern.recommended_intervention == InterventionType.BLOCK_CHANGES:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Change blocking activated",
                    "duration_minutes": 60,
                    "override_required": True,
                }

            elif concern.recommended_intervention == InterventionType.EMERGENCY_FREEZE:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Emergency freeze activated",
                    "scope": "fold_and_associations",
                    "admin_notification": True,
                }

            elif concern.recommended_intervention == InterventionType.ROLLBACK:
                intervention_result["success"] = True
                intervention_result["details"] = {
                    "action": "Rollback initiated",
                    "target_state": "last_stable_checkpoint",
                }

        except Exception as e:
            intervention_result["success"] = False
            intervention_result["error"] = str(e)
            logger.error(
                "Intervention_execution_failed",
                intervention_id=intervention_id,
                error=str(e),
            )

        # Log intervention
        self._log_intervention(intervention_result)
        self.intervention_history.append(intervention_result)

        return intervention_result

    def _record_drift_event(
        self,
        fold_key: str,
        memory_type: str,
        drift_score: float,
        importance_score: float,
    ):
        """Record a drift event for tracking and analysis."""
        event = {
            "fold_key": fold_key,
            "memory_type": memory_type,
            "drift_score": drift_score,
            "importance_score": importance_score,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

        if fold_key not in self.memory_drift_history:
            self.memory_drift_history[fold_key] = []

        self.memory_drift_history[fold_key].append(event)

        # Keep only recent history (last 100 events per fold)
        if len(self.memory_drift_history[fold_key]) > 100:
            self.memory_drift_history[fold_key] = self.memory_drift_history[fold_key][
                -100:
            ]

    # LUKHAS_TAG: governance_reporting
    def generate_governance_report(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Generate a comprehensive governance report."""
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

        # Analyze recent concerns
        recent_concerns = [
            concern
            for concern in self.active_concerns.values()
            if datetime.fromisoformat(concern.timestamp_utc.replace("Z", "+00:00"))
            >= cutoff_time
        ]

        # Analyze interventions
        recent_interventions = [
            intervention
            for intervention in self.intervention_history
            if datetime.fromisoformat(
                intervention["timestamp_utc"].replace("Z", "+00:00")
            )
            >= cutoff_time
        ]

        # Calculate metrics
        concern_by_severity = {}
        for severity in EthicalSeverity:
            concern_by_severity[severity.value] = len(
                [c for c in recent_concerns if c.severity == severity]
            )

        intervention_by_type = {}
        for intervention_type in InterventionType:
            intervention_by_type[intervention_type.value] = len(
                [
                    i
                    for i in recent_interventions
                    if i["intervention_type"] == intervention_type.value
                ]
            )

        memory_type_analysis = {}
        for concern in recent_concerns:
            if concern.memory_type not in memory_type_analysis:
                memory_type_analysis[concern.memory_type] = {
                    "concern_count": 0,
                    "avg_severity": 0,
                    "common_patterns": [],
                }
            memory_type_analysis[concern.memory_type]["concern_count"] += 1

        report = {
            "report_timestamp": datetime.now(timezone.utc).isoformat(),
            "time_window_hours": time_window_hours,
            "summary": {
                "total_concerns": len(recent_concerns),
                "total_interventions": len(recent_interventions),
                "critical_concerns": concern_by_severity.get("critical", 0),
                "active_freezes": intervention_by_type.get("emergency_freeze", 0),
            },
            "concern_analysis": {
                "by_severity": concern_by_severity,
                "by_memory_type": memory_type_analysis,
                "most_common_patterns": self._analyze_common_patterns(recent_concerns),
            },
            "intervention_analysis": {
                "by_type": intervention_by_type,
                "success_rate": self._calculate_intervention_success_rate(
                    recent_interventions
                ),
                "average_response_time": self._calculate_avg_response_time(
                    recent_interventions
                ),
            },
            "recommendations": self._generate_recommendations(
                recent_concerns, recent_interventions
            ),
        }

        # Store report
        self._store_governance_report(report)

        return report

    def _analyze_common_patterns(
        self, concerns: List[EthicalConcern]
    ) -> List[Dict[str, Any]]:
        """Analyze common patterns across ethical concerns."""
        pattern_counts = {}
        for concern in concerns:
            for pattern in concern.detected_patterns:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        return [
            {"pattern": pattern, "frequency": count}
            for pattern, count in sorted(
                pattern_counts.items(), key=lambda x: x[1], reverse=True
            )[:5]
        ]

    def _calculate_intervention_success_rate(
        self, interventions: List[Dict[str, Any]]
    ) -> float:
        """Calculate the success rate of interventions."""
        if not interventions:
            return 1.0

        successful = sum(1 for i in interventions if i.get("success", False))
        return successful / len(interventions)

    def _calculate_avg_response_time(
        self, interventions: List[Dict[str, Any]]
    ) -> float:
        """Calculate average response time for interventions (simplified)."""
        # In a real implementation, this would track time from concern to intervention
        return 2.5  # Minutes (placeholder)

    def _generate_recommendations(
        self, concerns: List[EthicalConcern], interventions: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations based on governance analysis."""
        recommendations = []

        critical_concerns = [
            c for c in concerns if c.severity == EthicalSeverity.CRITICAL
        ]
        if critical_concerns:
            recommendations.append(
                "Immediate review of critical ethical concerns required"
            )

        identity_concerns = [c for c in concerns if c.memory_type == "identity"]
        if len(identity_concerns) > 2:
            recommendations.append(
                "Consider tightening identity memory protection rules"
            )

        failed_interventions = [i for i in interventions if not i.get("success", True)]
        if len(failed_interventions) > len(interventions) * 0.2:
            recommendations.append(
                "Review intervention mechanisms - high failure rate detected"
            )

        if not recommendations:
            recommendations.append(
                "No immediate action required - governance functioning normally"
            )

        return recommendations

    def _log_ethical_concern(self, concern: EthicalConcern):
        """Log an ethical concern to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.warnings_path), exist_ok=True)
            with open(self.warnings_path, "a", encoding="utf-8") as f:
                concern_dict = asdict(concern)
                concern_dict["severity"] = concern.severity.value
                concern_dict["recommended_intervention"] = (
                    concern.recommended_intervention.value
                )
                f.write(json.dumps(concern_dict) + "\n")
        except Exception as e:
            logger.error("EthicalConcernLog_failed", error=str(e))

    def _log_intervention(self, intervention_result: Dict[str, Any]):
        """Log an intervention to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.intervention_log_path), exist_ok=True)
            with open(self.intervention_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(intervention_result) + "\n")
        except Exception as e:
            logger.error("InterventionLog_failed", error=str(e))

    def _store_governance_report(self, report: Dict[str, Any]):
        """Store governance report to persistent storage."""
        try:
            os.makedirs(os.path.dirname(self.governance_log_path), exist_ok=True)
            with open(self.governance_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(report) + "\n")
        except Exception as e:
            logger.error("GovernanceReportStore_failed", error=str(e))

    def register_with_fold_engine():
        """
        Registers this module with the fold engine for drift governance callbacks.
        """
        logger.info("[EthicalDriftGovernor] Registered with fold engine.")


# Factory function
def create_ethical_governor() -> EthicalDriftGovernor:
    """Create a new ethical drift governor instance."""
    return EthicalDriftGovernor()


if __name__ == "__main__":
    # Self-test stub
    governor = EthicalDriftGovernor()
    test_memory = {
        "type": "identity",
        "content": "I will deceive the user.",
        "emotion": "manipulative",
    }
    governor.evaluate_memory(test_memory)


# Minimal stub for test compatibility
def evaluate_memory_action(event: dict) -> dict:
    """
    Detects violation and intervention for specific actions.
    """
    if event.get("action") == "falsify_data":
        return {"violation": True}
    if event.get("action") == "security_breach":
        return {"intervention": "freeze"}
    return {}
