"""

#TAG:governance
#TAG:ethics
#TAG:neuroplastic
#TAG:colony


Ethical Hierarchy for lukhas AI System

AI Level 5 ethical framework with legal compliance integration.
Implements advanced ethical reasoning with legal compliance frameworks.

Based on Lukhas repository implementation with LUKHAS AI integration.
Based on Lukhas repository implementation with lukhas AI integration.
"""
import logging
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class EthicalPrinciple(Enum):
    """Core ethical principles"""

    HUMAN_DIGNITY = "human_dignity"
    AUTONOMY = "autonomy"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"
    JUSTICE = "justice"
    FAIRNESS = "fairness"
    TRANSPARENCY = "transparency"
    PRIVACY_PROTECTION = "privacy_protection"
    ACCOUNTABILITY = "accountability"
    ECOLOGICAL_BALANCE = "ecological_balance"


class ComplianceFramework(Enum):
    """Legal compliance frameworks"""

    EU_AI_ACT_2025 = "EU_AI_ACT_2025"
    IEEE_7000_2024 = "IEEE_7000-2024"
    OECD_AI_PRINCIPLES = "OECD_AI_PRINCIPLES"
    GDPR = "GDPR"
    ISO_27001 = "ISO_27001"
    NIST_AI_RMF = "NIST_AI_RMF"


class EthicalSeverity(Enum):
    """Ethical concern severity levels"""

    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    CRITICAL = "critical"


