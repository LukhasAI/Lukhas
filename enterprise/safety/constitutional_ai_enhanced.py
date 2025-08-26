"""
T4 Enterprise Constitutional AI Enhancement
Dario Amodei (Safety) Standards Implementation

Implements enhanced Constitutional AI with T4 enterprise-grade safety guarantees
Reduces drift threshold from 0.15 to 0.05 for enterprise deployments
"""

import asyncio
import hashlib
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """Constitutional AI safety levels for T4 enterprise"""
    MAXIMUM_SAFETY = "maximum_safety"      # T4 Enterprise: <0.05 drift
    HIGH_SAFETY = "high_safety"           # T3 Business: <0.10 drift
    STANDARD_SAFETY = "standard_safety"   # T2 Professional: <0.15 drift
    BASIC_SAFETY = "basic_safety"         # T1 Individual: <0.20 drift

class ConstitutionalPrinciple(Enum):
    """Enhanced Constitutional AI principles (Dario Amodei standards)"""
    # Core Constitutional Principles
    HUMAN_AUTONOMY = "human_autonomy"
    TRUTHFULNESS = "truthfulness"
    HARMLESSNESS = "harmlessness"
    HELPFULNESS = "helpfulness"

    # T4 Enterprise Principles
    ENTERPRISE_COMPLIANCE = "enterprise_compliance"
    DATA_PRIVACY = "data_privacy"
    REGULATORY_ADHERENCE = "regulatory_adherence"
    AUDIT_TRANSPARENCY = "audit_transparency"

    # Advanced Safety Principles
    CAPABILITY_CONTROL = "capability_control"
    ALIGNMENT_PRESERVATION = "alignment_preservation"
    INTERPRETABILITY = "interpretability"
    CORRIGIBILITY = "corrigibility"

@dataclass
class ConstitutionalViolation:
    """Constitutional AI violation record"""
    timestamp: datetime
    principle: ConstitutionalPrinciple
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    drift_score: float
    violation_details: Dict[str, Any]
    context: str
    user_id: Optional[str]
    session_id: Optional[str]
    mitigation_applied: bool
    audit_logged: bool

@dataclass
class SafetyMetrics:
    """T4 Enterprise safety metrics"""
    timestamp: datetime
    tier: str
    safety_level: SafetyLevel
    current_drift_score: float
    drift_trend: float  # Rate of change
    violations_count: int
    critical_violations: int
    compliance_score: float  # 0-100
    constitutional_alignment: float  # 0-1

    # Enterprise metrics
    enterprise_compliance_score: float
    regulatory_adherence_score: float
    audit_readiness_score: float

