"""

#TAG:bridge
#TAG:protocols
#TAG:neuroplastic
#TAG:colony

LUKHAS ΛiD Public Previewer - Interactive Web Interface

A comprehensive web-based tool for previewing, validating, and analyzing ΛiDs
in real-time. Features live entropy feedback, format validation, tier analysis,
and educational content about the ΛiD system.

Features:
- Real-time ΛiD validation and analysis
- Live entropy scoring with optimization suggestions
- Interactive tier explorer
- Format specification browser
- Commercial ΛiD preview (with mock data)
- Educational tutorials and documentation
- Accessibility-compliant interface
- Mobile-responsive design

Author: LUKHAS AI Systems
Version: 2.0.0
Last Updated: July 5, 2025
"""

from dataclasses import dataclass
from typing import Any, Optional

from ..id_service.entropy_engine import EntropyEngine
from ..id_service.lambd_id_validator import LambdaIDValidator

# Import core modules
from ..lambd_id_service import LambdaIDService


@dataclass
class PreviewResult:
    """Result object for ΛiD preview operations."""

    lambda_id: str
    is_valid: bool
    format_type: str  # "standard", "commercial", "invalid"
    tier: Optional[int]
    entropy_score: Optional[float]
    entropy_level: Optional[str]
    validation_details: dict[str, Any]
    analysis: dict[str, Any]
    suggestions: list[str]
    warnings: list[str]
    errors: list[str]
    educational_content: Optional[dict[str, Any]]


