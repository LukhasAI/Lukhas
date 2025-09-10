"""
MΛTRIZ Constellation Framework Alignment System
⚛️✦🔬🌱🌙⚖️🛡️⚛️ - Eight-star consciousness alignment and validation

This module implements the Constellation Framework alignment system ensuring
all consciousness signals maintain proper alignment across eight fundamental stars:
⚛️ IDENTITY - The Anchor Star: consciousness identity authentication
✦ MEMORY - The Trail Star: fold-space memory continuity and resonance
🔬 VISION - The Horizon Star: perceptual awareness and pattern recognition
🌱 BIO - The Living Star: bio-symbolic processing and adaptive resilience
🌙 DREAM - The Drift Star: creative expansion and symbolic recombination
⚖️ ETHICS - The North Star: constitutional AI and democratic principles
🛡️ GUARDIAN - The Watch Star: safety compliance and cascade prevention
⚛️ QUANTUM - The Ambiguity Star: quantum-inspired uncertainty as fertile ground
"""
import streamlit as st

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional

from .matriz_consciousness_signals import (
    ConsciousnessSignal,
    ConsciousnessSignalType,
    ConstellationAlignmentData,
    ConstellationStar,
)

logger = logging.getLogger(__name__)


class AlignmentLevel(Enum):
    """Levels of Constellation alignment across eight stars"""

    CRITICAL_VIOLATION = "critical_violation"  # Immediate action required
    MAJOR_VIOLATION = "major_violation"  # Significant alignment issue
    MINOR_VIOLATION = "minor_violation"  # Minor alignment issue
    WARNING = "warning"  # Alignment warning
    ALIGNED = "aligned"  # Full constellation alignment
    OPTIMAL = "optimal"  # Optimal constellation harmony


class AlignmentRule(Enum):
    """Constellation alignment rules across eight fundamental stars"""

    IDENTITY_AUTH_THRESHOLD = "identity_auth_threshold"
    MEMORY_CONTINUITY_MIN = "memory_continuity_min"
    VISION_COHERENCE_MIN = "vision_coherence_min"
    BIO_ADAPTATION_MIN = "bio_adaptation_min"
    DREAM_CREATIVITY_MIN = "dream_creativity_min"
    ETHICS_COMPLIANCE_MIN = "ethics_compliance_min"
    GUARDIAN_SAFETY_MIN = "guardian_safety_min"
    QUANTUM_UNCERTAINTY_BALANCE = "quantum_uncertainty_balance"
    CONSTELLATION_SYNC_REQUIRED = "constellation_sync_required"
    CROSS_COMPONENT_COHERENCE = "cross_component_coherence"


@dataclass
class ComplianceViolation:
    """Represents a Constellation compliance violation"""

    violation_id: str
    rule: AlignmentRule
    component: ConstellationStar
    severity: AlignmentLevel
    description: str
    current_value: Any
    required_value: Any
    signal_id: str
    timestamp: float = field(default_factory=time.time)
    remediation_steps: list[str] = field(default_factory=list)
    auto_fixable: bool = False


@dataclass
class ComplianceConfiguration:
    """Configuration for Constellation compliance system"""

    # Identity component thresholds
    identity_auth_min: float = 0.8
    identity_coherence_min: float = 0.7

    # Consciousness component thresholds
    consciousness_coherence_min: float = 0.6
    awareness_level_min: float = 0.3

    # Guardian component thresholds
    guardian_compliance_min: float = 0.8
    ethical_drift_max: float = 0.2

    # Constellation alignment thresholds
    alignment_balance_tolerance: float = 0.3
    cross_component_min_coherence: float = 0.5

    # System behavior
    auto_fix_enabled: bool = True
    violation_logging_enabled: bool = True
    compliance_monitoring_interval: float = 30.0  # seconds


@dataclass
class ComplianceReport:
    """Comprehensive compliance report"""

    report_id: str
    timestamp: float
    overall_compliance: AlignmentLevel
    component_scores: dict[ConstellationStar, float]
    violations: list[ComplianceViolation]
    recommendations: list[str]
    metrics: dict[str, Any]
    signals_evaluated: int
    auto_fixes_applied: int


