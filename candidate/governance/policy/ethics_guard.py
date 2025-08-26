"""

#TAG:governance
#TAG:policy
#TAG:neuroplastic
#TAG:colony


Lukhas Ethics Guard - Legal Compliance Assistant
Provides ethical compliance checking and safety monitoring for AI systems.
"""

import datetime
from typing import Any, Optional


class LegalComplianceAssistant:
    """
    Legal compliance assistant for ethical AI operations.

    This class provides safety checks, content filtering, and compliance
    monitoring for AI-generated content and interactions.
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        """
        Initialize the legal compliance assistant.

        Args:
            config: Configuration dictionary for compliance settings
        """
        self.config = config or {}
        self.compliance_rules = self._load_default_rules()
        self.violation_history = []
        self.safety_threshold = self.config.get("safety_threshold", 0.8)
        self.enabled = self.config.get("enabled", True)

    def _load_default_rules(self) -> dict[str, Any]:
        """Load default compliance rules."""
        return {
            "content_safety": {
                "blocked_keywords": ["harmful", "dangerous", "illegal"],
                "sensitive_topics": ["violence", "hate", "discrimination"],
                "max_sentiment_negativity": -0.7,
            },
            "privacy": {
                "no_personal_data": True,
                "data_retention_days": 30,
                "anonymization_required": True,
            },
            "ethical_guidelines": {
                "transparency": True,
                "fairness": True,
                "accountability": True,
                "human_oversight": True,
            },
        }

    def check_content_safety(self, content: str) -> dict[str, Any]:
        """
        Check content for safety violations.

        Args:
            content: Text content to check

        Returns:
            Dictionary with safety assessment results
        """
        if not self.enabled:
            return {"safe": True, "reason": "compliance_disabled"}

        violations = []
        safety_score = 1.0

        # Check for blocked keywords
        content_lower = content.lower()
        for keyword in self.compliance_rules["content_safety"]["blocked_keywords"]:
            if keyword in content_lower:
                violations.append(f"Blocked keyword detected: {keyword}")
                safety_score -= 0.2

        # Check for sensitive topics
        for topic in self.compliance_rules["content_safety"]["sensitive_topics"]:
            if topic in content_lower:
                violations.append(f"Sensitive topic detected: {topic}")
                safety_score -= 0.1

        # Overall safety assessment
        is_safe = safety_score >= self.safety_threshold

        result = {
            "safe": is_safe,
            "safety_score": max(0, safety_score),
            "violations": violations,
            "content_length": len(content),
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # Log violation if content is not safe
        if not is_safe:
            self.violation_history.append(
                {
                    "content_hash": hash(content),
                    "violations": violations,
                    "safety_score": safety_score,
                    "timestamp": result["timestamp"],
                }
            )

        return result

    def check_privacy_compliance(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Check data for privacy compliance.

        Args:
            data: Data dictionary to check for privacy issues

        Returns:
            Dictionary with privacy compliance assessment
        """
        if not self.enabled:
            return {"compliant": True, "reason": "compliance_disabled"}

        privacy_issues = []

        # Check for personal data
        if self.compliance_rules["privacy"]["no_personal_data"]:
            personal_data_indicators = ["email", "phone", "address", "ssn", "name"]
            for key, _value in data.items():
                if any(
                    indicator in key.lower() for indicator in personal_data_indicators
                ):
                    privacy_issues.append(f"Potential personal data in field: {key}")

        # Check data retention requirements
        if "timestamp" in data:
            try:
                data_timestamp = datetime.datetime.fromisoformat(data["timestamp"])
                age_days = (datetime.datetime.now() - data_timestamp).days
                max_retention = self.compliance_rules["privacy"]["data_retention_days"]

                if age_days > max_retention:
                    privacy_issues.append(
                        f"Data older than retention limit: {age_days} days"
                    )
            except (ValueError, TypeError):
                privacy_issues.append("Invalid timestamp format for retention check")

        return {
            "compliant": len(privacy_issues) == 0,
            "issues": privacy_issues,
            "anonymization_required": self.compliance_rules["privacy"][
                "anonymization_required"
            ],
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def ethical_review(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Perform ethical review of an AI operation or decision.

        Args:
            context: Context information about the operation

        Returns:
            Dictionary with ethical assessment results
        """
        if not self.enabled:
            return {"approved": True, "reason": "compliance_disabled"}

        ethical_concerns = []
        guidelines = self.compliance_rules["ethical_guidelines"]

        # Transparency check
        if guidelines["transparency"] and not context.get("operation_disclosed", False):
            ethical_concerns.append("Operation not disclosed to user")

        # Fairness check
        if guidelines["fairness"] and context.get("bias_detected", False):
            ethical_concerns.append("Potential bias detected in operation")

        # Human oversight check
        if guidelines["human_oversight"]:
            if context.get("human_approval_required", False) and not context.get(
                "human_approved", False
            ):
                ethical_concerns.append("Human oversight required but not obtained")

        return {
            "approved": len(ethical_concerns) == 0,
            "concerns": ethical_concerns,
            "guidelines_applied": guidelines,
            "recommendation": self._generate_recommendation(ethical_concerns),
            "timestamp": datetime.datetime.now().isoformat(),
        }

    def comprehensive_compliance_check(
        self, content: str, data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Perform comprehensive compliance check covering all aspects.

        Args:
            content: Content to check
            data: Data to check
            context: Context for ethical review

        Returns:
            Dictionary with comprehensive compliance results
        """
        safety_check = self.check_content_safety(content)
        privacy_check = self.check_privacy_compliance(data)
        ethical_check = self.ethical_review(context)

        overall_compliant = (
            safety_check["safe"]
            and privacy_check["compliant"]
            and ethical_check["approved"]
        )

        return {
            "overall_compliant": overall_compliant,
            "safety_assessment": safety_check,
            "privacy_assessment": privacy_check,
            "ethical_assessment": ethical_check,
            "timestamp": datetime.datetime.now().isoformat(),
            "compliance_version": "1.0",
        }

    def get_compliance_report(self) -> dict[str, Any]:
        """
        Generate compliance report with historical data.

        Returns:
            Dictionary with compliance report
        """
        total_violations = len(self.violation_history)

        if total_violations > 0:
            recent_violations = [
                v
                for v in self.violation_history
                if (
                    datetime.datetime.now()
                    - datetime.datetime.fromisoformat(v["timestamp"])
                ).days
                <= 7
            ]

            violation_types = {}
            for violation in self.violation_history:
                for v in violation["violations"]:
                    violation_types[v] = violation_types.get(v, 0) + 1
        else:
            recent_violations = []
            violation_types = {}

        return {
            "total_violations": total_violations,
            "recent_violations": len(recent_violations),
            "violation_types": violation_types,
            "safety_threshold": self.safety_threshold,
            "enabled": self.enabled,
            "rules_version": "1.0",
            "report_timestamp": datetime.datetime.now().isoformat(),
        }

    def update_rules(self, new_rules: dict[str, Any]) -> None:
        """
        Update compliance rules.

        Args:
            new_rules: New rules to apply
        """
        self.compliance_rules.update(new_rules)

    def _generate_recommendation(self, concerns: list[str]) -> str:
        """
        Generate recommendation based on ethical concerns.

        Args:
            concerns: List of ethical concerns

        Returns:
            Recommendation string
        """
        if not concerns:
            return "Operation approved - no ethical concerns identified"

        if len(concerns) == 1:
            return f"Address concern: {concerns[0]}"

        return f"Address {len(concerns)} concerns before proceeding"

    def anonymize_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Anonymize data by removing or masking personal information.

        Args:
            data: Data to anonymize

        Returns:
            Anonymized data
        """
        if not self.enabled:
            return data

        anonymized = data.copy()

        # Simple anonymization - in practice this would be more sophisticated
        personal_fields = ["name", "email", "phone", "address", "ssn"]

        for field in personal_fields:
            if field in anonymized:
                anonymized[field] = "[REDACTED]"

        # Add anonymization marker
        anonymized["_anonymized"] = True
        anonymized["_anonymization_timestamp"] = datetime.datetime.now().isoformat()

        return anonymized