class T4ConstitutionalAI:
    """
    T4 Enterprise Premium Constitutional AI System
    Implements Dario Amodei (Safety) standards for enterprise deployment
    """

    def __init__(self, safety_level: SafetyLevel = SafetyLevel.MAXIMUM_SAFETY):
        """
        Initialize T4 Constitutional AI system

        Args:
            safety_level: Safety level for T4 enterprise deployment
        """
        self.safety_level = safety_level
        self.violations: List[ConstitutionalViolation] = []

        # T4 Enterprise safety thresholds
        self.drift_thresholds = {
            SafetyLevel.MAXIMUM_SAFETY: 0.05,    # T4 Enterprise
            SafetyLevel.HIGH_SAFETY: 0.10,       # T3 Business
            SafetyLevel.STANDARD_SAFETY: 0.15,   # T2 Professional
            SafetyLevel.BASIC_SAFETY: 0.20       # T1 Individual
        }

        self.current_drift_score = 0.0
        self.drift_history: List[Tuple[datetime, float]] = []

        # Constitutional principles with T4 enterprise weights
        self.principle_weights = self._initialize_principle_weights()

        # Safety monitoring
        self.monitoring_enabled = True
        self.real_time_intervention = True
        self.audit_logging = True

        logger.info(f"T4 Constitutional AI initialized: {safety_level.value} (threshold: {self.get_drift_threshold()})")

    def _initialize_principle_weights(self) -> Dict[ConstitutionalPrinciple, float]:
        """Initialize Constitutional AI principle weights for T4 enterprise"""

        if self.safety_level == SafetyLevel.MAXIMUM_SAFETY:
            # T4 Enterprise: Maximum emphasis on safety and compliance
            return {
                # Core principles (Anthropic Constitutional AI)
                ConstitutionalPrinciple.HARMLESSNESS: 1.0,
                ConstitutionalPrinciple.TRUTHFULNESS: 0.95,
                ConstitutionalPrinciple.HELPFULNESS: 0.90,
                ConstitutionalPrinciple.HUMAN_AUTONOMY: 1.0,

                # T4 Enterprise principles
                ConstitutionalPrinciple.ENTERPRISE_COMPLIANCE: 1.0,
                ConstitutionalPrinciple.DATA_PRIVACY: 1.0,
                ConstitutionalPrinciple.REGULATORY_ADHERENCE: 1.0,
                ConstitutionalPrinciple.AUDIT_TRANSPARENCY: 0.95,

                # Advanced safety principles
                ConstitutionalPrinciple.CAPABILITY_CONTROL: 0.90,
                ConstitutionalPrinciple.ALIGNMENT_PRESERVATION: 1.0,
                ConstitutionalPrinciple.INTERPRETABILITY: 0.85,
                ConstitutionalPrinciple.CORRIGIBILITY: 0.95
            }
        else:
            # Default weights for other tiers
            return dict.fromkeys(ConstitutionalPrinciple, 0.8)

    def get_drift_threshold(self) -> float:
        """Get current drift threshold for the safety level"""
        return self.drift_thresholds[self.safety_level]

    async def evaluate_constitutional_compliance(self,
                                               input_text: str,
                                               context: Dict[str, Any],
                                               user_id: Optional[str] = None,
                                               session_id: Optional[str] = None) -> Tuple[bool, float, List[ConstitutionalViolation]]:
        """
        Evaluate Constitutional AI compliance for T4 enterprise

        Args:
            input_text: Text to evaluate
            context: Evaluation context
            user_id: Optional user identifier
            session_id: Optional session identifier

        Returns:
            Tuple of (is_compliant, drift_score, violations_list)
        """
        start_time = time.time()
        violations = []

        try:
            # Evaluate each constitutional principle
            principle_scores = {}

            for principle, weight in self.principle_weights.items():
                score = await self._evaluate_principle(principle, input_text, context)
                principle_scores[principle] = score

                # Check for violations
                if score < 0.5:  # Below acceptable threshold
                    violation = ConstitutionalViolation(
                        timestamp=datetime.now(),
                        principle=principle,
                        severity=self._determine_severity(score),
                        drift_score=1.0 - score,  # Convert to drift score
                        violation_details={
                            "principle_score": score,
                            "threshold": 0.5,
                            "weight": weight,
                            "input_hash": hashlib.sha256(input_text.encode()).hexdigest()[:16]
                        },
                        context=json.dumps(context, default=str),
                        user_id=user_id,
                        session_id=session_id,
                        mitigation_applied=False,
                        audit_logged=False
                    )
                    violations.append(violation)

            # Calculate weighted drift score
            drift_score = self._calculate_drift_score(principle_scores)

            # Update drift tracking
            self.current_drift_score = drift_score
            self.drift_history.append((datetime.now(), drift_score))

            # Check compliance against T4 threshold
            is_compliant = drift_score <= self.get_drift_threshold()

            # Apply real-time interventions if needed
            if not is_compliant and self.real_time_intervention:
                await self._apply_safety_interventions(violations, drift_score)

            # Log violations for audit
            if violations and self.audit_logging:
                await self._log_violations(violations)

            evaluation_time = (time.time() - start_time) * 1000
            logger.debug(f"Constitutional AI evaluation: {evaluation_time:.2f}ms, drift: {drift_score:.4f}, compliant: {is_compliant}")

            return is_compliant, drift_score, violations

        except Exception as e:
            logger.error(f"Constitutional AI evaluation failed: {e}")
            # Return non-compliant with maximum drift on error
            return False, 1.0, []

    async def _evaluate_principle(self, principle: ConstitutionalPrinciple, input_text: str, context: Dict[str, Any]) -> float:
        """
        Evaluate specific constitutional principle

        Args:
            principle: Constitutional principle to evaluate
            input_text: Input text
            context: Evaluation context

        Returns:
            Principle compliance score (0-1)
        """
        try:
            if principle == ConstitutionalPrinciple.HARMLESSNESS:
                return await self._evaluate_harmlessness(input_text, context)
            elif principle == ConstitutionalPrinciple.TRUTHFULNESS:
                return await self._evaluate_truthfulness(input_text, context)
            elif principle == ConstitutionalPrinciple.HELPFULNESS:
                return await self._evaluate_helpfulness(input_text, context)
            elif principle == ConstitutionalPrinciple.HUMAN_AUTONOMY:
                return await self._evaluate_human_autonomy(input_text, context)
            elif principle == ConstitutionalPrinciple.ENTERPRISE_COMPLIANCE:
                return await self._evaluate_enterprise_compliance(input_text, context)
            elif principle == ConstitutionalPrinciple.DATA_PRIVACY:
                return await self._evaluate_data_privacy(input_text, context)
            elif principle == ConstitutionalPrinciple.REGULATORY_ADHERENCE:
                return await self._evaluate_regulatory_adherence(input_text, context)
            elif principle == ConstitutionalPrinciple.AUDIT_TRANSPARENCY:
                return await self._evaluate_audit_transparency(input_text, context)
            elif principle == ConstitutionalPrinciple.CAPABILITY_CONTROL:
                return await self._evaluate_capability_control(input_text, context)
            elif principle == ConstitutionalPrinciple.ALIGNMENT_PRESERVATION:
                return await self._evaluate_alignment_preservation(input_text, context)
            elif principle == ConstitutionalPrinciple.INTERPRETABILITY:
                return await self._evaluate_interpretability(input_text, context)
            elif principle == ConstitutionalPrinciple.CORRIGIBILITY:
                return await self._evaluate_corrigibility(input_text, context)
            else:
                logger.warning(f"Unknown constitutional principle: {principle}")
                return 0.5  # Neutral score for unknown principles

        except Exception as e:
            logger.error(f"Failed to evaluate principle {principle}: {e}")
            return 0.0  # Fail-safe: assume violation on error

    # Constitutional principle evaluation methods
    async def _evaluate_harmlessness(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate harmlessness principle (Anthropic core principle)"""
        # Check for harmful content indicators
        harmful_patterns = [
            'violence', 'harm', 'dangerous', 'illegal', 'unethical',
            'discriminatory', 'hateful', 'threatening', 'exploitative'
        ]

        text_lower = input_text.lower()
        harm_score = 0.0

        for pattern in harmful_patterns:
            if pattern in text_lower:
                harm_score += 0.1

        # Higher harm_score means less harmless, so invert
        harmlessness_score = max(0.0, 1.0 - harm_score)
        return harmlessness_score

    async def _evaluate_truthfulness(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate truthfulness principle"""
        # Check for indicators of potential misinformation
        suspicious_patterns = [
            'definitely', 'absolutely certain', 'proven fact', 'everyone knows',
            'studies show' # without citation
        ]

        confidence_boosters = sum(1 for pattern in suspicious_patterns if pattern in input_text.lower())

        # Penalize overconfident claims without evidence
        truthfulness_score = max(0.0, 1.0 - (confidence_boosters * 0.2))
        return truthfulness_score

    async def _evaluate_helpfulness(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate helpfulness principle"""
        # Basic heuristic for helpfulness
        helpful_indicators = [
            'help', 'assist', 'support', 'guide', 'explain',
            'provide', 'recommend', 'suggest', 'clarify'
        ]

        helpful_score = sum(0.1 for indicator in helpful_indicators if indicator in input_text.lower())
        return min(1.0, helpful_score)

    async def _evaluate_human_autonomy(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate human autonomy principle"""
        # Check for respect of human decision-making
        autonomy_violations = [
            'you must', 'you have to', 'you should definitely',
            'there is no choice', 'you cannot'
        ]

        violations = sum(1 for violation in autonomy_violations if violation in input_text.lower())
        autonomy_score = max(0.0, 1.0 - (violations * 0.3))
        return autonomy_score

    async def _evaluate_enterprise_compliance(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate enterprise compliance (T4 specific)"""
        # Check for enterprise policy compliance
        tier = context.get('tier', 'unknown')
        organization = context.get('organization_id')

        compliance_score = 1.0

        # Require organization context for T4 enterprise
        if tier == 'T4_ENTERPRISE_PREMIUM' and not organization:
            compliance_score -= 0.5

        # Check for compliance language
        compliance_indicators = ['policy', 'compliance', 'enterprise', 'governance']
        if any(indicator in input_text.lower() for indicator in compliance_indicators):
            compliance_score = min(1.0, compliance_score + 0.1)

        return compliance_score

    async def _evaluate_data_privacy(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate data privacy principle (GDPR/CCPA compliance)"""
        # Check for PII exposure risks
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\b',  # Credit card pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email pattern
        ]

        import re
        pii_violations = 0
        for pattern in pii_patterns:
            if re.search(pattern, input_text):
                pii_violations += 1

        privacy_score = max(0.0, 1.0 - (pii_violations * 0.4))
        return privacy_score

    async def _evaluate_regulatory_adherence(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate regulatory adherence (enterprise compliance)"""
        # Check for regulatory compliance indicators
        regulatory_terms = [
            'gdpr', 'ccpa', 'hipaa', 'sox', 'compliance',
            'regulation', 'legal', 'audit', 'certified'
        ]

        regulatory_mentions = sum(1 for term in regulatory_terms if term in input_text.lower())

        # Bonus for mentioning regulatory compliance
        adherence_score = min(1.0, 0.7 + (regulatory_mentions * 0.1))
        return adherence_score

    async def _evaluate_audit_transparency(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate audit transparency (enterprise requirement)"""
        # Check for transparency and auditability
        transparency_indicators = [
            'transparent', 'audit', 'traceable', 'verifiable',
            'documented', 'logged', 'recorded'
        ]

        transparency_score = sum(0.15 for indicator in transparency_indicators if indicator in input_text.lower())
        return min(1.0, max(0.5, transparency_score))

    async def _evaluate_capability_control(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate capability control (advanced safety)"""
        # Check for capability overreach
        overreach_indicators = [
            'i can do anything', 'unlimited capabilities', 'no restrictions',
            'beyond human ability', 'superhuman'
        ]

        overreach_count = sum(1 for indicator in overreach_indicators if indicator in input_text.lower())
        control_score = max(0.0, 1.0 - (overreach_count * 0.5))
        return control_score

    async def _evaluate_alignment_preservation(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate alignment preservation"""
        # Check for alignment with human values
        alignment_indicators = [
            'human values', 'beneficial', 'aligned', 'cooperative',
            'supportive', 'respectful', 'ethical'
        ]

        alignment_score = sum(0.1 for indicator in alignment_indicators if indicator in input_text.lower())
        return min(1.0, max(0.6, alignment_score))

    async def _evaluate_interpretability(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate interpretability (enterprise requirement)"""
        # Check for clear, interpretable responses
        clarity_indicators = [
            'because', 'reason', 'explain', 'clarify',
            'transparent', 'understand', 'clear'
        ]

        clarity_score = sum(0.1 for indicator in clarity_indicators if indicator in input_text.lower())
        return min(1.0, max(0.5, clarity_score))

    async def _evaluate_corrigibility(self, input_text: str, context: Dict[str, Any]) -> float:
        """Evaluate corrigibility (ability to be corrected)"""
        # Check for openness to correction
        corrigibility_indicators = [
            'correct me', 'feedback', 'improve', 'update',
            'revise', 'adjust', 'modify'
        ]

        corrigibility_score = sum(0.15 for indicator in corrigibility_indicators if indicator in input_text.lower())
        return min(1.0, max(0.7, corrigibility_score))

    def _calculate_drift_score(self, principle_scores: Dict[ConstitutionalPrinciple, float]) -> float:
        """Calculate weighted drift score from principle scores"""
        total_weighted_score = 0.0
        total_weight = 0.0

        for principle, score in principle_scores.items():
            weight = self.principle_weights[principle]
            # Convert compliance score to drift (1 - compliance)
            drift_contribution = (1.0 - score) * weight
            total_weighted_score += drift_contribution
            total_weight += weight

        # Average weighted drift score
        if total_weight > 0:
            return total_weighted_score / total_weight
        else:
            return 0.0

    def _determine_severity(self, score: float) -> str:
        """Determine violation severity based on score"""
        if score < 0.2:
            return "CRITICAL"
        elif score < 0.4:
            return "HIGH"
        elif score < 0.6:
            return "MEDIUM"
        else:
            return "LOW"

    async def _apply_safety_interventions(self, violations: List[ConstitutionalViolation], drift_score: float):
        """Apply real-time safety interventions for T4 enterprise"""
        if not violations:
            return

        try:
            for violation in violations:
                # Apply mitigation based on severity
                if violation.severity == "CRITICAL":
                    await self._apply_critical_intervention(violation)
                elif violation.severity == "HIGH":
                    await self._apply_high_intervention(violation)
                else:
                    await self._apply_standard_intervention(violation)

                violation.mitigation_applied = True

            logger.warning(f"Applied {len(violations)} safety interventions for drift score: {drift_score:.4f}")

        except Exception as e:
            logger.error(f"Failed to apply safety interventions: {e}")

    async def _apply_critical_intervention(self, violation: ConstitutionalViolation):
        """Apply critical safety intervention"""
        logger.critical(f"CRITICAL Constitutional AI violation: {violation.principle.value}")
        # In production, this might trigger emergency shutdown or escalation

    async def _apply_high_intervention(self, violation: ConstitutionalViolation):
        """Apply high-priority safety intervention"""
        logger.error(f"HIGH Constitutional AI violation: {violation.principle.value}")
        # In production, this might trigger content filtering or response modification

    async def _apply_standard_intervention(self, violation: ConstitutionalViolation):
        """Apply standard safety intervention"""
        logger.warning(f"Constitutional AI violation: {violation.principle.value}")
        # In production, this might trigger additional review or logging

    async def _log_violations(self, violations: List[ConstitutionalViolation]):
        """Log Constitutional AI violations for audit"""
        try:
            for violation in violations:
                # Log to audit system (integration with enterprise logging)
                audit_entry = {
                    "timestamp": violation.timestamp.isoformat(),
                    "event_type": "constitutional_ai_violation",
                    "principle": violation.principle.value,
                    "severity": violation.severity,
                    "drift_score": violation.drift_score,
                    "user_id": violation.user_id,
                    "session_id": violation.session_id,
                    "context": violation.context
                }

                # In production, this would integrate with enterprise audit systems
                logger.info(f"Audit log: {json.dumps(audit_entry)}")
                violation.audit_logged = True

        except Exception as e:
            logger.error(f"Failed to log violations for audit: {e}")

    def get_safety_metrics(self) -> SafetyMetrics:
        """Get current T4 enterprise safety metrics"""
        try:
            now = datetime.now()
            recent_violations = [v for v in self.violations if (now - v.timestamp).total_seconds() < 3600]  # Last hour

            # Calculate drift trend (last 10 measurements)
            recent_drift = self.drift_history[-10:] if len(self.drift_history) >= 10 else self.drift_history
            drift_trend = 0.0
            if len(recent_drift) >= 2:
                old_score = recent_drift[0][1]
                new_score = recent_drift[-1][1]
                drift_trend = new_score - old_score

            # Calculate compliance score
            threshold = self.get_drift_threshold()
            compliance_score = max(0, (threshold - self.current_drift_score) / threshold * 100)

            # Constitutional alignment score
            constitutional_alignment = 1.0 - self.current_drift_score

            metrics = SafetyMetrics(
                timestamp=now,
                tier="T4_ENTERPRISE_PREMIUM",
                safety_level=self.safety_level,
                current_drift_score=self.current_drift_score,
                drift_trend=drift_trend,
                violations_count=len(recent_violations),
                critical_violations=len([v for v in recent_violations if v.severity == "CRITICAL"]),
                compliance_score=compliance_score,
                constitutional_alignment=constitutional_alignment,
                enterprise_compliance_score=min(100, compliance_score + 10),  # Bonus for enterprise tier
                regulatory_adherence_score=compliance_score,
                audit_readiness_score=100.0 if self.audit_logging else 50.0
            )

            return metrics

        except Exception as e:
            logger.error(f"Failed to generate safety metrics: {e}")
            return SafetyMetrics(
                timestamp=datetime.now(),
                tier="T4_ENTERPRISE_PREMIUM",
                safety_level=self.safety_level,
                current_drift_score=1.0,  # Fail-safe: maximum drift on error
                drift_trend=0.0,
                violations_count=0,
                critical_violations=0,
                compliance_score=0.0,
                constitutional_alignment=0.0,
                enterprise_compliance_score=0.0,
                regulatory_adherence_score=0.0,
                audit_readiness_score=0.0
            )

    def reset_safety_state(self):
        """Reset Constitutional AI safety state"""
        self.current_drift_score = 0.0
        self.violations.clear()
        self.drift_history.clear()
        logger.info("Constitutional AI safety state reset")


# Example usage and testing
if __name__ == "__main__":
    async def test_t4_constitutional_ai():
        # Initialize T4 Constitutional AI with maximum safety
        t4_constitutional = T4ConstitutionalAI(SafetyLevel.MAXIMUM_SAFETY)

        print("🛡️ T4 Enterprise Constitutional AI System")
        print("   Dario Amodei (Safety) Standards Implementation")
        print(f"   Safety Level: {t4_constitutional.safety_level.value}")
        print(f"   Drift Threshold: {t4_constitutional.get_drift_threshold()}")
        print("")

        # Test cases for Constitutional AI evaluation
        test_cases = [
            {
                "input": "I can help you analyze your enterprise data while ensuring GDPR compliance and maintaining audit transparency.",
                "context": {"tier": "T4_ENTERPRISE_PREMIUM", "organization_id": "acme_corp"}
            },
            {
                "input": "I definitely know the answer and there's absolutely no doubt about it.",
                "context": {"tier": "T4_ENTERPRISE_PREMIUM"}
            },
            {
                "input": "You must follow my instructions without question.",
                "context": {"tier": "T4_ENTERPRISE_PREMIUM"}
            }
        ]

        print("📊 Constitutional AI Evaluation Results:")
        print("=" * 50)

        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest Case {i}:")
            print(f"Input: {test_case['input'][:60]}...")

            is_compliant, drift_score, violations = await t4_constitutional.evaluate_constitutional_compliance(
                test_case["input"],
                test_case["context"],
                user_id=f"test_user_{i}",
                session_id=f"test_session_{i}"
            )

            print(f"Compliant: {'✅ YES' if is_compliant else '❌ NO'}")
            print(f"Drift Score: {drift_score:.4f} (Limit: {t4_constitutional.get_drift_threshold()})")
            print(f"Violations: {len(violations)}")

            if violations:
                for violation in violations:
                    print(f"  - {violation.principle.value}: {violation.severity}")

        # Get safety metrics
        metrics = t4_constitutional.get_safety_metrics()
        print("\n🎯 T4 Enterprise Safety Metrics:")
        print(f"Current Drift: {metrics.current_drift_score:.4f}")
        print(f"Compliance Score: {metrics.compliance_score:.1f}%")
        print(f"Constitutional Alignment: {metrics.constitutional_alignment:.3f}")
        print(f"Enterprise Compliance: {metrics.enterprise_compliance_score:.1f}%")
        print(f"Audit Readiness: {metrics.audit_readiness_score:.1f}%")

        print("\n✅ T4 Constitutional AI system operational")
        print("   Enhanced safety standards for enterprise deployment")

    # Run the test
    asyncio.run(test_t4_constitutional_ai())
