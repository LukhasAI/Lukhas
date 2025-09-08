"""
LUKHAS ΛiD Commercial Module - Branded Prefix System

This module handles commercial-tier ΛiD generation with branded prefixes,
following a hybrid namespace approach for maximum flexibility while maintaining
backward compatibility.

Supported Formats:
- Standard: LUKHAS{tier}-{timestamp}-{symbolic}-{entropy}
- Commercial: LUKHAS©{brand}-{tier}-{timestamp}-{symbolic}-{entropy}
- Enterprise: LUKHAS⬟{brand}-{division}-{tier}-{timestamp}-{symbolic}-{entropy}

Author: LUKHAS AI Systems
Version: 2.0.0
Last Updated: July 5, 2025
"""
import hashlib
import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional


from ..id_service.entropy_engine import EntropyEngine
from ..id_service.lambd_id_validator import LambdaIDValidator


class CommercialTier(Enum):
    """Commercial tier definitions with enhanced permissions."""

    BUSINESS = "business"
    ENTERPRISE = "enterprise"
    CORPORATE = "corporate"
    WHITE_LABEL = "white_label"


class BrandStatus(Enum):
    """Brand prefix registration status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    EXPIRED = "expired"


@dataclass
class BrandPrefix:
    """Represents a registered brand prefix for commercial ΛiDs."""

    brand_code: str
    company_name: str
    contact_email: str
    commercial_tier: CommercialTier
    status: BrandStatus
    registration_date: datetime
    expiry_date: datetime
    verification_documents: dict[str, str]
    usage_stats: dict[str, Any]
    restrictions: dict[str, Any]

    def is_valid(self) -> bool:
        """Check if brand prefix is currently valid."""
        return self.status == BrandStatus.APPROVED and self.expiry_date > datetime.now(timezone.utc)


@dataclass
class CommercialLambdaIDResult:
    """Enhanced result object for commercial ΛiD operations."""

    success: bool
    lambda_id: Optional[str] = None
    brand_prefix: Optional[str] = None
    commercial_tier: Optional[CommercialTier] = None
    generation_time: Optional[datetime] = None
    entropy_score: Optional[float] = None
    validation_result: Optional[dict[str, Any]] = None
    billing_info: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class CommercialModule:
    """
    Commercial ΛiD module with branded prefix support.

    Implements hybrid namespace system:
    - LUKHAS© prefix for commercial business tier
    - LUKHAS⬟ prefix for enterprise tier with division support
    - Full backward compatibility with standard LUKHAS format
    """

    def __init__(self, config_path: str = "config/commercial_config.json"):
        """Initialize commercial module with configuration."""
        self.config = self._load_config(config_path)
        self.validator = LambdaIDValidator()
        self.entropy_engine = EntropyEngine()
        self.registered_brands: dict[str, BrandPrefix] = {}
        self.usage_tracking: dict[str, dict[str, Any]] = {}

        # Commercial symbolic characters (exclusive to paid tiers)
        self.commercial_symbols = {
            CommercialTier.BUSINESS: ["⬢", "⬡", "⬟", "◈", "◇", "⬛", "⬜"],
            CommercialTier.ENTERPRISE: ["⟐", "⟡", "⟢", "⟣", "⟤", "⟥", "⟦", "⟧"],
            CommercialTier.CORPORATE: ["⬢", "⬡", "⬟", "◈", "◇", "⟐", "⟡", "⟢"],
            CommercialTier.WHITE_LABEL: ["★", "☆", "✦", "✧", "✩", "✪", "⭐", "🌟"],
        }

        # Initialize brand registry
        self._load_brand_registry()

    def _load_config(self, config_path: str) -> dict[str, Any]:
        """Load commercial module configuration."""
        try:
            with open(config_path) as f:
                return json.load(f)
        except FileNotFoundError:
            # Default configuration
            return {
                "commercial_tiers": {
                    "business": {
                        "base_tier": 3,
                        "monthly_cost": 99.99,
                        "max_lambda_ids": 1000,
                        "max_brand_prefixes": 5,
                        "rate_limit": 5000,
                    },
                    "enterprise": {
                        "base_tier": 4,
                        "monthly_cost": 499.99,
                        "max_lambda_ids": 10000,
                        "max_brand_prefixes": 20,
                        "rate_limit": 20000,
                    },
                },
                "brand_prefix_validation": {
                    "min_length": 2,
                    "max_length": 8,
                    "allowed_chars": "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                    "reserved_prefixes": ["LUKHAS", "LAMBDA", "ADMIN", "SYSTEM"],
                    "verification_required": True,
                },
                "billing": {
                    "currency": "USD",
                    "billing_cycle": "monthly",
                    "grace_period_days": 7,
                },
            }

    def _load_brand_registry(self):
        """Load registered brand prefixes from storage."""
        # In production, this would load from database
        # For now, initialize with empty registry

    def register_brand_prefix(
        self,
        brand_code: str,
        company_name: str,
        contact_email: str,
        commercial_tier: CommercialTier,
        verification_documents: dict[str, str],
    ) -> dict[str, Any]:
        """
        Register a new brand prefix for commercial use.

        Args:
            brand_code: Unique brand identifier (2-8 chars, alphanumeric)
            company_name: Legal company name
            contact_email: Primary contact email
            commercial_tier: Commercial tier level
            verification_documents: URLs to verification documents

        Returns:
            Registration result with status and next steps
        """
        # Validate brand code format
        if not self._validate_brand_code(brand_code):
            return {
                "success": False,
                "error": "Invalid brand code format",
                "requirements": {
                    "length": "2-8 characters",
                    "characters": "Alphanumeric only",
                    "case": "Uppercase recommended",
                },
            }

        # Check if brand code is already registered
        if brand_code in self.registered_brands:
            return {
                "success": False,
                "error": "Brand code already registered",
                "suggestion": "Try a different brand code or contact support",
            }

        # Check reserved prefixes
        if brand_code in self.config["brand_prefix_validation"]["reserved_prefixes"]:
            return {
                "success": False,
                "error": "Brand code is reserved",
                "suggestion": "Choose a different brand code",
            }

        # Create brand registration
        registration_id = f"brand_reg_{int(time.time())}"
        expiry_date = datetime.now(timezone.utc) + timedelta(days=365)

        brand_prefix = BrandPrefix(
            brand_code=brand_code,
            company_name=company_name,
            contact_email=contact_email,
            commercial_tier=commercial_tier,
            status=BrandStatus.PENDING,
            registration_date=datetime.now(timezone.utc),
            expiry_date=expiry_date,
            verification_documents=verification_documents,
            usage_stats={
                "lambda_ids_generated": 0,
                "total_validations": 0,
                "last_used": None,
            },
            restrictions={},
        )

        # Store registration (in production, save to database)
        self.registered_brands[brand_code] = brand_prefix

        return {
            "success": True,
            "registration_id": registration_id,
            "brand_code": brand_code,
            "status": "pending_verification",
            "estimated_approval_time": "3-5 business days",
            "verification_requirements": [
                "Trademark verification",
                "Business license validation",
                "Contact verification",
            ],
            "next_steps": [
                "Await verification email",
                "Complete identity verification",
                "Setup billing information",
            ],
        }

    def _validate_brand_code(self, brand_code: str) -> bool:
        """Validate brand code format."""
        config = self.config["brand_prefix_validation"]

        # Check length
        if not (config["min_length"] <= len(brand_code) <= config["max_length"]):
            return False

        # Check allowed characters
        allowed_chars = set(config["allowed_chars"])
        return all(char in allowed_chars for char in brand_code.upper())

    def generate_commercial_lambda_id(
        self,
        brand_code: str,
        tier: int,
        user_context: dict[str, Any],
        options: Optional[dict[str, Any]] = None,
    ) -> CommercialLambdaIDResult:
        """
        Generate a commercial ΛiD with branded prefix.

        Args:
            brand_code: Registered brand prefix
            tier: Base tier level (enhanced by commercial tier)
            user_context: User and billing context
            options: Generation options

        Returns:
            Commercial ΛiD generation result
        """
        # Validate brand prefix
        if brand_code not in self.registered_brands:
            return CommercialLambdaIDResult(success=False, error="Brand prefix not registered")

        brand_prefix = self.registered_brands[brand_code]
        if not brand_prefix.is_valid():
            return CommercialLambdaIDResult(success=False, error=f"Brand prefix status: {brand_prefix.status.value}")

        # Determine commercial format
        commercial_tier = brand_prefix.commercial_tier

        try:
            if commercial_tier == CommercialTier.BUSINESS:
                lambda_id = self._generate_business_format(brand_code, tier, user_context, options)
            elif commercial_tier == CommercialTier.ENTERPRISE:
                lambda_id = self._generate_enterprise_format(brand_code, tier, user_context, options)
            elif commercial_tier == CommercialTier.CORPORATE:
                lambda_id = self._generate_corporate_format(brand_code, tier, user_context, options)
            elif commercial_tier == CommercialTier.WHITE_LABEL:
                lambda_id = self._generate_white_label_format(brand_code, tier, user_context, options)
            else:
                raise ValueError(f"Unsupported commercial tier: {commercial_tier}")

            # Validate generated ΛiD
            validation_result = self.validator.validate_lambda_id(
                lambda_id,
                validation_level="enterprise",
                context={"commercial": True, "brand_code": brand_code, "tier": tier},
            )

            if not validation_result.valid:
                return CommercialLambdaIDResult(
                    success=False,
                    error="Generated ΛiD failed validation",
                    validation_result=validation_result.__dict__,
                )

            # Calculate entropy
            entropy_score = self.entropy_engine.calculate_entropy(lambda_id, tier)

            # Update usage statistics
            self._update_usage_stats(brand_code, lambda_id)

            # Calculate billing info
            billing_info = self._calculate_billing(brand_prefix, user_context)

            return CommercialLambdaIDResult(
                success=True,
                lambda_id=lambda_id,
                brand_prefix=brand_code,
                commercial_tier=commercial_tier,
                generation_time=datetime.now(timezone.utc),
                entropy_score=entropy_score,
                validation_result=validation_result.__dict__,
                billing_info=billing_info,
                metadata={
                    "format": "commercial",
                    "tier_enhanced": True,
                    "symbolic_pool": "commercial",
                },
            )

        except Exception as e:
            return CommercialLambdaIDResult(success=False, error=f"Generation failed: {e!s}")

    def _generate_business_format(
        self,
        brand_code: str,
        tier: int,
        user_context: dict[str, Any],
        options: Optional[dict[str, Any]],
    ) -> str:
        """
        Generate business tier ΛiD: LUKHAS©{BRAND}-{TIER}-{TIMESTAMP}-{SYMBOLIC}-{ENTROPY}
        """
        # Enhanced tier (business adds +1 to base tier)
        enhanced_tier = min(tier + 1, 5)

        # Generate timestamp hash
        timestamp = str(int(time.time()))[-8:]
        timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:4].upper()

        # Select commercial symbolic character
        symbols = self.commercial_symbols[CommercialTier.BUSINESS]
        symbolic_char = options.get("symbolic_preference") if options else symbols[0]
        if symbolic_char not in symbols:
            symbolic_char = symbols[hash(timestamp) % len(symbols)]

        # Generate entropy component
        entropy_seed = f"{brand_code}{enhanced_tier}{timestamp_hash}{symbolic_char}"
        entropy_hash = hashlib.sha256(entropy_seed.encode()).hexdigest()[:4].upper()

        return f"LUKHAS©{brand_code}-{enhanced_tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

    def _generate_enterprise_format(
        self,
        brand_code: str,
        tier: int,
        user_context: dict[str, Any],
        options: Optional[dict[str, Any]],
    ) -> str:
        """
        Generate enterprise tier ΛiD: LUKHAS⬟{BRAND}-{DIVISION}-{TIER}-{TIMESTAMP}-{SYMBOLIC}-{ENTROPY}
        """
        # Enhanced tier (enterprise adds +2 to base tier)
        enhanced_tier = min(tier + 2, 6)

        # Get division code from user context
        division = user_context.get("division", "GEN")[:3].upper()

        # Generate timestamp hash
        timestamp = str(int(time.time()))[-8:]
        timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:3].upper()

        # Select enterprise symbolic character
        symbols = self.commercial_symbols[CommercialTier.ENTERPRISE]
        symbolic_char = options.get("symbolic_preference") if options else symbols[0]
        if symbolic_char not in symbols:
            symbolic_char = symbols[hash(timestamp) % len(symbols)]

        # Generate entropy component
        entropy_seed = f"{brand_code}{division}{enhanced_tier}{timestamp_hash}{symbolic_char}"
        entropy_hash = hashlib.sha256(entropy_seed.encode()).hexdigest()[:3].upper()

        return f"LUKHAS⬟{brand_code}-{division}-{enhanced_tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

    def _generate_corporate_format(
        self,
        brand_code: str,
        tier: int,
        user_context: dict[str, Any],
        options: Optional[dict[str, Any]],
    ) -> str:
        """
        Generate corporate tier ΛiD with enhanced security features.
        """
        # Corporate tier gets maximum enhancement
        enhanced_tier = min(tier + 2, 6)

        # Generate timestamp hash with microsecond precision
        timestamp = str(int(time.time() * 1000000))[-10:]
        timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:5].upper()

        # Select corporate symbolic character
        symbols = self.commercial_symbols[CommercialTier.CORPORATE]
        symbolic_char = options.get("symbolic_preference") if options else symbols[0]
        if symbolic_char not in symbols:
            symbolic_char = symbols[hash(timestamp) % len(symbols)]

        # Generate enhanced entropy component
        entropy_seed = f"{brand_code}{enhanced_tier}{timestamp_hash}{symbolic_char}{user_context.get('user_id', '')}"
        entropy_hash = hashlib.sha256(entropy_seed.encode()).hexdigest()[:5].upper()

        return f"LUKHAS©{brand_code}-{enhanced_tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

    def _generate_white_label_format(
        self,
        brand_code: str,
        tier: int,
        user_context: dict[str, Any],
        options: Optional[dict[str, Any]],
    ) -> str:
        """
        Generate white-label ΛiD with custom branding.
        """
        # White-label can override prefix symbol
        custom_prefix = user_context.get("custom_prefix", "LUKHAS©")
        enhanced_tier = min(tier + 1, 5)

        # Generate timestamp hash
        timestamp = str(int(time.time()))[-8:]
        timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:4].upper()

        # Select white-label symbolic character
        symbols = self.commercial_symbols[CommercialTier.WHITE_LABEL]
        symbolic_char = options.get("symbolic_preference") if options else symbols[0]
        if symbolic_char not in symbols:
            symbolic_char = symbols[hash(timestamp) % len(symbols)]

        # Generate entropy component
        entropy_seed = f"{brand_code}{enhanced_tier}{timestamp_hash}{symbolic_char}"
        entropy_hash = hashlib.sha256(entropy_seed.encode()).hexdigest()[:4].upper()

        return f"{custom_prefix}{brand_code}-{enhanced_tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

    def _update_usage_stats(self, brand_code: str, lambda_id: str):
        """Update usage statistics for brand prefix."""
        if brand_code in self.registered_brands:
            brand = self.registered_brands[brand_code]
            brand.usage_stats["lambda_ids_generated"] += 1
            brand.usage_stats["last_used"] = datetime.now(timezone.utc)

            # Track daily usage
            today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            if brand_code not in self.usage_tracking:
                self.usage_tracking[brand_code] = {}
            if today not in self.usage_tracking[brand_code]:
                self.usage_tracking[brand_code][today] = 0
            self.usage_tracking[brand_code][today] += 1

    def _calculate_billing(self, brand_prefix: BrandPrefix, user_context: dict[str, Any]) -> dict[str, Any]:
        """Calculate billing information for commercial ΛiD generation."""
        tier_config = self.config["commercial_tiers"][brand_prefix.commercial_tier.value]

        return {
            "commercial_tier": brand_prefix.commercial_tier.value,
            "monthly_cost": tier_config["monthly_cost"],
            "usage_count": brand_prefix.usage_stats["lambda_ids_generated"],
            "usage_limit": tier_config["max_lambda_ids"],
            "billing_cycle": self.config["billing"]["billing_cycle"],
            "currency": self.config["billing"]["currency"],
        }

    def validate_commercial_lambda_id(self, lambda_id: str, validation_level: str = "enterprise") -> dict[str, Any]:
        """
        Validate a commercial ΛiD with enhanced checks.

        Args:
            lambda_id: Commercial ΛiD to validate
            validation_level: Validation thoroughness level

        Returns:
            Enhanced validation result with commercial-specific checks
        """
        # Parse commercial format
        commercial_info = self._parse_commercial_format(lambda_id)
        if not commercial_info["is_commercial"]:
            return {
                "valid": False,
                "error": "Not a commercial ΛiD format",
                "format": "standard",
            }

        # Validate brand prefix
        brand_code = commercial_info["brand_code"]
        if brand_code not in self.registered_brands:
            return {
                "valid": False,
                "error": "Unregistered brand prefix",
                "brand_code": brand_code,
            }

        brand_prefix = self.registered_brands[brand_code]
        if not brand_prefix.is_valid():
            return {
                "valid": False,
                "error": f"Brand prefix status: {brand_prefix.status.value}",
                "brand_code": brand_code,
            }

        # Standard ΛiD validation
        base_validation = self.validator.validate_lambda_id(
            lambda_id,
            validation_level=validation_level,
            context={
                "commercial": True,
                "brand_code": brand_code,
                "tier": commercial_info["tier"],
            },
        )

        # Commercial-specific validation
        commercial_checks = self._validate_commercial_specific(lambda_id, commercial_info, brand_prefix)

        # Combine results
        result = {
            "valid": base_validation.valid and commercial_checks["valid"],
            "lambda_id": lambda_id,
            "format": "commercial",
            "commercial_info": commercial_info,
            "brand_validation": {
                "brand_code": brand_code,
                "company_name": brand_prefix.company_name,
                "commercial_tier": brand_prefix.commercial_tier.value,
                "valid": brand_prefix.is_valid(),
                "status": brand_prefix.status.value,
            },
            "base_validation": base_validation.__dict__,
            "commercial_checks": commercial_checks,
            "entropy_analysis": self.entropy_engine.analyze_entropy(lambda_id, commercial_info["tier"]),
        }

        return result

    def _parse_commercial_format(self, lambda_id: str) -> dict[str, Any]:
        """Parse commercial ΛiD format and extract components."""
        # Business format: LUKHAS©{BRAND}-{TIER}-{TIMESTAMP}-{SYMBOLIC}-{ENTROPY}
        business_pattern = r"^LUKHAS©([A-Z0-9]{2,8})-(\d)-([A-F0-9]{3,4})-(.)-([A-F0-9]{3,4})$"

        # Enterprise format:
        # LUKHAS⬟{BRAND}-{DIVISION}-{TIER}-{TIMESTAMP}-{SYMBOLIC}-{ENTROPY}
        enterprise_pattern = r"^LUKHAS⬟([A-Z0-9]{2,8})-([A-Z]{2,3})-(\d)-([A-F0-9]{3,4})-(.)-([A-F0-9]{3,4})$"

        # Check business format
        business_match = re.match(business_pattern, lambda_id)
        if business_match:
            return {
                "is_commercial": True,
                "format": "business",
                "brand_code": business_match.group(1),
                "tier": int(business_match.group(2)),
                "timestamp_hash": business_match.group(3),
                "symbolic_char": business_match.group(4),
                "entropy_hash": business_match.group(5),
            }

        # Check enterprise format
        enterprise_match = re.match(enterprise_pattern, lambda_id)
        if enterprise_match:
            return {
                "is_commercial": True,
                "format": "enterprise",
                "brand_code": enterprise_match.group(1),
                "division": enterprise_match.group(2),
                "tier": int(enterprise_match.group(3)),
                "timestamp_hash": enterprise_match.group(4),
                "symbolic_char": enterprise_match.group(5),
                "entropy_hash": enterprise_match.group(6),
            }

        return {"is_commercial": False, "format": "unknown"}

    def _validate_commercial_specific(
        self, lambda_id: str, commercial_info: dict[str, Any], brand_prefix: BrandPrefix
    ) -> dict[str, Any]:
        """Perform commercial-specific validation checks."""
        checks = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "commercial_tier_match": False,
            "symbolic_char_authorized": False,
            "usage_within_limits": False,
        }

        # Check commercial tier consistency
        expected_symbols = self.commercial_symbols.get(brand_prefix.commercial_tier, [])
        if commercial_info["symbolic_char"] in expected_symbols:
            checks["symbolic_char_authorized"] = True
        else:
            checks["errors"].append("Symbolic character not authorized for commercial tier")
            checks["valid"] = False

        # Check usage limits
        tier_config = self.config["commercial_tiers"][brand_prefix.commercial_tier.value]
        current_usage = brand_prefix.usage_stats["lambda_ids_generated"]
        if current_usage < tier_config["max_lambda_ids"]:
            checks["usage_within_limits"] = True
        else:
            checks["warnings"].append("Usage approaching tier limits")

        # Commercial tier format validation
        if (commercial_info["format"] == "business" and brand_prefix.commercial_tier == CommercialTier.BUSINESS) or (
            commercial_info["format"] == "enterprise" and brand_prefix.commercial_tier == CommercialTier.ENTERPRISE
        ):
            checks["commercial_tier_match"] = True
        else:
            checks["errors"].append("Commercial format doesn't match registered tier")
            checks["valid"] = False

        return checks

    def get_brand_analytics(self, brand_code: str) -> dict[str, Any]:
        """Get analytics and usage statistics for a brand prefix."""
        if brand_code not in self.registered_brands:
            return {"success": False, "error": "Brand prefix not found"}

        brand = self.registered_brands[brand_code]
        usage_data = self.usage_tracking.get(brand_code, {})

        return {
            "success": True,
            "brand_code": brand_code,
            "company_name": brand.company_name,
            "commercial_tier": brand.commercial_tier.value,
            "status": brand.status.value,
            "registration_date": brand.registration_date.isoformat(),
            "expiry_date": brand.expiry_date.isoformat(),
            "usage_stats": {
                "total_generated": brand.usage_stats["lambda_ids_generated"],
                "last_used": (brand.usage_stats["last_used"].isoformat() if brand.usage_stats["last_used"] else None),
                "daily_usage": usage_data,
            },
            "tier_limits": self.config["commercial_tiers"][brand.commercial_tier.value],
            "remaining_quota": (
                self.config["commercial_tiers"][brand.commercial_tier.value]["max_lambda_ids"]
                - brand.usage_stats["lambda_ids_generated"]
            ),
        }

    def list_commercial_tiers(self) -> dict[str, Any]:
        """List available commercial tiers and their features."""
        return {
            "success": True,
            "commercial_tiers": self.config["commercial_tiers"],
            "symbolic_characters": {tier.value: symbols for tier, symbols in self.commercial_symbols.items()},
            "features_comparison": {
                "business": {
                    "branded_prefixes": True,
                    "enhanced_tier": "+1 tier boost",
                    "exclusive_symbols": True,
                    "division_support": False,
                    "white_labeling": False,
                },
                "enterprise": {
                    "branded_prefixes": True,
                    "enhanced_tier": "+2 tier boost",
                    "exclusive_symbols": True,
                    "division_support": True,
                    "white_labeling": False,
                },
                "corporate": {
                    "branded_prefixes": True,
                    "enhanced_tier": "+2 tier boost",
                    "exclusive_symbols": True,
                    "division_support": True,
                    "white_labeling": False,
                    "enhanced_security": True,
                },
                "white_label": {
                    "branded_prefixes": True,
                    "enhanced_tier": "+1 tier boost",
                    "exclusive_symbols": True,
                    "division_support": False,
                    "white_labeling": True,
                    "custom_prefix": True,
                },
            },
        }