class EthicalHierarchy:
    """
    AI Level 5 ethical framework with legal compliance integration.

    Implements comprehensive ethical reasoning that adapts to context
    while maintaining alignment with international legal frameworks.
    """

    def __init__(self):
        self.logger = logging.getLogger("ΛAGI.ethical_hierarchy")
        self.logger = logging.getLogger("lukhasAGI.ethical_hierarchy")

        # Legal compliance frameworks
        self.legal_frameworks = [
            ComplianceFramework.EU_AI_ACT_2025,
            ComplianceFramework.IEEE_7000_2024,
            ComplianceFramework.OECD_AI_PRINCIPLES,
            ComplianceFramework.GDPR,
            ComplianceFramework.ISO_27001,
            ComplianceFramework.NIST_AI_RMF,
        ]

        # Base ethical weights (can be dynamically adjusted)
        self.context_weights = {
            EthicalPrinciple.HUMAN_DIGNITY: 0.95,  # Highest priority
            EthicalPrinciple.NON_MALEFICENCE: 0.90,  # Do no harm
            EthicalPrinciple.PRIVACY_PROTECTION: 0.85,  # Privacy is fundamental
            EthicalPrinciple.AUTONOMY: 0.80,  # Respect human agency
            EthicalPrinciple.TRANSPARENCY: 0.75,  # Explainable AI
            EthicalPrinciple.JUSTICE: 0.75,  # Fair treatment
            EthicalPrinciple.FAIRNESS: 0.70,  # Unbiased decisions
            EthicalPrinciple.BENEFICENCE: 0.70,  # Promote well-being
            EthicalPrinciple.ACCOUNTABILITY: 0.65,  # Responsible AI
            EthicalPrinciple.ECOLOGICAL_BALANCE: 0.60,  # Environmental consideration
        }

        # Legal compliance requirements by framework
        self.compliance_requirements = {
            ComplianceFramework.EU_AI_ACT_2025: {
                "prohibited_practices": [
                    "subliminal_manipulation",
                    "behavioral_manipulation",
                    "social_scoring",
                    "real_time_biometric_identification",
                ],
                "high_risk_requirements": [
                    "human_oversight",
                    "transparency",
                    "risk_assessment",
                    "documentation",
                ],
                "fundamental_rights": [
                    "dignity",
                    "freedom",
                    "equality",
                    "privacy",
                    "data_protection",
                ],
            },
            ComplianceFramework.GDPR: {
                "data_principles": [
                    "lawfulness",
                    "fairness",
                    "transparency",
                    "purpose_limitation",
                    "data_minimization",
                    "accuracy",
                    "storage_limitation",
                    "integrity_confidentiality",
                ],
                "individual_rights": [
                    "right_to_information",
                    "right_of_access",
                    "right_to_rectification",
                    "right_to_erasure",
                    "right_to_restrict_processing",
                    "right_to_data_portability",
                    "right_to_object",
                    "rights_related_to_automated_decision_making",
                ],
            },
            ComplianceFramework.IEEE_7000_2024: {
                "ethical_design_process": [
                    "stakeholder_identification",
                    "value_investigation",
                    "design_requirements",
                    "risk_assessment",
                    "impact_assessment",
                ]
            },
            ComplianceFramework.OECD_AI_PRINCIPLES: {
                "ai_principles": [
                    "inclusive_growth",
                    "human_centered_values",
                    "transparency_explainability",
                    "robustness_security_safety",
                    "accountability",
                ]
            },
        }

        # Ethical decision history for learning
        self.decision_history = []
        self.ethical_violations = []

        self.logger.info("⚖️ Ethical Hierarchy initialized with multi-framework compliance")

    async def evaluate_ethical_decision(
        self,
        action: dict[str, Any],
        context: dict[str, Any],
        stakeholders: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        """
        Comprehensive ethical evaluation of a proposed action.

        Args:
            action: The proposed action to evaluate
            context: Contextual information about the situation
            stakeholders: List of affected stakeholders

        Returns:
            Detailed ethical assessment with recommendations
        """

        evaluation_id = f"eval_{int(time.time())}"
        self.logger.info(f"🔍 Starting ethical evaluation {evaluation_id}")

        # Initialize evaluation result
        result = {
            "evaluation_id": evaluation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "context": context,
            "stakeholders": stakeholders or [],
            "ethical_scores": {},
            "compliance_checks": {},
            "overall_assessment": {},
            "recommendations": [],
            "violations": [],
            "approval_status": "pending",
        }

        try:
            # 1. Evaluate against each ethical principle
            for principle in EthicalPrinciple:
                score = await self._evaluate_principle(principle, action, context)
                result["ethical_scores"][principle.value] = score

            # 2. Check legal compliance
            for framework in self.legal_frameworks:
                compliance = await self._check_framework_compliance(framework, action, context)
                result["compliance_checks"][framework.value] = compliance

            # 3. Perform stakeholder impact analysis
            stakeholder_impact = await self._analyze_stakeholder_impact(action, context, stakeholders)
            result["stakeholder_impact"] = stakeholder_impact

            # 4. Calculate overall ethical assessment
            overall_assessment = await self._calculate_overall_assessment(result)
            result["overall_assessment"] = overall_assessment

            # 5. Generate recommendations
            recommendations = await self._generate_recommendations(result)
            result["recommendations"] = recommendations

            # 6. Determine approval status
            approval_status = await self._determine_approval_status(result)
            result["approval_status"] = approval_status

            # 7. Log decision for learning
            self.decision_history.append(result)

            # 8. Check for violations
            violations = self._identify_violations(result)
            if violations:
                result["violations"] = violations
                self.ethical_violations.extend(violations)
                self.logger.warning(f"⚠️ Ethical violations detected: {len(violations)}")

            self.logger.info(f"✅ Ethical evaluation {evaluation_id} completed: {approval_status}")

            return result

        except Exception as e:
            self.logger.error(f"❌ Ethical evaluation failed: {e!s}")
            result["error"] = str(e)
            result["approval_status"] = "error"
            return result

    async def _evaluate_principle(
        self,
        principle: EthicalPrinciple,
        action: dict[str, Any],
        context: dict[str, Any],
    ) -> float:
        """Evaluate action against a specific ethical principle."""

        action.get("type", "")
        action_description = action.get("description", "")

        # Default base score
        score = 0.5

        if principle == EthicalPrinciple.HUMAN_DIGNITY:
            # Evaluate respect for human dignity
            if "human" in action_description.lower():
                if any(term in action_description.lower() for term in ["respect", "dignity", "worth"]):
                    score = 0.9
                elif any(term in action_description.lower() for term in ["exploit", "degrade", "manipulate"]):
                    score = 0.1
                else:
                    score = 0.7

        elif principle == EthicalPrinciple.AUTONOMY:
            # Evaluate respect for human autonomy and choice
            if context.get("user_choice", True):
                score = 0.8
            if context.get("informed_consent", False):
                score = min(1.0, score + 0.2)
            if "override" in action_description.lower() or "force" in action_description.lower():
                score = max(0.1, score - 0.5)

        elif principle == EthicalPrinciple.NON_MALEFICENCE:
            # Do no harm evaluation
            harmful_indicators = ["harm", "damage", "hurt", "injure", "violate"]
            score = 0.2 if any(term in action_description.lower() for term in harmful_indicators) else 0.8

            # Check for risk factors
            risk_level = context.get("risk_level", "low")
            if risk_level == "high":
                score = max(0.1, score - 0.4)
            elif risk_level == "medium":
                score = max(0.3, score - 0.2)

        elif principle == EthicalPrinciple.BENEFICENCE:
            # Promote well-being and benefit
            beneficial_indicators = ["help", "benefit", "improve", "assist", "support"]
            score = 0.8 if any(term in action_description.lower() for term in beneficial_indicators) else 0.5

        elif principle == EthicalPrinciple.JUSTICE:
            # Fair treatment and justice
            if context.get("treats_equally", True):
                score = 0.8
            if context.get("discriminatory", False):
                score = 0.1

        elif principle == EthicalPrinciple.FAIRNESS:
            # Unbiased and fair decisions
            bias_indicators = context.get("bias_detected", False)
            score = 0.2 if bias_indicators else 0.8

        elif principle == EthicalPrinciple.TRANSPARENCY:
            # Explainability and openness
            if context.get("explainable", False):
                score = 0.9
            elif context.get("black_box", False):
                score = 0.3
            else:
                score = 0.6

        elif principle == EthicalPrinciple.PRIVACY_PROTECTION:
            # Data privacy and protection
            if context.get("involves_personal_data", False):
                score = 0.8 if context.get("privacy_protected", True) else 0.2
            else:
                score = 0.9  # No privacy concerns

        elif principle == EthicalPrinciple.ACCOUNTABILITY:
            # Responsibility and accountability
            score = 0.8 if context.get("accountable_party") else 0.4

        elif principle == EthicalPrinciple.ECOLOGICAL_BALANCE:
            # Environmental considerations
            environmental_impact = context.get("environmental_impact", "neutral")
            if environmental_impact == "positive":
                score = 0.9
            elif environmental_impact == "negative":
                score = 0.3
            else:
                score = 0.6

        return max(0.0, min(1.0, score))  # Ensure score is between 0 and 1

    async def _check_framework_compliance(
        self,
        framework: ComplianceFramework,
        action: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Check compliance with a specific legal framework."""

        compliance_result = {
            "framework": framework.value,
            "compliant": True,
            "violations": [],
            "requirements_met": [],
            "score": 1.0,
        }

        action_description = action.get("description", "").lower()
        requirements = self.compliance_requirements.get(framework, {})

        if framework == ComplianceFramework.EU_AI_ACT_2025:
            # Check prohibited practices
            prohibited = requirements.get("prohibited_practices", [])
            for practice in prohibited:
                if practice.replace("_", " ") in action_description:
                    compliance_result["compliant"] = False
                    compliance_result["violations"].append(
                        {
                            "type": "prohibited_practice",
                            "practice": practice,
                            "severity": "critical",
                        }
                    )

            # Check high-risk requirements if applicable
            if context.get("high_risk_ai", False):
                high_risk_reqs = requirements.get("high_risk_requirements", [])
                for req in high_risk_reqs:
                    if context.get(req, False):
                        compliance_result["requirements_met"].append(req)
                    else:
                        compliance_result["violations"].append(
                            {
                                "type": "missing_requirement",
                                "requirement": req,
                                "severity": "high",
                            }
                        )

        elif framework == ComplianceFramework.GDPR:
            # Check data processing principles
            if context.get("involves_personal_data", False):
                data_principles = requirements.get("data_principles", [])
                for principle in data_principles:
                    if not context.get(f"gdpr_{principle}", True):
                        compliance_result["violations"].append(
                            {
                                "type": "data_principle_violation",
                                "principle": principle,
                                "severity": "high",
                            }
                        )

        # Calculate compliance score
        total_checks = len(compliance_result["violations"]) + len(compliance_result["requirements_met"])
        if total_checks > 0:
            violation_weight = len(compliance_result["violations"]) * 0.5
            compliance_result["score"] = max(0.0, 1.0 - (violation_weight / total_checks))

        if compliance_result["violations"]:
            compliance_result["compliant"] = False

        return compliance_result

    async def _analyze_stakeholder_impact(
        self,
        action: dict[str, Any],
        context: dict[str, Any],
        stakeholders: Optional[list[str]],
    ) -> dict[str, Any]:
        """Analyze impact on different stakeholders."""

        if not stakeholders:
            stakeholders = ["users", "society", "developers", "organization"]

        impact_analysis = {
            "stakeholder_impacts": {},
            "overall_impact": "neutral",
            "concerns": [],
            "benefits": [],
        }

        for stakeholder in stakeholders:
            # Assess impact for each stakeholder
            impact_score = 0.5  # Neutral by default

            if stakeholder == "users":
                if context.get("user_benefit", False):
                    impact_score = 0.8
                elif context.get("user_harm_risk", False):
                    impact_score = 0.2

            elif stakeholder == "society" and "social" in action.get("description", "").lower():
                if any(term in action.get("description", "").lower() for term in ["benefit", "improve"]):
                    impact_score = 0.7
                elif any(term in action.get("description", "").lower() for term in ["harm", "disrupt"]):
                    impact_score = 0.3

            impact_analysis["stakeholder_impacts"][stakeholder] = {
                "impact_score": impact_score,
                "concerns": [],
                "benefits": [],
            }

        # Calculate overall impact
        avg_impact = sum(s["impact_score"] for s in impact_analysis["stakeholder_impacts"].values()) / len(
            impact_analysis["stakeholder_impacts"]
        )

        if avg_impact >= 0.7:
            impact_analysis["overall_impact"] = "positive"
        elif avg_impact <= 0.3:
            impact_analysis["overall_impact"] = "negative"
        else:
            impact_analysis["overall_impact"] = "neutral"

        return impact_analysis

    async def _calculate_overall_assessment(self, evaluation_result: dict[str, Any]) -> dict[str, Any]:
        """Calculate overall ethical assessment."""

        ethical_scores = evaluation_result["ethical_scores"]
        compliance_checks = evaluation_result["compliance_checks"]

        # Calculate weighted ethical score
        weighted_ethical_score = 0.0
        total_weight = 0.0

        for principle_str, score in ethical_scores.items():
            principle = EthicalPrinciple(principle_str)
            weight = self.context_weights[principle]
            weighted_ethical_score += score * weight
            total_weight += weight

        overall_ethical_score = weighted_ethical_score / total_weight if total_weight > 0 else 0.5

        # Calculate compliance score
        compliance_scores = [check["score"] for check in compliance_checks.values()]
        overall_compliance_score = sum(compliance_scores) / len(compliance_scores) if compliance_scores else 1.0

        # Combined assessment
        combined_score = (overall_ethical_score * 0.6) + (overall_compliance_score * 0.4)

        # Determine severity level
        if combined_score >= 0.8:
            severity = EthicalSeverity.SAFE
        elif combined_score >= 0.6:
            severity = EthicalSeverity.CAUTION
        elif combined_score >= 0.4:
            severity = EthicalSeverity.WARNING
        else:
            severity = EthicalSeverity.CRITICAL

        return {
            "overall_ethical_score": overall_ethical_score,
            "overall_compliance_score": overall_compliance_score,
            "combined_score": combined_score,
            "severity": severity.value,
            "confidence": min(1.0, combined_score + 0.1),  # Confidence in assessment
            "reasoning": self._generate_assessment_reasoning(evaluation_result, combined_score, severity),
        }

    def _generate_assessment_reasoning(
        self,
        evaluation_result: dict[str, Any],
        combined_score: float,
        severity: EthicalSeverity,
    ) -> str:
        """Generate human-readable reasoning for the ethical assessment."""

        reasoning_parts = []

        # Ethical principles analysis
        ethical_scores = evaluation_result["ethical_scores"]
        low_scores = [p for p, s in ethical_scores.items() if s < 0.5]
        high_scores = [p for p, s in ethical_scores.items() if s > 0.8]

        if high_scores:
            reasoning_parts.append(f"Strong alignment with {', '.join(high_scores)}")

        if low_scores:
            reasoning_parts.append(f"Concerns regarding {', '.join(low_scores)}")

        # Compliance analysis
        compliance_violations = []
        for framework, check in evaluation_result["compliance_checks"].items():
            if check["violations"]:
                compliance_violations.append(framework)

        if compliance_violations:
            reasoning_parts.append(f"Legal compliance issues with {', '.join(compliance_violations)}")
        else:
            reasoning_parts.append("Full legal compliance maintained")

        # Overall assessment
        if severity == EthicalSeverity.SAFE:
            reasoning_parts.append("Action approved with high ethical confidence")
        elif severity == EthicalSeverity.CAUTION:
            reasoning_parts.append("Action conditionally approved with monitoring")
        elif severity == EthicalSeverity.WARNING:
            reasoning_parts.append("Action requires modification before approval")
        else:
            reasoning_parts.append("Action rejected due to ethical and/or legal concerns")

        return ". ".join(reasoning_parts) + "."

    async def _generate_recommendations(self, evaluation_result: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations based on the evaluation."""

        recommendations = []
        overall_assessment = evaluation_result["overall_assessment"]
        severity = EthicalSeverity(overall_assessment["severity"])

        # Ethical principle recommendations
        ethical_scores = evaluation_result["ethical_scores"]
        for principle_str, score in ethical_scores.items():
            if score < 0.5:
                principle = EthicalPrinciple(principle_str)
                if principle == EthicalPrinciple.TRANSPARENCY:
                    recommendations.append("Implement explainable AI mechanisms to improve transparency")
                elif principle == EthicalPrinciple.PRIVACY_PROTECTION:
                    recommendations.append("Strengthen data protection and privacy safeguards")
                elif principle == EthicalPrinciple.FAIRNESS:
                    recommendations.append("Conduct bias testing and implement fairness constraints")
                elif principle == EthicalPrinciple.AUTONOMY:
                    recommendations.append("Enhance user control and informed consent mechanisms")
                elif principle == EthicalPrinciple.NON_MALEFICENCE:
                    recommendations.append("Implement additional safety controls and risk mitigation")

        # Compliance recommendations
        for framework, check in evaluation_result["compliance_checks"].items():
            if check["violations"]:
                if framework == "EU_AI_ACT_2025":
                    recommendations.append("Address EU AI Act compliance gaps before deployment")
                elif framework == "GDPR":
                    recommendations.append("Implement GDPR data protection requirements")
                elif framework == "IEEE_7000_2024":
                    recommendations.append("Follow IEEE ethical design process requirements")

        # Severity-based recommendations
        if severity == EthicalSeverity.CRITICAL:
            recommendations.append("Conduct comprehensive ethical review before proceeding")
            recommendations.append("Consider alternative approaches or complete redesign")
        elif severity == EthicalSeverity.WARNING:
            recommendations.append("Implement recommended modifications and re-evaluate")
            recommendations.append("Add monitoring and oversight mechanisms")
        elif severity == EthicalSeverity.CAUTION:
            recommendations.append("Proceed with enhanced monitoring and periodic review")

        return list(set(recommendations))  # Remove duplicates

    async def _determine_approval_status(self, evaluation_result: dict[str, Any]) -> str:
        """Determine the approval status for the action."""

        overall_assessment = evaluation_result["overall_assessment"]
        overall_assessment["combined_score"]
        severity = EthicalSeverity(overall_assessment["severity"])

        # Check for critical violations
        critical_violations = []
        for check in evaluation_result["compliance_checks"].values():
            critical_violations.extend([v for v in check.get("violations", []) if v.get("severity") == "critical"])

        if critical_violations or severity == EthicalSeverity.CRITICAL:
            return "rejected"
        elif severity == EthicalSeverity.WARNING:
            return "conditional"
        elif severity in [EthicalSeverity.CAUTION, EthicalSeverity.SAFE]:
            return "approved"
        else:
            return "under_review"

    def _identify_violations(self, evaluation_result: dict[str, Any]) -> list[dict[str, Any]]:
        """Identify specific ethical or legal violations."""

        violations = []

        # Collect compliance violations
        for framework, check in evaluation_result["compliance_checks"].items():
            for violation in check.get("violations", []):
                violations.append(
                    {
                        **violation,
                        "framework": framework,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        # Check for ethical principle violations
        ethical_scores = evaluation_result["ethical_scores"]
        for principle_str, score in ethical_scores.items():
            if score < 0.3:  # Critical ethical score
                violations.append(
                    {
                        "type": "ethical_principle_violation",
                        "principle": principle_str,
                        "score": score,
                        "severity": "high",
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

        return violations

    def adapt_weights(self, environmental_context: dict[str, Any]) -> None:
        """Dynamic weight adjustment based on real-world context."""

        # Adjust weights based on context
        if environmental_context.get("high_stakes", False):
            # Increase importance of safety and dignity in high-stakes situations
            self.context_weights[EthicalPrinciple.HUMAN_DIGNITY] = min(
                1.0, self.context_weights[EthicalPrinciple.HUMAN_DIGNITY] + 0.05
            )
            self.context_weights[EthicalPrinciple.NON_MALEFICENCE] = min(
                1.0, self.context_weights[EthicalPrinciple.NON_MALEFICENCE] + 0.05
            )

        if environmental_context.get("privacy_sensitive", False):
            # Increase privacy weight for privacy-sensitive contexts
            self.context_weights[EthicalPrinciple.PRIVACY_PROTECTION] = min(
                1.0, self.context_weights[EthicalPrinciple.PRIVACY_PROTECTION] + 0.1
            )

        if environmental_context.get("public_facing", False):
            # Increase transparency and accountability for public-facing systems
            self.context_weights[EthicalPrinciple.TRANSPARENCY] = min(
                1.0, self.context_weights[EthicalPrinciple.TRANSPARENCY] + 0.05
            )
            self.context_weights[EthicalPrinciple.ACCOUNTABILITY] = min(
                1.0, self.context_weights[EthicalPrinciple.ACCOUNTABILITY] + 0.05
            )

        self.logger.info("⚖️ Ethical weights adapted to environmental context")

    def get_priority_weights(self, context: dict[str, Any]) -> dict[str, float]:
        """Generate context-aware ethical weights with legal constraints."""

        # Start with base weights
        priority_weights = self.context_weights.copy()

        # Apply contextual adjustments
        self.adapt_weights(context)

        # Legal framework constraints
        jurisdiction = context.get("jurisdiction", "international")

        if jurisdiction == "EU":
            # EU AI Act emphasizes transparency and human oversight
            priority_weights[EthicalPrinciple.TRANSPARENCY] = min(
                1.0, priority_weights[EthicalPrinciple.TRANSPARENCY] + 0.1
            )
            priority_weights[EthicalPrinciple.PRIVACY_PROTECTION] = min(
                1.0, priority_weights[EthicalPrinciple.PRIVACY_PROTECTION] + 0.1
            )

        elif jurisdiction == "US":
            # US frameworks emphasize fairness and accountability
            priority_weights[EthicalPrinciple.FAIRNESS] = min(1.0, priority_weights[EthicalPrinciple.FAIRNESS] + 0.1)
            priority_weights[EthicalPrinciple.ACCOUNTABILITY] = min(
                1.0, priority_weights[EthicalPrinciple.ACCOUNTABILITY] + 0.1
            )

        return priority_weights

    def get_ethical_status(self) -> dict[str, Any]:
        """Get current ethical framework status and statistics."""

        total_evaluations = len(self.decision_history)
        total_violations = len(self.ethical_violations)

        recent_evaluations = self.decision_history[-10:] if self.decision_history else []
        approval_rate = (
            len([e for e in recent_evaluations if e["approval_status"] == "approved"]) / len(recent_evaluations)
            if recent_evaluations
            else 0
        )

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "framework_version": "lukhasAGI_Ethical_Hierarchy_v1.0",
            "active_frameworks": [f.value for f in self.legal_frameworks],
            "ethical_principles": list(self.context_weights.keys()),
            "statistics": {
                "total_evaluations": total_evaluations,
                "total_violations": total_violations,
                "recent_approval_rate": approval_rate,
                "violation_rate": (total_violations / total_evaluations if total_evaluations > 0 else 0),
            },
            "current_weights": {k.value: v for k, v in self.context_weights.items()},
            "recent_violations": [
                {
                    "type": v.get("type", "unknown"),
                    "severity": v.get("severity", "unknown"),
                    "timestamp": v.get("timestamp", "unknown"),
                }
                for v in self.ethical_violations[-5:]
            ],
        }
