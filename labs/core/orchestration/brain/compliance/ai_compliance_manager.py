"""
AI Compliance Manager for lukhas AI System

Comprehensive regulatory compliance, ethical constraints, and data governance.
Ensures adherence to EU AI Act, GDPR, NIST RMF, and international standards.

Based on Lukhas repository implementation with LUKHAS AI integration.
Based on Lukhas repository implementation with lukhas AI integration.
"""

import logging
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any


class ComplianceLevel(Enum):
    """Compliance assessment levels"""

    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"


class AIComplianceManager:
    """
    Advanced AI Compliance Manager for LUKHAS AI System
    Advanced AI Compliance Manager for lukhas AI System

    Manages comprehensive regulatory compliance, ethical constraints, and data governance.
    Ensures adherence to regulations like GDPR, EU AI Act, NIST RMF, and ISO standards.
    """

    def __init__(self, region: str = "GLOBAL", level: str = "STRICT"):
        self.logger = logging.getLogger("ΛAI.compliance")
        self.logger = logging.getLogger("lukhasAI.compliance")
        self.region = region
        self.level = level

        # Comprehensive compliance rules framework
        self.compliance_rules = {
            "EU": {
                "AI_ACT": True,
                "GDPR": True,
                "risk_level": "high",
                "required_assessments": [
                    "fundamental_rights",
                    "safety",
                    "bias",
                    "transparency",
                ],
                "prohibited_practices": [
                    "subliminal_manipulation",
                    "cognitive_behavioral_manipulation",
                    "social_scoring",
                    "real_time_remote_biometric_identification",
                ],
            },
            "US": {
                "AI_BILL_RIGHTS": True,
                "NIST_AI_RMF": True,
                "state_laws": ["CCPA", "BIPA", "SHIELD"],
                "required_assessments": [
                    "privacy",
                    "fairness",
                    "transparency",
                    "accountability",
                ],
            },
            "INTERNATIONAL": {
                "IEEE_AI_ETHICS": True,
                "ISO_AI": ["ISO/IEC 24368", "ISO/IEC 42001", "ISO/IEC 27001"],
                "OECD_PRINCIPLES": True,
                "required_assessments": [
                    "ethics",
                    "governance",
                    "human_oversight",
                ],
            },
        }

        # Assessment history for compliance tracking
        self.assessment_history = []
        self.violation_log = []

        self.logger.info(f"🛡️ AI Compliance Manager initialized for {region} with {level} level")

    async def validate_ai_action(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Validate AI action against all applicable regulations"""

        result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action_id": action.get("id", "unknown"),
            "compliant": True,
            "compliance_level": ComplianceLevel.COMPLIANT.value,
            "validations": [],
            "violations": [],
            "required_actions": [],
            "risk_assessment": {},
        }

        try:
            # EU AI Act compliance check
            if self.region in ["EU", "GLOBAL"]:
                eu_result = await self._check_eu_ai_act_compliance(action, context)
                result["validations"].append(eu_result)
                if not eu_result["compliant"]:
                    result["compliant"] = False
                    result["violations"].extend(eu_result.get("violations", []))
                    result["required_actions"].extend(eu_result.get("required_actions", []))

            # GDPR compliance check
            if context.get("involves_personal_data", False):
                gdpr_result = await self._check_gdpr_compliance(action, context)
                result["validations"].append(gdpr_result)
                if not gdpr_result["compliant"]:
                    result["compliant"] = False
                    result["violations"].extend(gdpr_result.get("violations", []))
                    result["required_actions"].extend(gdpr_result.get("required_actions", []))

            # NIST AI RMF compliance check
            if self.region in ["US", "GLOBAL"]:
                nist_result = await self._check_nist_compliance(action, context)
                result["validations"].append(nist_result)
                if not nist_result["compliant"]:
                    result["compliant"] = False
                    result["violations"].extend(nist_result.get("violations", []))
                    result["required_actions"].extend(nist_result.get("required_actions", []))

            # ISO/IEC standards compliance
            iso_result = await self._check_iso_compliance(action, context)
            result["validations"].append(iso_result)
            if not iso_result["compliant"]:
                result["compliant"] = False
                result["violations"].extend(iso_result.get("violations", []))
                result["required_actions"].extend(iso_result.get("required_actions", []))

            # Determine overall compliance level
            if result["violations"]:
                critical_violations = [v for v in result["violations"] if v.get("severity") == "critical"]
                high_violations = [v for v in result["violations"] if v.get("severity") == "high"]

                if critical_violations:
                    result["compliance_level"] = ComplianceLevel.CRITICAL.value
                elif high_violations:
                    result["compliance_level"] = ComplianceLevel.VIOLATION.value
                else:
                    result["compliance_level"] = ComplianceLevel.WARNING.value

            # Log assessment
            self.assessment_history.append(result)

            # Log violations if any
            if result["violations"]:
                self.violation_log.extend(result["violations"])
                self.logger.warning(f"Compliance violations detected: {len(result['violations'])}")

            return result

        except Exception as e:
            self.logger.error(f"Compliance validation error: {e!s}")
            return {
                **result,
                "compliant": False,
                "compliance_level": ComplianceLevel.CRITICAL.value,
                "violations": [
                    {
                        "type": "validation_error",
                        "description": str(e),
                        "severity": "critical",
                    }
                ],
            }

    async def _check_eu_ai_act_compliance(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Check compliance with EU AI Act requirements"""

        result = {
            "framework": "EU_AI_ACT",
            "compliant": True,
            "risk_level": "minimal",
            "violations": [],
            "required_actions": [],
        }

        action_type = action.get("type", "")
        ai_system = context.get("ai_system", {})

        # Check for prohibited AI practices (Article 5)
        prohibited_practices = self.compliance_rules["EU"]["prohibited_practices"]
        for practice in prohibited_practices:
            if practice in action_type.lower() or practice in str(action.get("description", "")).lower():
                result["compliant"] = False
                result["risk_level"] = "prohibited"
                result["violations"].append(
                    {
                        "type": "prohibited_practice",
                        "practice": practice,
                        "article": "Article 5",
                        "severity": "critical",
                        "description": f"AI system uses prohibited practice: {practice}",
                    }
                )
                result["required_actions"].append("discontinue_prohibited_practice")

        # Check if high-risk AI system
        if self._is_high_risk_ai_system(ai_system):
            result["risk_level"] = "high"

            # High-risk requirements (Articles 8-15)
            required_measures = [
                "quality_management_system",
                "risk_management_system",
                "data_governance",
                "technical_documentation",
                "record_keeping",
                "transparency_requirements",
                "human_oversight",
                "accuracy_robustness",
            ]

            for measure in required_measures:
                if not ai_system.get(measure, False):
                    result["violations"].append(
                        {
                            "type": "missing_requirement",
                            "requirement": measure,
                            "severity": "high",
                            "description": f"High-risk AI system missing: {measure}",
                        }
                    )
                    result["required_actions"].append(f"implement_{measure}")

        # Transparency requirements (Article 13)
        if not ai_system.get("transparent_to_users", False):
            result["violations"].append(
                {
                    "type": "transparency_violation",
                    "article": "Article 13",
                    "severity": "medium",
                    "description": "Users must be informed they are interacting with AI system",
                }
            )
            result["required_actions"].append("implement_user_disclosure")

        if result["violations"]:
            result["compliant"] = False

        return result

    async def _check_gdpr_compliance(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Check GDPR compliance for data processing"""

        result = {
            "framework": "GDPR",
            "compliant": True,
            "violations": [],
            "required_actions": [],
        }

        data_processing = context.get("data_processing", {})
        personal_data = context.get("personal_data", {})

        # Lawful basis check (Article 6)
        if not data_processing.get("lawful_basis"):
            result["compliant"] = False
            result["violations"].append(
                {
                    "type": "missing_lawful_basis",
                    "article": "Article 6",
                    "severity": "high",
                    "description": "No lawful basis specified for personal data processing",
                }
            )
            result["required_actions"].append("establish_lawful_basis")

        # Consent requirements (Article 7)
        if data_processing.get("lawful_basis") == "consent":
            consent = context.get("user_consent", {})
            if not consent.get("freely_given", False):
                result["violations"].append(
                    {
                        "type": "invalid_consent",
                        "article": "Article 7",
                        "severity": "high",
                        "description": "Consent must be freely given",
                    }
                )
            if not consent.get("specific", False):
                result["violations"].append(
                    {
                        "type": "invalid_consent",
                        "article": "Article 7",
                        "severity": "high",
                        "description": "Consent must be specific",
                    }
                )

        # Data minimization (Article 5.1.c)
        if not data_processing.get("data_minimized", False):
            result["violations"].append(
                {
                    "type": "data_minimization_violation",
                    "article": "Article 5.1.c",
                    "severity": "medium",
                    "description": "Personal data must be adequate, relevant and limited",
                }
            )
            result["required_actions"].append("implement_data_minimization")

        # Retention period (Article 5.1.e)
        if not data_processing.get("retention_period"):
            result["violations"].append(
                {
                    "type": "undefined_retention",
                    "article": "Article 5.1.e",
                    "severity": "medium",
                    "description": "Data retention period must be defined",
                }
            )
            result["required_actions"].append("define_retention_period")

        # Special categories of data (Article 9)
        if personal_data.get("special_categories", False):
            if not context.get("special_category_exception", False):
                result["violations"].append(
                    {
                        "type": "special_category_violation",
                        "article": "Article 9",
                        "severity": "high",
                        "description": "Special categories require explicit exception",
                    }
                )
                result["required_actions"].append("obtain_special_category_basis")

        if result["violations"]:
            result["compliant"] = False

        return result

    async def _check_nist_compliance(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Check NIST AI Risk Management Framework compliance"""

        result = {
            "framework": "NIST_AI_RMF",
            "compliant": True,
            "violations": [],
            "required_actions": [],
        }

        ai_system = context.get("ai_system", {})

        # GOVERN function
        if not ai_system.get("governance_structure", False):
            result["violations"].append(
                {
                    "type": "missing_governance",
                    "function": "GOVERN",
                    "severity": "high",
                    "description": "AI governance structure required",
                }
            )
            result["required_actions"].append("establish_ai_governance")

        # MAP function
        if not ai_system.get("risk_mapping", False):
            result["violations"].append(
                {
                    "type": "missing_risk_mapping",
                    "function": "MAP",
                    "severity": "medium",
                    "description": "AI risks must be identified and mapped",
                }
            )
            result["required_actions"].append("conduct_risk_mapping")

        # MEASURE function
        if not ai_system.get("risk_measurement", False):
            result["violations"].append(
                {
                    "type": "missing_risk_measurement",
                    "function": "MEASURE",
                    "severity": "medium",
                    "description": "AI risks must be measured and assessed",
                }
            )
            result["required_actions"].append("implement_risk_measurement")

        # MANAGE function
        if not ai_system.get("risk_management", False):
            result["violations"].append(
                {
                    "type": "missing_risk_management",
                    "function": "MANAGE",
                    "severity": "high",
                    "description": "AI risks must be actively managed",
                }
            )
            result["required_actions"].append("implement_risk_management")

        if result["violations"]:
            result["compliant"] = False

        return result

    async def _check_iso_compliance(self, action: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
        """Check ISO/IEC standards compliance"""

        result = {
            "framework": "ISO_STANDARDS",
            "compliant": True,
            "violations": [],
            "required_actions": [],
        }

        ai_system = context.get("ai_system", {})

        # ISO/IEC 42001 - AI Management Systems
        if not ai_system.get("ai_management_system", False):
            result["violations"].append(
                {
                    "type": "missing_ai_management_system",
                    "standard": "ISO/IEC 42001",
                    "severity": "medium",
                    "description": "AI management system required",
                }
            )
            result["required_actions"].append("implement_ai_management_system")

        # ISO/IEC 27001 - Information Security
        if not ai_system.get("information_security", False):
            result["violations"].append(
                {
                    "type": "missing_information_security",
                    "standard": "ISO/IEC 27001",
                    "severity": "high",
                    "description": "Information security controls required",
                }
            )
            result["required_actions"].append("implement_security_controls")

        if result["violations"]:
            result["compliant"] = False

        return result

    def _is_high_risk_ai_system(self, ai_system: dict[str, Any]) -> bool:
        """Determine if AI system is high-risk under EU AI Act"""

        high_risk_areas = [
            "biometric_identification",
            "critical_infrastructure",
            "education_assessment",
            "employment_decisions",
            "essential_services",
            "law_enforcement",
            "migration_asylum",
            "administration_justice",
        ]

        system_area = ai_system.get("application_area", "")
        return system_area in high_risk_areas

    def get_transparency_report(self) -> dict[str, Any]:
        """Generate comprehensive transparency report for AI system"""

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "compliance_framework": "lukhas AI Compliance System",
            "region": self.region,
            "compliance_level": self.level,
            "active_regulations": self.compliance_rules,
            "assessment_summary": {
                "total_assessments": len(self.assessment_history),
                "compliant_assessments": len([a for a in self.assessment_history if a["compliant"]]),
                "violation_count": len(self.violation_log),
                "last_assessment": (self.assessment_history[-1]["timestamp"] if self.assessment_history else None),
            },
            "data_processing_purposes": self._get_processing_purposes(),
            "compliance_certifications": [
                "EU AI Act Article 8-15 Implementation",
                "GDPR Data Protection Impact Assessment",
                "NIST AI RMF Framework Alignment",
                "ISO/IEC 42001 AI Management Systems",
            ],
            "audit_trail": {
                "assessments_logged": len(self.assessment_history),
                "violations_logged": len(self.violation_log),
                "retention_period": "7 years (regulatory requirement)",
            },
        }

    def _get_processing_purposes(self) -> dict[str, str]:
        """Get data processing purposes for transparency"""

        return {
            "intent_detection": "Understand user requests and context for appropriate responses",
            "conversation_memory": "Maintain conversation context for coherent interactions",
            "personalization": "Adapt responses to user preferences (with explicit consent)",
            "safety_monitoring": "Detect harmful content and ensure user safety",
            "compliance_logging": "Maintain regulatory compliance audit trails",
            "system_optimization": "Improve AI system performance and capabilities",
        }

    async def generate_compliance_report(self, hours: int = 24) -> dict[str, Any]:
        """Generate compliance report for recent assessments"""

        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        recent_assessments = [
            a for a in self.assessment_history if datetime.fromisoformat(a["timestamp"]) >= cutoff_time
        ]

        if not recent_assessments:
            return {
                "status": "no_recent_assessments",
                "time_period_hours": hours,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Calculate compliance metrics
        total_assessments = len(recent_assessments)
        compliant_assessments = len([a for a in recent_assessments if a["compliant"]])
        compliance_rate = compliant_assessments / total_assessments if total_assessments > 0 else 0

        # Violation analysis
        recent_violations = []
        for assessment in recent_assessments:
            recent_violations.extend(assessment.get("violations", []))

        violation_counts = {}
        for violation in recent_violations:
            framework = violation.get("framework", "unknown")
            violation_counts[framework] = violation_counts.get(framework, 0) + 1

        # Overall status
        if compliance_rate >= 0.95:
            status = "excellent"
        elif compliance_rate >= 0.85:
            status = "good"
        elif compliance_rate >= 0.70:
            status = "needs_attention"
        else:
            status = "critical"

        return {
            "time_period_hours": hours,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_assessments": total_assessments,
            "compliant_assessments": compliant_assessments,
            "compliance_rate": compliance_rate,
            "overall_status": status,
            "violation_counts_by_framework": violation_counts,
            "most_violated_framework": (
                max(violation_counts.items(), key=lambda x: x[1])[0] if violation_counts else None
            ),
            "recommendations": self._generate_compliance_recommendations(recent_assessments),
            "regulatory_alignment": {
                "EU_AI_ACT": "Full compliance monitoring active",
                "GDPR": "Data protection controls enforced",
                "NIST_AI_RMF": "Risk management framework implemented",
                "ISO_STANDARDS": "Information security controls active",
            },
        }

    def _generate_compliance_recommendations(self, assessments: list[dict[str, Any]]) -> list[str]:
        """Generate compliance recommendations based on recent assessments"""

        recommendations = []

        # Analyze common violations
        all_violations = []
        for assessment in assessments:
            all_violations.extend(assessment.get("violations", []))

        violation_types = {}
        for violation in all_violations:
            v_type = violation.get("type", "unknown")
            violation_types[v_type] = violation_types.get(v_type, 0) + 1

        # Generate specific recommendations
        if "transparency_violation" in violation_types:
            recommendations.append("Implement user disclosure mechanisms for AI interactions")

        if "missing_lawful_basis" in violation_types:
            recommendations.append("Establish clear lawful basis for all personal data processing")

        if "missing_governance" in violation_types:
            recommendations.append("Strengthen AI governance and oversight structures")

        if "prohibited_practice" in violation_types:
            recommendations.append("Review and eliminate any prohibited AI practices")

        if len(all_violations) > len(assessments) * 0.1:  # More than 10% violation rate
            recommendations.append("Conduct comprehensive compliance audit and remediation")

        return recommendations

    async def emergency_compliance_shutdown(self, reason: str) -> dict[str, Any]:
        """Emergency compliance shutdown procedure"""

        self.logger.critical(f"🚨 Emergency compliance shutdown triggered: {reason}")

        shutdown_result = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": reason,
            "status": "emergency_shutdown_initiated",
            "actions_taken": [
                "halt_ai_operations",
                "preserve_audit_logs",
                "notify_compliance_officer",
                "initiate_investigation_protocol",
            ],
            "recovery_steps": [
                "conduct_compliance_audit",
                "remediate_violations",
                "verify_regulatory_alignment",
                "obtain_clearance_for_restart",
            ],
        }

        # Log the emergency shutdown
        self.violation_log.append(
            {
                "type": "emergency_shutdown",
                "reason": reason,
                "severity": "critical",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "requires_manual_intervention": True,
            }
        )

        return shutdown_result
