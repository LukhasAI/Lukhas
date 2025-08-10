"""
Identity Validator - Advanced validation engine for SEEDRA
Provides comprehensive identity verification and validation
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

logger = logging.getLogger(__name__)


@dataclass
class ValidationRule:
    """Represents a validation rule"""

    name: str
    pattern: str
    required: bool = True
    message: str = ""
    confidence_weight: float = 1.0


@dataclass
class ValidationResult:
    """Result of identity validation"""

    field: str
    valid: bool
    confidence: float
    message: str
    details: Dict = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class IdentityValidator:
    """Advanced identity validation system"""

    def __init__(self):
        self.validation_rules = self._initialize_default_rules()
        self.custom_validators = {}
        self.confidence_threshold = 0.7

    def _initialize_default_rules(self) -> Dict[str, ValidationRule]:
        """Initialize default validation rules"""
        return {
            "email": ValidationRule(
                name="email",
                pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                required=True,
                message="Invalid email format",
                confidence_weight=1.0,
            ),
            "username": ValidationRule(
                name="username",
                pattern=r"^[a-zA-Z0-9_]{3,20}$",
                required=True,
                message="Username must be 3-20 characters, alphanumeric and underscore only",
                confidence_weight=0.8,
            ),
            "phone": ValidationRule(
                name="phone",
                pattern=r"^\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$",
                required=False,
                message="Invalid phone number format",
                confidence_weight=0.9,
            ),
            "government_id": ValidationRule(
                name="government_id",
                pattern=r"^[A-Z0-9]{6,12}$",
                required=False,
                message="Invalid government ID format",
                confidence_weight=1.5,
            ),
        }

    async def validate_identity_data(self, identity_data: Dict) -> Dict:
        """Validate complete identity data"""
        try:
            results = []
            total_confidence = 0.0
            total_weight = 0.0

            for field, value in identity_data.items():
                if field in self.validation_rules:
                    result = await self._validate_field(field, value)
                    results.append(result)

                    if result.valid:
                        rule = self.validation_rules[field]
                        total_confidence += result.confidence * rule.confidence_weight
                        total_weight += rule.confidence_weight

            # Calculate overall confidence
            overall_confidence = (
                total_confidence / total_weight if total_weight > 0 else 0.0
            )

            # Check for required fields
            missing_required = []
            for field_name, rule in self.validation_rules.items():
                if rule.required and field_name not in identity_data:
                    missing_required.append(field_name)

            return {
                "valid": overall_confidence >= self.confidence_threshold
                and not missing_required,
                "confidence": overall_confidence,
                "field_results": results,
                "missing_required": missing_required,
                "overall_score": overall_confidence * 100,
            }

        except Exception as e:
            logger.error(f"Identity validation failed: {e}")
            return {"valid": False, "confidence": 0.0, "error": str(e)}

    async def _validate_field(self, field: str, value: str) -> ValidationResult:
        """Validate a specific field"""
        try:
            rule = self.validation_rules[field]

            # Basic pattern matching
            pattern_match = bool(re.match(rule.pattern, str(value)))

            # Calculate confidence based on various factors
            confidence = 0.0
            details = {}

            if pattern_match:
                confidence += 0.7

                # Additional validation based on field type
                if field == "email":
                    confidence += await self._validate_email_advanced(value, details)
                elif field == "phone":
                    confidence += await self._validate_phone_advanced(value, details)
                elif field == "username":
                    confidence += await self._validate_username_advanced(value, details)
                elif field == "government_id":
                    confidence += await self._validate_government_id_advanced(
                        value, details
                    )

            # Apply custom validators if available
            if field in self.custom_validators:
                custom_result = await self.custom_validators[field](value)
                confidence = max(confidence, custom_result.get("confidence", 0.0))
                details.update(custom_result.get("details", {}))

            return ValidationResult(
                field=field,
                valid=pattern_match and confidence >= 0.5,
                confidence=min(1.0, confidence),
                message=rule.message if not pattern_match else "Valid",
                details=details,
            )

        except Exception as e:
            logger.error(f"Field validation failed for {field}: {e}")
            return ValidationResult(
                field=field,
                valid=False,
                confidence=0.0,
                message=f"Validation error: {str(e)}",
            )

    async def _validate_email_advanced(self, email: str, details: Dict) -> float:
        """Advanced email validation"""
        confidence_boost = 0.0

        # Check for common email providers
        domain = email.split("@")[1].lower()
        trusted_domains = {
            "gmail.com",
            "yahoo.com",
            "outlook.com",
            "hotmail.com",
            "icloud.com",
            "protonmail.com",
            "aol.com",
        }

        if domain in trusted_domains:
            confidence_boost += 0.2
            details["trusted_domain"] = True

        # Check for suspicious patterns
        if "+" in email.split("@")[0]:
            details["has_alias"] = True

        # Check for temporary email patterns
        temp_indicators = ["temp", "throwaway", "10minute", "guerrilla"]
        if any(indicator in domain for indicator in temp_indicators):
            confidence_boost -= 0.3
            details["potential_temporary"] = True

        return confidence_boost

    async def _validate_phone_advanced(self, phone: str, details: Dict) -> float:
        """Advanced phone validation"""
        confidence_boost = 0.0

        # Clean phone number
        cleaned = re.sub(r"[^\d]", "", phone)

        # Check length
        if len(cleaned) == 10 or len(cleaned) == 11:
            confidence_boost += 0.2
            details["proper_length"] = True

        # Check for valid area codes (US)
        if len(cleaned) >= 3:
            area_code = cleaned[-10:-7] if len(cleaned) == 11 else cleaned[:3]
            invalid_area_codes = ["000", "911", "555"]
            if area_code not in invalid_area_codes:
                confidence_boost += 0.1
                details["valid_area_code"] = True

        return confidence_boost

    async def _validate_username_advanced(self, username: str, details: Dict) -> float:
        """Advanced username validation"""
        confidence_boost = 0.0

        # Check for good practices
        if not username.isdigit():  # Not all numbers
            confidence_boost += 0.1

        if len(username) >= 5:  # Reasonable length
            confidence_boost += 0.1

        # Check for suspicious patterns
        profanity_indicators = ["admin", "test", "user", "guest", "anonymous"]
        if any(indicator in username.lower() for indicator in profanity_indicators):
            confidence_boost -= 0.2
            details["suspicious_pattern"] = True

        # Check for good entropy
        unique_chars = len(set(username.lower()))
        if unique_chars >= len(username) * 0.7:
            confidence_boost += 0.1
            details["good_entropy"] = True

        return confidence_boost

    async def _validate_government_id_advanced(
        self, gov_id: str, details: Dict
    ) -> float:
        """Advanced government ID validation"""
        confidence_boost = 0.0

        # Basic format checks
        if len(gov_id) >= 8:
            confidence_boost += 0.2

        # Check for mix of letters and numbers
        has_letters = any(c.isalpha() for c in gov_id)
        has_numbers = any(c.isdigit() for c in gov_id)

        if has_letters and has_numbers:
            confidence_boost += 0.1
            details["mixed_format"] = True

        return confidence_boost

    async def add_custom_validator(self, field: str, validator_func):
        """Add custom validation function for a field"""
        self.custom_validators[field] = validator_func
        logger.info(f"Added custom validator for field: {field}")

    async def add_validation_rule(self, rule: ValidationRule):
        """Add new validation rule"""
        self.validation_rules[rule.name] = rule
        logger.info(f"Added validation rule: {rule.name}")

    async def cross_reference_validation(
        self, identity_data: Dict, external_sources: List[str] = None
    ) -> Dict:
        """Cross-reference identity data with external sources"""
        try:
            if external_sources is None:
                external_sources = []

            cross_ref_results = {}

            # Simulate cross-referencing with various sources
            for source in external_sources:
                if source == "social_media":
                    result = await self._cross_ref_social_media(identity_data)
                elif source == "public_records":
                    result = await self._cross_ref_public_records(identity_data)
                elif source == "credit_bureau":
                    result = await self._cross_ref_credit_bureau(identity_data)
                else:
                    result = {
                        "available": False,
                        "message": f"Unknown source: {source}",
                    }

                cross_ref_results[source] = result

            # Calculate cross-reference confidence
            total_confidence = 0.0
            available_sources = 0

            for source, result in cross_ref_results.items():
                if result.get("available", False):
                    total_confidence += result.get("confidence", 0.0)
                    available_sources += 1

            cross_ref_confidence = (
                total_confidence / available_sources if available_sources > 0 else 0.0
            )

            return {
                "cross_reference_confidence": cross_ref_confidence,
                "sources_checked": len(external_sources),
                "sources_available": available_sources,
                "results": cross_ref_results,
            }

        except Exception as e:
            logger.error(f"Cross-reference validation failed: {e}")
            return {"error": str(e)}

    async def _cross_ref_social_media(self, identity_data: Dict) -> Dict:
        """Simulate social media cross-reference"""
        # In production, this would integrate with social media APIs
        return {
            "available": True,
            "confidence": 0.6,
            "matches": 2,
            "details": "Found matching profiles on 2 platforms",
        }

    async def _cross_ref_public_records(self, identity_data: Dict) -> Dict:
        """Simulate public records cross-reference"""
        # In production, this would check government databases
        return {
            "available": True,
            "confidence": 0.8,
            "verified_fields": ["name", "address"],
            "details": "Verified in public records database",
        }

    async def _cross_ref_credit_bureau(self, identity_data: Dict) -> Dict:
        """Simulate credit bureau cross-reference"""
        # In production, this would integrate with credit reporting agencies
        return {
            "available": False,
            "reason": "Credit check not requested",
            "details": "Would require explicit consent",
        }

    async def get_validation_report(self, user_id: str, identity_data: Dict) -> Dict:
        """Generate comprehensive validation report"""
        try:
            # Basic validation
            basic_validation = await self.validate_identity_data(identity_data)

            # Cross-reference validation (if enabled)
            cross_ref = await self.cross_reference_validation(
                identity_data, ["social_media", "public_records"]
            )

            # Generate overall score
            basic_score = basic_validation.get("confidence", 0.0)
            cross_ref_score = cross_ref.get("cross_reference_confidence", 0.0)

            # Weighted average (basic validation weighted more heavily)
            overall_score = (basic_score * 0.7) + (cross_ref_score * 0.3)

            return {
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "overall_confidence": overall_score,
                "risk_level": self._calculate_risk_level(overall_score),
                "basic_validation": basic_validation,
                "cross_reference": cross_ref,
                "recommendations": self._generate_recommendations(
                    basic_validation, cross_ref
                ),
            }

        except Exception as e:
            logger.error(f"Failed to generate validation report: {e}")
            return {"error": str(e)}

    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level based on confidence score"""
        if confidence >= 0.9:
            return "low"
        elif confidence >= 0.7:
            return "medium"
        elif confidence >= 0.5:
            return "high"
        else:
            return "very_high"

    def _generate_recommendations(
        self, basic_validation: Dict, cross_ref: Dict
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        confidence = basic_validation.get("confidence", 0.0)

        if confidence < 0.7:
            recommendations.append(
                "Consider requesting additional verification documents"
            )

        if basic_validation.get("missing_required"):
            recommendations.append("Complete all required fields")

        if cross_ref.get("sources_available", 0) == 0:
            recommendations.append(
                "Enable cross-reference validation for higher confidence"
            )

        if confidence < 0.5:
            recommendations.append("Manual review recommended")

        return recommendations