class PublicLambdaIDPreviewer:
    """
    Public web interface for ΛiD preview and validation.

    Provides real-time analysis and educational content without requiring
    authentication or user accounts. Safe for public use with rate limiting
    and input sanitization.
    """

    def __init__(self):
        """Initialize the public previewer."""
        self.validator = LambdaIDValidator()
        self.entropy_engine = EntropyEngine()
        self.service = LambdaIDService()

        # Safe demo data (no real user information)
        self.demo_lambda_ids = {
            "tier_0": "Λ0-A1B2-○-C3D4",
            "tier_1": "Λ1-E5F6-◊-G7H8",
            "tier_2": "Λ2-I9J0-🔮-K1L2",
            "tier_3": "Λ3-M3N4-⟐-O5P6",
            "tier_4": "Λ4-Q7R8-◈-S9T0",
            "tier_5": "Λ5-U1V2-✨-W3X4",
        }

        self.commercial_demo_ids = {
            "business": "LUKHAS©DEMO-3-Y5Z6-⬢-A7B8",
            "enterprise": "LUKHAS⬟CORP-DIV-4-C9D0-⟐-E1F2",
        }

        # Educational content
        self.educational_content = self._load_educational_content()

        # Rate limiting (simple in-memory for demo)
        self.rate_limits = {}

    def _load_educational_content(self) -> dict[str, Any]:
        """Load educational content for the previewer."""
        return {
            "tier_explanations": {
                0: {
                    "name": "Invisible",
                    "description": "Basic anonymous identity with minimal features",
                    "features": [
                        "Anonymous access",
                        "Basic format",
                        "Limited symbolic characters",
                    ],
                    "symbolic_chars": ["○", "◊", "△"],
                    "use_cases": [
                        "Anonymous browsing",
                        "Temporary access",
                        "Privacy-focused interactions",
                    ],
                },
                1: {
                    "name": "Individual",
                    "description": "Personal identity with enhanced features",
                    "features": [
                        "Personal profiles",
                        "Basic recovery",
                        "Extended symbolic set",
                    ],
                    "symbolic_chars": ["○", "◊", "△", "□", "▽"],
                    "use_cases": [
                        "Personal accounts",
                        "Social interactions",
                        "Basic commerce",
                    ],
                },
                2: {
                    "name": "Family",
                    "description": "Enhanced access with emoji support and recovery features",
                    "features": [
                        "Emoji support",
                        "QR-G recovery",
                        "Cross-device sync",
                    ],
                    "symbolic_chars": ["🌀", "✨", "🔮", "◊", "⟐"],
                    "use_cases": [
                        "Family accounts",
                        "Shared devices",
                        "Enhanced security",
                    ],
                },
                3: {
                    "name": "Community",
                    "description": "Advanced features for community participation",
                    "features": [
                        "Advanced entropy",
                        "Community features",
                        "Enhanced validation",
                    ],
                    "symbolic_chars": ["⟐", "◈", "⬟", "⬢", "⟡"],
                    "use_cases": [
                        "Community leadership",
                        "Advanced features",
                        "Professional use",
                    ],
                },
                4: {
                    "name": "Creator",
                    "description": "Professional tier with live entropy optimization",
                    "features": [
                        "Live entropy feedback",
                        "Professional tools",
                        "Advanced analytics",
                    ],
                    "symbolic_chars": ["◈", "⬟", "⟢", "⟣", "⟤"],
                    "use_cases": [
                        "Content creation",
                        "Professional services",
                        "Advanced features",
                    ],
                },
                5: {
                    "name": "Visionary",
                    "description": "Premium tier with maximum features and capabilities",
                    "features": [
                        "All features",
                        "Priority support",
                        "Beta access",
                    ],
                    "symbolic_chars": ["✨", "🌟", "⭐", "💫", "🔥"],
                    "use_cases": [
                        "Enterprise use",
                        "Maximum capabilities",
                        "Innovation access",
                    ],
                },
            },
            "format_guide": {
                "standard": {
                    "pattern": "LUKHAS{tier}-{timestamp}-{symbolic}-{entropy}",
                    "description": "Standard ΛiD format for individual users",
                    "components": {
                        "lambda_symbol": "LUKHAS - Universal lambda symbol",
                        "tier": "0-5 tier designation",
                        "timestamp": "4-character timestamp hash",
                        "symbolic": "Tier-specific symbolic character",
                        "entropy": "4-character entropy hash",
                    },
                },
                "commercial": {
                    "pattern": "LUKHAS©{brand}-{tier}-{timestamp}-{symbolic}-{entropy}",
                    "description": "Commercial ΛiD format with branded prefixes",
                    "components": {
                        "commercial_prefix": "LUKHAS© - Commercial designation",
                        "brand": "2-8 character brand code",
                        "tier": "Enhanced tier (base + commercial boost)",
                        "timestamp": "3-4 character timestamp hash",
                        "symbolic": "Commercial symbolic character",
                        "entropy": "3-4 character entropy hash",
                    },
                },
                "enterprise": {
                    "pattern": "LUKHAS⬟{brand}-{division}-{tier}-{timestamp}-{symbolic}-{entropy}",
                    "description": "Enterprise ΛiD format with division support",
                    "components": {
                        "enterprise_prefix": "LUKHAS⬟ - Enterprise designation",
                        "brand": "2-8 character brand code",
                        "division": "2-3 character division code",
                        "tier": "Enhanced tier (base + enterprise boost)",
                        "timestamp": "3-4 character timestamp hash",
                        "symbolic": "Enterprise symbolic character",
                        "entropy": "3-4 character entropy hash",
                    },
                },
            },
            "entropy_guide": {
                "what_is_entropy": "Entropy measures the randomness and unpredictability of your ΛiD, contributing to its security and uniqueness.",
                "levels": {
                    "very_low": {
                        "range": "0.0-0.8",
                        "description": "Poor entropy, predictable patterns",
                        "color": "#ff4444",
                    },
                    "low": {
                        "range": "0.8-1.5",
                        "description": "Below recommended, some patterns",
                        "color": "#ff8800",
                    },
                    "medium": {
                        "range": "1.5-2.5",
                        "description": "Good entropy, adequate security",
                        "color": "#ffaa00",
                    },
                    "high": {
                        "range": "2.5-3.5",
                        "description": "Excellent entropy, strong security",
                        "color": "#88dd00",
                    },
                    "very_high": {
                        "range": "3.5+",
                        "description": "Maximum entropy, optimal security",
                        "color": "#00dd88",
                    },
                },
                "boost_factors": {
                    "unicode_symbols": "1.3x boost for Unicode symbolic characters",
                    "pattern_complexity": "1.1x boost for complex patterns",
                    "character_diversity": "1.05x boost for diverse character types",
                },
                "optimization_tips": [
                    "Use Unicode symbolic characters for entropy boost",
                    "Avoid repeating patterns in timestamp or entropy components",
                    "Mix different character types for maximum diversity",
                    "Higher tiers have access to more entropy-rich symbolic characters",
                ],
            },
        }

    def preview_lambda_id(self, lambda_id: str, include_educational: bool = True) -> PreviewResult:
        """
        Preview and analyze a ΛiD with comprehensive feedback.

        Args:
            lambda_id: The ΛiD to preview and analyze
            include_educational: Whether to include educational content

        Returns:
            Comprehensive preview result with analysis and suggestions
        """
        # Sanitize input
        lambda_id = self._sanitize_input(lambda_id)

        # Initialize result
        result = PreviewResult(
            lambda_id=lambda_id,
            is_valid=False,
            format_type="invalid",
            tier=None,
            entropy_score=None,
            entropy_level=None,
            validation_details={},
            analysis={},
            suggestions=[],
            warnings=[],
            errors=[],
            educational_content=None,
        )

        try:
            # Determine format type
            format_info = self._analyze_format(lambda_id)
            result.format_type = format_info["type"]

            # Validate ΛiD
            if format_info["type"] == "commercial":
                validation_result = self._validate_commercial_lambda_id(lambda_id)
            else:
                validation_result = self.validator.validate_lambda_id(lambda_id, validation_level="full")

            result.is_valid = (
                validation_result.valid
                if hasattr(validation_result, "valid")
                else validation_result.get("valid", False)
            )
            result.validation_details = self._format_validation_details(validation_result)

            # Extract tier information
            if result.is_valid:
                result.tier = self._extract_tier(lambda_id, format_info)

                # Calculate entropy
                if result.tier is not None:
                    result.entropy_score = self.entropy_engine.calculate_entropy(lambda_id, result.tier)
                    entropy_analysis = self.entropy_engine.analyze_entropy(lambda_id, result.tier)
                    result.entropy_level = entropy_analysis.get("entropy_level", "unknown")

                    # Generate analysis
                    result.analysis = self._generate_analysis(lambda_id, format_info, entropy_analysis)

                    # Generate suggestions
                    result.suggestions = self._generate_suggestions(lambda_id, format_info, entropy_analysis)

            # Check for warnings
            result.warnings = self._generate_warnings(lambda_id, format_info, result)

            # Add educational content
            if include_educational:
                result.educational_content = self._get_educational_content(result)

        except Exception as e:
            result.errors.append(f"Analysis error: {e!s}")

        return result

    def _sanitize_input(self, input_string: str) -> str:
        """Sanitize user input for security."""
        if not isinstance(input_string, str):
            return ""

        # Remove dangerous characters and limit length
        sanitized = input_string.strip()[:100]  # Max 100 chars

        # Remove control characters except printable ones
        sanitized = "".join(char for char in sanitized if ord(char) >= 32 or char in "\t\n\r")

        return sanitized

    def _analyze_format(self, lambda_id: str) -> dict[str, Any]:
        """Analyze the format type of a ΛiD."""
        import re

        # Standard format: LUKHAS{tier}-{timestamp}-{symbolic}-{entropy}
        standard_pattern = r"^LUKHAS(\d)-([A-F0-9]{4})-(.)-([A-F0-9]{4})$"

        # Commercial format: LUKHAS©{brand}-{tier}-{timestamp}-{symbolic}-{entropy}
        commercial_pattern = r"^LUKHAS©([A-Z0-9]{2,8})-(\d)-([A-F0-9]{3,4})-(.)-([A-F0-9]{3,4})$"

        # Enterprise format:
        # LUKHAS⬟{brand}-{division}-{tier}-{timestamp}-{symbolic}-{entropy}
        enterprise_pattern = r"^LUKHAS⬟([A-Z0-9]{2,8})-([A-Z]{2,3})-(\d)-([A-F0-9]{3,4})-(.))-([A-F0-9]{3,4})$"

        # Check formats
        if re.match(standard_pattern, lambda_id):
            match = re.match(standard_pattern, lambda_id)
            return {
                "type": "standard",
                "components": {
                    "tier": int(match.group(1)),
                    "timestamp_hash": match.group(2),
                    "symbolic_char": match.group(3),
                    "entropy_hash": match.group(4),
                },
            }
        elif re.match(commercial_pattern, lambda_id):
            match = re.match(commercial_pattern, lambda_id)
            return {
                "type": "commercial",
                "subtype": "business",
                "components": {
                    "brand_code": match.group(1),
                    "tier": int(match.group(2)),
                    "timestamp_hash": match.group(3),
                    "symbolic_char": match.group(4),
                    "entropy_hash": match.group(5),
                },
            }
        elif re.match(enterprise_pattern, lambda_id):
            match = re.match(enterprise_pattern, lambda_id)
            return {
                "type": "commercial",
                "subtype": "enterprise",
                "components": {
                    "brand_code": match.group(1),
                    "division": match.group(2),
                    "tier": int(match.group(3)),
                    "timestamp_hash": match.group(4),
                    "symbolic_char": match.group(5),
                    "entropy_hash": match.group(6),
                },
            }
        else:
            return {"type": "invalid", "components": {}}

    def _validate_commercial_lambda_id(self, lambda_id: str) -> dict[str, Any]:
        """Validate commercial ΛiD (with mock validation for public preview)."""
        # For public preview, we use mock validation to avoid exposing real
        # commercial data
        format_info = self._analyze_format(lambda_id)

        if format_info["type"] != "commercial":
            return {"valid": False, "errors": ["Not a commercial format"]}

        # Mock validation for demonstration
        return {
            "valid": True,
            "format": "commercial",
            "commercial_info": format_info,
            "brand_validation": {
                "brand_code": format_info["components"]["brand_code"],
                "valid": True,  # Mock approval for preview
                "status": "approved",
                "note": "Demo validation - real validation requires commercial account",
            },
            "checks": {
                "format_valid": True,
                "tier_compliant": True,
                "commercial_tier_match": True,
                "symbolic_char_authorized": True,
            },
            "warnings": ["This is a demo validation - commercial ΛiDs require verification"],
            "errors": [],
        }

    def _extract_tier(self, lambda_id: str, format_info: dict[str, Any]) -> Optional[int]:
        """Extract tier information from ΛiD."""
        if format_info["type"] in ["standard", "commercial"]:
            return format_info["components"].get("tier")
        return None

    def _format_validation_details(self, validation_result) -> dict[str, Any]:
        """Format validation details for display."""
        if hasattr(validation_result, "__dict__"):
            return {
                "valid": validation_result.valid,
                "errors": getattr(validation_result, "errors", []),
                "warnings": getattr(validation_result, "warnings", []),
                "checks_passed": getattr(validation_result, "checks_passed", []),
                "validation_level": getattr(validation_result, "validation_level", "unknown"),
            }
        elif isinstance(validation_result, dict):
            return validation_result
        else:
            return {
                "valid": False,
                "errors": ["Unknown validation result format"],
            }

    def _generate_analysis(
        self,
        lambda_id: str,
        format_info: dict[str, Any],
        entropy_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate comprehensive analysis of the ΛiD."""
        analysis = {
            "format": {
                "type": format_info["type"],
                "description": self._get_format_description(format_info["type"]),
                "components": format_info["components"],
            },
            "entropy": {
                "score": entropy_analysis.get("overall_score", 0),
                "level": entropy_analysis.get("entropy_level", "unknown"),
                "base_entropy": entropy_analysis.get("base_entropy", 0),
                "boost_factors": entropy_analysis.get("boost_factors", {}),
                "component_scores": entropy_analysis.get("component_scores", {}),
            },
            "security": {
                "strength": self._assess_security_strength(entropy_analysis),
                "recommendations": self._get_security_recommendations(entropy_analysis),
            },
        }

        # Add tier-specific analysis
        if format_info["components"].get("tier") is not None:
            tier = format_info["components"]["tier"]
            analysis["tier"] = {
                "number": tier,
                "name": self.educational_content["tier_explanations"][tier]["name"],
                "description": self.educational_content["tier_explanations"][tier]["description"],
                "features": self.educational_content["tier_explanations"][tier]["features"],
            }

        # Add commercial-specific analysis
        if format_info["type"] == "commercial":
            analysis["commercial"] = {
                "subtype": format_info.get("subtype", "business"),
                "brand_code": format_info["components"].get("brand_code", ""),
                "benefits": self._get_commercial_benefits(format_info.get("subtype", "business")),
            }

            if "division" in format_info["components"]:
                analysis["commercial"]["division"] = format_info["components"]["division"]

        return analysis

    def _get_format_description(self, format_type: str) -> str:
        """Get description for format type."""
        descriptions = {
            "standard": "Standard ΛiD format for individual users with tier-based features",
            "commercial": "Commercial ΛiD format with branded prefixes and enhanced capabilities",
            "invalid": "Invalid or unrecognized ΛiD format",
        }
        return descriptions.get(format_type, "Unknown format")

    def _assess_security_strength(self, entropy_analysis: dict[str, Any]) -> str:
        """Assess overall security strength based on entropy."""
        score = entropy_analysis.get("overall_score", 0)

        if score >= 3.5:
            return "excellent"
        elif score >= 2.5:
            return "strong"
        elif score >= 1.5:
            return "adequate"
        elif score >= 0.8:
            return "weak"
        else:
            return "poor"

    def _get_security_recommendations(self, entropy_analysis: dict[str, Any]) -> list[str]:
        """Get security recommendations based on entropy analysis."""
        recommendations = []
        score = entropy_analysis.get("overall_score", 0)

        if score < 1.5:
            recommendations.append("Consider upgrading to a higher tier for better entropy options")
            recommendations.append("Use Unicode symbolic characters when available")

        if score < 2.5:
            recommendations.append("Entropy could be improved with tier upgrade")

        boost_factors = entropy_analysis.get("boost_factors", {})
        if boost_factors.get("unicode_symbolic", 1.0) < 1.2:
            recommendations.append("Use Unicode symbols for entropy boost")

        return recommendations

    def _get_commercial_benefits(self, subtype: str) -> list[str]:
        """Get benefits for commercial ΛiD subtypes."""
        benefits = {
            "business": [
                "Branded prefix for company identity",
                "Enhanced tier capabilities",
                "Commercial symbolic characters",
                "Business dashboard access",
                "Priority support",
            ],
            "enterprise": [
                "Division-based organization",
                "Maximum tier enhancement",
                "Enterprise symbolic characters",
                "Advanced analytics",
                "Dedicated support",
                "Custom integrations",
            ],
        }
        return benefits.get(subtype, [])

    def _generate_suggestions(
        self,
        lambda_id: str,
        format_info: dict[str, Any],
        entropy_analysis: dict[str, Any],
    ) -> list[str]:
        """Generate improvement suggestions."""
        suggestions = []

        # Entropy-based suggestions
        score = entropy_analysis.get("overall_score", 0)
        if score < 2.0:
            suggestions.append("Consider using higher-entropy symbolic characters")
            suggestions.append("Tier upgrades provide access to better entropy options")

        # Format-specific suggestions
        if format_info["type"] == "standard":
            tier = format_info["components"].get("tier", 0)
            if tier < 2:
                suggestions.append("Tier 2+ includes emoji support and recovery features")
            if tier < 4:
                suggestions.append("Tier 4+ includes live entropy optimization")

        # Commercial suggestions
        if format_info["type"] == "commercial" and format_info.get("subtype") == "business":
            suggestions.append("Enterprise tier offers division support and advanced features")

        return suggestions

    def _generate_warnings(
        self,
        lambda_id: str,
        format_info: dict[str, Any],
        result: PreviewResult,
    ) -> list[str]:
        """Generate warnings for the ΛiD."""
        warnings = []

        # Format warnings
        if format_info["type"] == "invalid":
            warnings.append("ΛiD format is not recognized")

        # Entropy warnings
        if result.entropy_score and result.entropy_score < 1.0:
            warnings.append("Low entropy detected - security may be compromised")

        # Commercial warnings
        if format_info["type"] == "commercial":
            warnings.append("Commercial ΛiD preview - actual validation requires commercial account")

        return warnings

    def _get_educational_content(self, result: PreviewResult) -> dict[str, Any]:
        """Get relevant educational content based on the preview result."""
        content = {
            "format_guide": self.educational_content["format_guide"].get(result.format_type, {}),
            "entropy_guide": self.educational_content["entropy_guide"],
        }

        # Add tier-specific content
        if result.tier is not None:
            content["tier_info"] = self.educational_content["tier_explanations"].get(result.tier, {})

        # Add related demos
        content["related_demos"] = self._get_related_demos(result)

        return content

    def _get_related_demos(self, result: PreviewResult) -> list[dict[str, str]]:
        """Get related demo ΛiDs for exploration."""
        demos = []

        # Add tier demos
        for tier, demo_id in self.demo_lambda_ids.items():
            tier_num = int(tier.split("_")[1])
            demos.append(
                {
                    "id": demo_id,
                    "description": f"Tier {tier_num} ({self.educational_content['tier_explanations'][tier_num]['name']}) Example",
                    "category": "tier_demo",
                }
            )

        # Add commercial demos
        for commercial_type, demo_id in self.commercial_demo_ids.items():
            demos.append(
                {
                    "id": demo_id,
                    "description": f"Commercial {commercial_type.title()} Example",
                    "category": "commercial_demo",
                }
            )

        return demos

    def generate_demo_lambda_id(self, tier: int = 2, format_type: str = "standard") -> dict[str, Any]:
        """Generate a demo ΛiD for educational purposes."""
        try:
            if format_type == "standard":
                # Use existing demo or generate safe demo
                if f"tier_{tier}" in self.demo_lambda_ids:
                    demo_id = self.demo_lambda_ids[f"tier_{tier}"]
                else:
                    # Generate safe demo ID (not stored, for demonstration only)
                    import random

                    timestamp_hash = "".join(random.choices("ABCDEF0123456789", k=4))
                    entropy_hash = "".join(random.choices("ABCDEF0123456789", k=4))

                    # Get tier-appropriate symbolic character
                    tier_symbols = self.educational_content["tier_explanations"][tier]["symbolic_chars"]
                    symbolic_char = random.choice(tier_symbols)

                    demo_id = f"LUKHAS{tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

                return {
                    "success": True,
                    "lambda_id": demo_id,
                    "type": "demo",
                    "tier": tier,
                    "note": "This is a demonstration ΛiD for educational purposes only",
                }

            elif format_type == "commercial":
                # Return commercial demo
                if tier >= 3:
                    demo_id = self.commercial_demo_ids["business"]
                    commercial_type = "business"
                else:
                    demo_id = self.commercial_demo_ids["enterprise"]
                    commercial_type = "enterprise"

                return {
                    "success": True,
                    "lambda_id": demo_id,
                    "type": "commercial_demo",
                    "commercial_type": commercial_type,
                    "note": "This is a demonstration commercial ΛiD - real commercial features require account setup",
                }

            else:
                return {
                    "success": False,
                    "error": "Unsupported demo format type",
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Demo generation failed: {e!s}",
            }

    def get_tier_comparison(self) -> dict[str, Any]:
        """Get comprehensive tier comparison data."""
        return {
            "tiers": self.educational_content["tier_explanations"],
            "feature_matrix": {
                "anonymous_access": [True, False, False, False, False, False],
                "personal_profiles": [False, True, True, True, True, True],
                "emoji_support": [False, False, True, True, True, True],
                "recovery_features": [False, True, True, True, True, True],
                "cross_device_sync": [False, False, True, True, True, True],
                "advanced_entropy": [False, False, False, True, True, True],
                "live_optimization": [False, False, False, False, True, True],
                "professional_tools": [False, False, False, False, True, True],
                "premium_support": [False, False, False, False, False, True],
                "beta_access": [False, False, False, False, False, True],
            },
            "symbolic_character_access": {
                tier: info["symbolic_chars"] for tier, info in self.educational_content["tier_explanations"].items()
            },
            "upgrade_paths": {
                tier: {
                    "next_tier": tier + 1 if tier < 5 else None,
                    "benefits": (
                        self.educational_content["tier_explanations"][tier + 1]["features"] if tier < 5 else []
                    ),
                    "new_symbols": (
                        self.educational_content["tier_explanations"][tier + 1]["symbolic_chars"] if tier < 5 else []
                    ),
                }
                for tier in range(6)
            },
        }

    def get_format_specifications(self) -> dict[str, Any]:
        """Get detailed format specifications."""
        return {
            "format_guide": self.educational_content["format_guide"],
            "validation_rules": {
                "tier_range": "0-5 for standard format",
                "timestamp_hash": "4 hexadecimal characters (A-F, 0-9)",
                "entropy_hash": "4 hexadecimal characters (A-F, 0-9)",
                "symbolic_characters": "Tier-specific Unicode or ASCII symbols",
                "brand_codes": "2-8 alphanumeric characters (commercial only)",
                "division_codes": "2-3 alphabetic characters (enterprise only)",
            },
            "examples": {
                "valid_standard": list(self.demo_lambda_ids.values()),
                "valid_commercial": list(self.commercial_demo_ids.values()),
                "invalid_examples": [
                    {"id": "Λ10-ABCD-🔮-EFGH", "error": "Invalid tier (10)"},
                    {
                        "id": "Λ2-GGGG-🔮-HHHH",
                        "error": "Invalid hex characters (G)",
                    },
                    {
                        "id": "Λ2-ABCD-💀-EFGH",
                        "error": "Symbolic character not allowed for tier",
                    },
                    {
                        "id": "Lambda2-ABCD-🔮-EFGH",
                        "error": "Must use lambda symbol (LUKHAS)",
                    },
                ],
            },
        }

    def analyze_entropy_live(self, partial_lambda_id: str) -> dict[str, Any]:
        """Provide live entropy analysis for partial ΛiD input."""
        # This is a simplified version for public preview
        # Real implementation would integrate with entropy engine

        analysis = {
            "current_length": len(partial_lambda_id),
            "progress": "incomplete",
            "current_entropy": 0.0,
            "suggestions": [],
            "next_character_suggestions": [],
            "format_validation": {"valid": False, "errors": []},
        }

        try:
            # Basic format checking
            if partial_lambda_id.startswith("LUKHAS"):
                analysis["format_validation"]["valid"] = True
                analysis["suggestions"].append("Good start with lambda symbol")

                # Check for tier
                if len(partial_lambda_id) >= 2 and partial_lambda_id[1].isdigit():
                    tier = int(partial_lambda_id[1])
                    if 0 <= tier <= 5:
                        analysis["suggestions"].append(f"Valid tier {tier} detected")

                        # Get tier-specific suggestions
                        tier_info = self.educational_content["tier_explanations"][tier]
                        analysis["next_character_suggestions"] = [
                            f"Use {char} for tier {tier}" for char in tier_info["symbolic_chars"][:3]
                        ]
                    else:
                        analysis["format_validation"]["errors"].append(f"Invalid tier: {tier}")

                # Estimate current entropy
                if len(partial_lambda_id) > 2:
                    # Simple entropy estimation
                    unique_chars = len(set(partial_lambda_id))
                    analysis["current_entropy"] = min(unique_chars * 0.3, 4.0)

            else:
                analysis["format_validation"]["errors"].append("Must start with LUKHAS symbol")
                analysis["suggestions"].append("Start with the lambda symbol: LUKHAS")

        except Exception as e:
            analysis["format_validation"]["errors"].append(f"Analysis error: {e!s}")

        return analysis

    def get_public_api_info(self) -> dict[str, Any]:
        """Get information about public API endpoints for the previewer."""
        return {
            "endpoints": {
                "preview": {
                    "path": "/api/public/preview",
                    "method": "POST",
                    "description": "Preview and analyze a ΛiD",
                    "parameters": {
                        "lambda_id": "ΛiD string to analyze",
                        "include_educational": "Include educational content (optional, default: true)",
                    },
                    "rate_limit": "100 requests per hour per IP",
                },
                "demo": {
                    "path": "/api/public/demo",
                    "method": "GET",
                    "description": "Generate demo ΛiD for education",
                    "parameters": {
                        "tier": "Tier level 0-5 (optional, default: 2)",
                        "format": "Format type: standard or commercial (optional, default: standard)",
                    },
                    "rate_limit": "50 requests per hour per IP",
                },
                "tiers": {
                    "path": "/api/public/tiers",
                    "method": "GET",
                    "description": "Get tier comparison and information",
                    "rate_limit": "20 requests per hour per IP",
                },
                "formats": {
                    "path": "/api/public/formats",
                    "method": "GET",
                    "description": "Get format specifications and examples",
                    "rate_limit": "20 requests per hour per IP",
                },
                "entropy": {
                    "path": "/api/public/entropy/live",
                    "method": "POST",
                    "description": "Live entropy analysis for partial input",
                    "parameters": {"partial_lambda_id": "Partial ΛiD string"},
                    "rate_limit": "200 requests per hour per IP",
                },
            },
            "authentication": "None required for public endpoints",
            "cors": "Enabled for web browser access",
            "usage_guidelines": [
                "Educational and preview purposes only",
                "No real user data processing",
                "Rate limits apply to prevent abuse",
                "Commercial features shown as demos only",
            ],
        }


# Web Interface HTML Template (for reference)


def get_web_interface_template() -> str:
    """Get the HTML template for the web interface."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LUKHAS ΛiD Public Previewer</title>
    <style>
        /* Modern, accessible CSS styling would go here */
        /* Includes responsive design, dark/light mode, accessibility features */
    </style>
</head>
<body>
    <header>
        <h1>LUKHAS ΛiD Public Previewer</h1>
        <nav>
            <!-- Navigation for different sections -->
        </nav>
    </header>

    <main>
        <section id="previewer">
            <!-- Live ΛiD preview interface -->
        </section>

        <section id="education">
            <!-- Educational content and tutorials -->
        </section>

        <section id="demos">
            <!-- Demo ΛiDs and examples -->
        </section>
    </main>

    <footer>
        <!-- Footer with links and information -->
    </footer>

    <script>
        // JavaScript for interactive functionality
        // Real-time preview, entropy visualization, etc.
    </script>
</body>
</html>
    """