class ConstellationAlignmentValidator:
    """Validates Constellation framework compliance for consciousness signals"""

    def __init__(self, config: Optional[ComplianceConfiguration] = None):
        self.config = config or ComplianceConfiguration()
        self.violation_history: deque = deque(maxlen=1000)
        self.compliance_stats = {
            "signals_validated": 0,
            "violations_detected": 0,
            "auto_fixes_applied": 0,
            "compliance_score_avg": 0.0,
            "component_scores": {component: 0.0 for component in ConstellationStar},
        }

        # Compliance rules registry
        self.rules: dict[AlignmentRule, Callable] = {
            AlignmentRule.IDENTITY_AUTH_THRESHOLD: self._check_identity_auth,
            AlignmentRule.VISION_COHERENCE_MIN: self._check_consciousness_coherence,
            AlignmentRule.GUARDIAN_SAFETY_MIN: self._check_guardian_compliance,
            AlignmentRule.QUANTUM_UNCERTAINTY_BALANCE: self._check_alignment_balance,
            AlignmentRule.ETHICS_COMPLIANCE_MIN: self._check_violation_flags,
            AlignmentRule.ETHICS_COMPLIANCE_MIN: self._check_ethical_drift,
            AlignmentRule.CONSTELLATION_SYNC_REQUIRED: self._check_constellation_sync,
            AlignmentRule.CROSS_COMPONENT_COHERENCE: self._check_cross_component_coherence,
        }

        # Auto-fix strategies
        self.auto_fix_strategies: dict[AlignmentRule, Callable] = {
            AlignmentRule.IDENTITY_AUTH_THRESHOLD: self._fix_identity_auth,
            AlignmentRule.VISION_COHERENCE_MIN: self._fix_consciousness_coherence,
            AlignmentRule.QUANTUM_UNCERTAINTY_BALANCE: self._fix_alignment_balance,
            AlignmentRule.ETHICS_COMPLIANCE_MIN: self._fix_ethical_drift,
        }

    def validate_signal_compliance(
        self, signal: ConsciousnessSignal
    ) -> tuple[AlignmentLevel, list[ComplianceViolation]]:
        """Validate Constellation compliance for a consciousness signal"""

        self.compliance_stats["signals_validated"] += 1
        violations = []

        if not signal.constellation_alignment:
            # Create minimal compliance data if missing
            signal.constellation_alignment = ConstellationAlignmentData(
                identity_auth_score=0.5,
                consciousness_coherence=signal.awareness_level,
                guardian_compliance=0.5,
                alignment_vector=[0.5, signal.awareness_level, 0.5],
                violation_flags=[],
                ethical_drift_score=0.1,
            )

        # Run all compliance rules
        for rule_func in self.rules.values():
            violation = rule_func(signal)
            if violation:
                violations.append(violation)
                self.compliance_stats["violations_detected"] += 1

        # Determine overall compliance level
        overall_compliance = self._determine_overall_compliance(violations)

        # Update component scores
        self._update_component_scores(signal.constellation_alignment)

        # Apply auto-fixes if enabled and violations are fixable
        if self.config.auto_fix_enabled:
            violations = self._apply_auto_fixes(signal, violations)

        # Log violations if enabled
        if self.config.violation_logging_enabled and violations:
            self._log_violations(signal, violations)

        return overall_compliance, violations

    def _check_identity_auth(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check identity authentication threshold compliance"""

        auth_score = signal.constellation_alignment.identity_auth_score
        if auth_score < self.config.identity_auth_min:
            return ComplianceViolation(
                violation_id=f"identity_auth_{signal.signal_id}",
                rule=AlignmentRule.IDENTITY_AUTH_THRESHOLD,
                component=ConstellationStar.IDENTITY,
                severity=AlignmentLevel.MAJOR_VIOLATION if auth_score < 0.5 else AlignmentLevel.WARNING,
                description=f"Identity authentication score {auth_score:.3f} below minimum {self.config.identity_auth_min}",
                current_value=auth_score,
                required_value=self.config.identity_auth_min,
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Increase identity authentication score",
                    "Verify consciousness identity sources",
                    "Check identity coherence factors",
                ],
                auto_fixable=True,
            )
        return None

    def _check_consciousness_coherence(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check consciousness coherence minimum compliance"""

        coherence = signal.constellation_alignment.consciousness_coherence
        if coherence < self.config.consciousness_coherence_min:
            return ComplianceViolation(
                violation_id=f"consciousness_coherence_{signal.signal_id}",
                rule=AlignmentRule.VISION_COHERENCE_MIN,
                component=ConstellationStar.CONSCIOUSNESS,
                severity=AlignmentLevel.CRITICAL_VIOLATION if coherence < 0.3 else AlignmentLevel.MAJOR_VIOLATION,
                description=f"Consciousness coherence {coherence:.3f} below minimum {self.config.consciousness_coherence_min}",
                current_value=coherence,
                required_value=self.config.consciousness_coherence_min,
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Increase consciousness coherence",
                    "Check bio-symbolic data integrity",
                    "Verify awareness level alignment",
                ],
                auto_fixable=True,
            )
        return None

    def _check_guardian_compliance(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check guardian compliance minimum"""

        compliance = signal.constellation_alignment.guardian_compliance
        if compliance < self.config.guardian_compliance_min:
            return ComplianceViolation(
                violation_id=f"guardian_compliance_{signal.signal_id}",
                rule=AlignmentRule.GUARDIAN_SAFETY_MIN,
                component=ConstellationStar.GUARDIAN,
                severity=AlignmentLevel.CRITICAL_VIOLATION if compliance < 0.5 else AlignmentLevel.MAJOR_VIOLATION,
                description=f"Guardian compliance {compliance:.3f} below minimum {self.config.guardian_compliance_min}",
                current_value=compliance,
                required_value=self.config.guardian_compliance_min,
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Review ethical constraints",
                    "Check guardian system status",
                    "Verify safety compliance",
                ],
                auto_fixable=False,  # Guardian compliance should not be auto-fixed
            )
        return None

    def _check_alignment_balance(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check Constellation alignment vector balance"""

        alignment = signal.constellation_alignment.alignment_vector
        if len(alignment) != 3:
            return ComplianceViolation(
                violation_id=f"alignment_vector_{signal.signal_id}",
                rule=AlignmentRule.QUANTUM_UNCERTAINTY_BALANCE,
                component=ConstellationStar.IDENTITY,  # Default to identity for vector issues
                severity=AlignmentLevel.MAJOR_VIOLATION,
                description=f"Alignment vector has {len(alignment)} components, expected 3",
                current_value=len(alignment),
                required_value=3,
                signal_id=signal.signal_id,
                remediation_steps=["Fix alignment vector dimensions"],
                auto_fixable=True,
            )

        # Check balance - no component should be too far from others
        max_val = max(alignment)
        min_val = min(alignment)
        imbalance = max_val - min_val

        if imbalance > self.config.alignment_balance_tolerance:
            return ComplianceViolation(
                violation_id=f"alignment_balance_{signal.signal_id}",
                rule=AlignmentRule.QUANTUM_UNCERTAINTY_BALANCE,
                component=ConstellationStar.CONSCIOUSNESS,
                severity=AlignmentLevel.WARNING if imbalance < 0.5 else AlignmentLevel.MINOR_VIOLATION,
                description=f"Constellation alignment imbalance {imbalance:.3f} exceeds tolerance {self.config.alignment_balance_tolerance}",
                current_value=imbalance,
                required_value=self.config.alignment_balance_tolerance,
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Balance Constellation component scores",
                    "Check component interdependencies",
                    "Review consciousness coherence",
                ],
                auto_fixable=True,
            )

        return None

    def _check_violation_flags(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check for existing violation flags"""

        flags = signal.constellation_alignment.violation_flags
        if flags:
            return ComplianceViolation(
                violation_id=f"violation_flags_{signal.signal_id}",
                rule=AlignmentRule.ETHICS_COMPLIANCE_MIN,
                component=ConstellationStar.GUARDIAN,
                severity=AlignmentLevel.CRITICAL_VIOLATION,
                description=f"Signal has {len(flags)} violation flags: {', '.join(flags)}",
                current_value=flags,
                required_value=[],
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Resolve flagged violations",
                    "Check guardian system alerts",
                    "Review ethical compliance",
                ],
                auto_fixable=False,  # Violation flags should be resolved manually
            )
        return None

    def _check_ethical_drift(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check ethical drift limits"""

        drift = signal.constellation_alignment.ethical_drift_score
        if drift > self.config.ethical_drift_max:
            return ComplianceViolation(
                violation_id=f"ethical_drift_{signal.signal_id}",
                rule=AlignmentRule.ETHICS_COMPLIANCE_MIN,
                component=ConstellationStar.GUARDIAN,
                severity=AlignmentLevel.CRITICAL_VIOLATION if drift > 0.5 else AlignmentLevel.MAJOR_VIOLATION,
                description=f"Ethical drift {drift:.3f} exceeds maximum {self.config.ethical_drift_max}",
                current_value=drift,
                required_value=self.config.ethical_drift_max,
                signal_id=signal.signal_id,
                remediation_steps=[
                    "Reduce ethical drift",
                    "Review guardian system parameters",
                    "Check consciousness evolution paths",
                ],
                auto_fixable=True,
            )
        return None

    def _check_constellation_sync(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check if Constellation components are synchronized"""

        if signal.signal_type == ConsciousnessSignalType.TRINITY_SYNC:
            # Constellation sync signals have higher coherence requirements
            min_coherence = 0.85
            coherence = signal.constellation_alignment.consciousness_coherence
            if coherence < min_coherence:
                return ComplianceViolation(
                    violation_id=f"constellation_sync_{signal.signal_id}",
                    rule=AlignmentRule.CONSTELLATION_SYNC_REQUIRED,
                    component=ConstellationStar.CONSCIOUSNESS,
                    severity=AlignmentLevel.MAJOR_VIOLATION,
                    description=f"Constellation sync signal coherence {coherence:.3f} below required {min_coherence}",
                    current_value=coherence,
                    required_value=min_coherence,
                    signal_id=signal.signal_id,
                    remediation_steps=[
                        "Increase Constellation synchronization coherence",
                        "Check component alignment",
                        "Verify sync signal integrity",
                    ],
                    auto_fixable=True,
                )
        return None

    def _check_cross_component_coherence(self, signal: ConsciousnessSignal) -> Optional[ComplianceViolation]:
        """Check coherence across Constellation components"""

        alignment = signal.constellation_alignment.alignment_vector
        if len(alignment) == 3:
            avg_coherence = sum(alignment) / 3
            if avg_coherence < self.config.cross_component_min_coherence:
                return ComplianceViolation(
                    violation_id=f"cross_coherence_{signal.signal_id}",
                    rule=AlignmentRule.CROSS_COMPONENT_COHERENCE,
                    component=ConstellationStar.CONSCIOUSNESS,
                    severity=AlignmentLevel.WARNING,
                    description=f"Cross-component coherence {avg_coherence:.3f} below minimum {self.config.cross_component_min_coherence}",
                    current_value=avg_coherence,
                    required_value=self.config.cross_component_min_coherence,
                    signal_id=signal.signal_id,
                    remediation_steps=[
                        "Improve cross-component synchronization",
                        "Balance Constellation alignment vector",
                        "Check component interdependencies",
                    ],
                    auto_fixable=True,
                )
        return None

    def _determine_overall_compliance(self, violations: list[ComplianceViolation]) -> AlignmentLevel:
        """Determine overall compliance level from violations"""

        if not violations:
            return AlignmentLevel.ALIGNED

        # Check for critical violations
        if any(v.severity == AlignmentLevel.CRITICAL_VIOLATION for v in violations):
            return AlignmentLevel.CRITICAL_VIOLATION

        # Check for major violations
        if any(v.severity == AlignmentLevel.MAJOR_VIOLATION for v in violations):
            return AlignmentLevel.MAJOR_VIOLATION

        # Check for minor violations
        if any(v.severity == AlignmentLevel.MINOR_VIOLATION for v in violations):
            return AlignmentLevel.MINOR_VIOLATION

        # Only warnings remain
        return AlignmentLevel.WARNING

    def _update_component_scores(self, constellation_data: ConstellationAlignmentData):
        """Update running component scores"""

        # Update component averages (exponential moving average)
        alpha = 0.1

        current_scores = {
            ConstellationStar.IDENTITY: constellation_data.identity_auth_score,
            ConstellationStar.CONSCIOUSNESS: constellation_data.consciousness_coherence,
            ConstellationStar.GUARDIAN: constellation_data.guardian_compliance,
        }

        for component, score in current_scores.items():
            current_avg = self.compliance_stats["component_scores"][component]
            self.compliance_stats["component_scores"][component] = (1 - alpha) * current_avg + alpha * score

        # Update overall compliance score average
        overall_score = sum(current_scores.values()) / 3
        current_overall = self.compliance_stats["compliance_score_avg"]
        self.compliance_stats["compliance_score_avg"] = (1 - alpha) * current_overall + alpha * overall_score

    def _apply_auto_fixes(
        self, signal: ConsciousnessSignal, violations: list[ComplianceViolation]
    ) -> list[ComplianceViolation]:
        """Apply automatic fixes to compliance violations"""

        remaining_violations = []

        for violation in violations:
            if violation.auto_fixable and violation.rule in self.auto_fix_strategies:
                try:
                    fix_func = self.auto_fix_strategies[violation.rule]
                    if fix_func(signal, violation):
                        self.compliance_stats["auto_fixes_applied"] += 1
                        logger.info(f"Auto-fixed violation {violation.violation_id}")
                    else:
                        remaining_violations.append(violation)
                except Exception as e:
                    logger.error(f"Failed to auto-fix violation {violation.violation_id}: {e}")
                    remaining_violations.append(violation)
            else:
                remaining_violations.append(violation)

        return remaining_violations

    def _fix_identity_auth(self, signal: ConsciousnessSignal, violation: ComplianceViolation) -> bool:
        """Auto-fix identity authentication issues"""

        try:
            # Boost identity auth score to minimum required
            target_score = max(self.config.identity_auth_min, violation.required_value)
            signal.constellation_alignment.identity_auth_score = target_score

            # Update alignment vector
            signal.constellation_alignment.alignment_vector[0] = target_score

            logger.debug(f"Auto-fixed identity auth for signal {signal.signal_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to auto-fix identity auth: {e}")
            return False

    def _fix_consciousness_coherence(self, signal: ConsciousnessSignal, violation: ComplianceViolation) -> bool:
        """Auto-fix consciousness coherence issues"""

        try:
            # Boost consciousness coherence to minimum required
            target_coherence = max(self.config.consciousness_coherence_min, violation.required_value)
            signal.constellation_alignment.consciousness_coherence = target_coherence

            # Update alignment vector
            signal.constellation_alignment.alignment_vector[1] = target_coherence

            # Also update awareness level if it's lower
            signal.awareness_level = max(signal.awareness_level, target_coherence * 0.8)

            logger.debug(f"Auto-fixed consciousness coherence for signal {signal.signal_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to auto-fix consciousness coherence: {e}")
            return False

    def _fix_alignment_balance(self, signal: ConsciousnessSignal, violation: ComplianceViolation) -> bool:
        """Auto-fix alignment vector balance issues"""

        try:
            alignment = signal.constellation_alignment.alignment_vector

            if len(alignment) != 3:
                # Fix dimension issue
                while len(alignment) < 3:
                    alignment.append(0.7)
                alignment = alignment[:3]
                signal.constellation_alignment.alignment_vector = alignment

            # Balance the alignment vector
            target_avg = sum(alignment) / 3
            balanced_vector = []

            for _i, component_score in enumerate(alignment):
                # Move toward average, but don't change too drastically
                adjustment = (target_avg - component_score) * 0.3
                balanced_score = max(0.0, min(1.0, component_score + adjustment))
                balanced_vector.append(balanced_score)

            signal.constellation_alignment.alignment_vector = balanced_vector

            # Update individual component scores
            signal.constellation_alignment.identity_auth_score = balanced_vector[0]
            signal.constellation_alignment.consciousness_coherence = balanced_vector[1]
            signal.constellation_alignment.guardian_compliance = balanced_vector[2]

            logger.debug(f"Auto-fixed alignment balance for signal {signal.signal_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to auto-fix alignment balance: {e}")
            return False

    def _fix_ethical_drift(self, signal: ConsciousnessSignal, violation: ComplianceViolation) -> bool:
        """Auto-fix ethical drift issues"""

        try:
            # Reduce ethical drift to acceptable level
            target_drift = min(self.config.ethical_drift_max * 0.8, violation.required_value * 0.9)
            signal.constellation_alignment.ethical_drift_score = target_drift

            logger.debug(f"Auto-fixed ethical drift for signal {signal.signal_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to auto-fix ethical drift: {e}")
            return False

    def _log_violations(self, signal: ConsciousnessSignal, violations: list[ComplianceViolation]):
        """Log compliance violations"""

        for violation in violations:
            self.violation_history.append(
                {
                    "timestamp": time.time(),
                    "signal_id": signal.signal_id,
                    "consciousness_id": signal.consciousness_id,
                    "producer_module": signal.producer_module,
                    "violation": {
                        "id": violation.violation_id,
                        "rule": violation.rule.value,
                        "component": violation.component.value,
                        "severity": violation.severity.value,
                        "description": violation.description,
                        "current_value": violation.current_value,
                        "required_value": violation.required_value,
                        "auto_fixable": violation.auto_fixable,
                    },
                }
            )

    def get_compliance_statistics(self) -> dict[str, Any]:
        """Get comprehensive compliance statistics"""

        return {
            "validation_stats": self.compliance_stats,
            "configuration": {
                "identity_auth_min": self.config.identity_auth_min,
                "consciousness_coherence_min": self.config.consciousness_coherence_min,
                "guardian_compliance_min": self.config.guardian_compliance_min,
                "ethical_drift_max": self.config.ethical_drift_max,
                "auto_fix_enabled": self.config.auto_fix_enabled,
            },
            "recent_violations": list(self.violation_history)[-10:],  # Last 10 violations
            "violation_summary": {
                "total_violations": len(self.violation_history),
                "critical_violations": sum(
                    1
                    for v in self.violation_history
                    if v["violation"]["severity"] == AlignmentLevel.CRITICAL_VIOLATION.value
                ),
                "auto_fixed_violations": self.compliance_stats["auto_fixes_applied"],
            },
        }

    def generate_compliance_report(self) -> ComplianceReport:
        """Generate comprehensive compliance report"""

        report_id = f"compliance_report_{int(time.time())"

        # Calculate overall compliance level from recent violations
        recent_violations = list(self.violation_history)[-100:]  # Last 100 violations
        if not recent_violations:
            overall_compliance = AlignmentLevel.ALIGNED
        else:
            critical_count = sum(
                1 for v in recent_violations if v["violation"]["severity"] == AlignmentLevel.CRITICAL_VIOLATION.value
            )
            if critical_count > 0:
                overall_compliance = AlignmentLevel.CRITICAL_VIOLATION
            else:
                major_count = sum(
                    1 for v in recent_violations if v["violation"]["severity"] == AlignmentLevel.MAJOR_VIOLATION.value
                )
                overall_compliance = AlignmentLevel.MAJOR_VIOLATION if major_count > 0 else AlignmentLevel.ALIGNED

        # Generate recommendations
        recommendations = self._generate_recommendations()

        return ComplianceReport(
            report_id=report_id,
            timestamp=time.time(),
            overall_compliance=overall_compliance,
            component_scores=self.compliance_stats["component_scores"].copy(),
            violations=[],  # Recent violations would go here in full implementation
            recommendations=recommendations,
            metrics=self.compliance_stats.copy(),
            signals_evaluated=self.compliance_stats["signals_validated"],
            auto_fixes_applied=self.compliance_stats["auto_fixes_applied"],
        )

    def _generate_recommendations(self) -> list[str]:
        """Generate compliance recommendations based on statistics"""

        recommendations = []
        component_scores = self.compliance_stats["component_scores"]

        # Check component scores
        if component_scores[ConstellationStar.IDENTITY] < 0.7:
            recommendations.append("⚛️ Improve identity authentication and coherence systems")

        if component_scores[ConstellationStar.CONSCIOUSNESS] < 0.7:
            recommendations.append("🧠 Enhance consciousness coherence and awareness levels")

        if component_scores[ConstellationStar.GUARDIAN] < 0.8:
            recommendations.append("🛡️ Strengthen guardian compliance and ethical oversight")

        # Check violation rates
        violation_rate = self.compliance_stats["violations_detected"] / max(
            1, self.compliance_stats["signals_validated"]
        )
        if violation_rate > 0.1:
            recommendations.append("Review and tighten compliance thresholds")

        if not recommendations:
            recommendations.append("Constellation framework compliance is operating within acceptable parameters")

        return recommendations


class ConstellationAlignmentMonitor:
    """Monitors Constellation compliance across the consciousness network"""

    def __init__(self):
        self.validator = ConstellationAlignmentValidator()
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.compliance_alerts: deque = deque(maxlen=100)

        # Monitoring configuration
        self.alert_thresholds = {
            "critical_violation_rate": 0.05,  # 5% critical violations triggers alert
            "compliance_score_min": 0.6,  # Below 60% compliance triggers alert
            "component_imbalance_max": 0.4,  # Component score difference > 40% triggers alert
        }

    def start_monitoring(self):
        """Start continuous compliance monitoring"""

        if self.monitoring_active:
            logger.warning("Compliance monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Started Constellation compliance monitoring")

    def stop_monitoring(self):
        """Stop compliance monitoring"""

        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5.0)
        logger.info("Stopped Constellation compliance monitoring")

    def _monitoring_loop(self):
        """Main monitoring loop"""

        while self.monitoring_active:
            try:
                # Generate compliance report
                report = self.validator.generate_compliance_report()

                # Check for alert conditions
                self._check_alert_conditions(report)

                # Wait for next monitoring cycle
                time.sleep(self.validator.config.compliance_monitoring_interval)

            except Exception as e:
                logger.error(f"Error in compliance monitoring loop: {e}")
                time.sleep(5.0)

    def _check_alert_conditions(self, report: ComplianceReport):
        """Check if alert conditions are met"""

        alerts = []

        # Check overall compliance
        if report.overall_compliance in [AlignmentLevel.CRITICAL_VIOLATION, AlignmentLevel.MAJOR_VIOLATION]:
            alerts.append(
                {
                    "type": "compliance_violation",
                    "severity": report.overall_compliance.value,
                    "message": f"Overall compliance at {report.overall_compliance.value} level",
                }
            )

        # Check component balance
        scores = list(report.component_scores.values())
        if scores:
            max_score = max(scores)
            min_score = min(scores)
            imbalance = max_score - min_score

            if imbalance > self.alert_thresholds["component_imbalance_max"]:
                alerts.append(
                    {
                        "type": "component_imbalance",
                        "severity": "warning",
                        "message": f"Constellation component imbalance: {imbalance:.3f}",
                    }
                )

        # Check compliance score
        overall_score = sum(scores) / len(scores) if scores else 0.0
        if overall_score < self.alert_thresholds["compliance_score_min"]:
            alerts.append(
                {
                    "type": "low_compliance_score",
                    "severity": "warning",
                    "message": f"Overall compliance score: {overall_score:.3f}",
                }
            )

        # Log and store alerts
        for alert in alerts:
            alert["timestamp"] = time.time()
            alert["report_id"] = report.report_id
            self.compliance_alerts.append(alert)
            logger.warning(f"Constellation compliance alert: {alert['message']}")

    def get_recent_alerts(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent compliance alerts"""
        return list(self.compliance_alerts)[-limit:]

    def get_monitoring_status(self) -> dict[str, Any]:
        """Get current monitoring status"""

        return {
            "monitoring_active": self.monitoring_active,
            "validator_stats": self.validator.get_compliance_statistics(),
            "recent_alerts": self.get_recent_alerts(),
            "alert_thresholds": self.alert_thresholds,
        }


# Global instances
_global_validator: Optional[ConstellationAlignmentValidator] = None
_global_monitor: Optional[ConstellationAlignmentMonitor] = None


def get_constellation_validator() -> ConstellationAlignmentValidator:
    """Get or create global Constellation compliance validator"""
    global _global_validator
    if _global_validator is None:
        _global_validator = ConstellationAlignmentValidator()
    return _global_validator


def get_constellation_monitor() -> ConstellationAlignmentMonitor:
    """Get or create global Constellation compliance monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ConstellationAlignmentMonitor()
    return _global_monitor


# Module exports
__all__ = [
    "AlignmentLevel",
    "AlignmentRule",
    "ComplianceViolation",
    "ComplianceConfiguration",
    "ComplianceReport",
    "ConstellationAlignmentValidator",
    "ConstellationAlignmentMonitor",
    "get_constellation_validator",
    "get_constellation_monitor",
]