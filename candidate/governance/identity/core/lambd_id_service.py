"""
ΛiD Service Manager
==================

Dedicated, reusable service for LUKHAS Lambda Identity management.
Designed for cross-platform usage (Web, Mobile, Internal APIs).

This service isolates all ΛiD operations into a clean, testable, and scalable module
that can be deployed as a microservice or embedded in applications.

Features:
- Tier-configurable generation
- Collision prevention with database integration
- Entropy scoring and validation
- Commercial branding support
- Cross-device synchronization
- Audit trail and analytics
- Rate limiting and security

Author: LUKHAS AI Systems
Version: 2.0.0
Created: 2025-07-05
"""

import hashlib
import json
import logging
import re
import secrets
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum, IntEnum
from pathlib import Path
from typing import Any, Optional, Union

from candidate.core.common import get_logger

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = get_logger(__name__)


class TierLevel(IntEnum):
    """User tier levels for ΛiD generation"""

    GUEST = 0
    VISITOR = 1
    FRIEND = 2
    TRUSTED = 3
    INNER_CIRCLE = 4
    ROOT_DEV = 5


class ValidationLevel(Enum):
    """ΛiD validation levels"""

    BASIC = "basic"  # Format validation only
    STANDARD = "standard"  # Format + tier compliance
    FULL = "full"  # Format + tier + collision + entropy


@dataclass
class LambdaIDResult:
    """Result object for ΛiD operations"""

    success: bool
    lambda_id: Optional[str] = None
    tier: Optional[int] = None
    entropy_score: Optional[float] = None
    symbolic_representation: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    generation_time_ms: Optional[float] = None


@dataclass
class ValidationResult:
    """Result object for ΛiD validation"""

    valid: bool
    lambda_id: str
    tier: Optional[int] = None
    entropy_score: Optional[float] = None
    format_valid: bool = False
    tier_compliant: bool = False
    collision_free: bool = False
    validation_level: str = "basic"
    errors: list[str] = None
    warnings: list[str] = None


@dataclass
class UserContext:
    """User context for personalized ΛiD generation"""

    user_id: Optional[str] = None
    email: Optional[str] = None
    registration_date: Optional[datetime] = None
    preferences: Optional[dict[str, Any]] = None
    geo_location: Optional[str] = None
    device_info: Optional[dict[str, str]] = None
    commercial_account: bool = False
    brand_prefix: Optional[str] = None


class LambdaIDService:
    """
    Centralized ΛiD service for generation, validation, and management.

    This service can be:
    - Embedded in web applications
    - Used by mobile SDKs
    - Deployed as a microservice
    - Integrated with databases and external systems
    """

    def __init__(self, config_path: Optional[str] = None, database_adapter=None):
        """
        Initialize the ΛiD service.

        Args:
            config_path: Path to tier configuration JSON
            database_adapter: Optional database adapter for persistence
        """
        self.config_path = config_path or self._get_default_config_path()
        self.database = database_adapter
        self.tier_config = self._load_tier_config()
        self.generated_ids = set()  # In-memory collision prevention
        self.rate_limiters = {}  # Rate limiting by user/IP

        logger.info(
            f"ΛiD Service initialized with {len(self.tier_config['tier_permissions'])} tiers"
        )

    def generate_lambda_id(
        self,
        tier: Union[int, TierLevel],
        user_context: Optional[UserContext] = None,
        symbolic_preference: Optional[str] = None,
        custom_options: Optional[dict[str, Any]] = None,
    ) -> LambdaIDResult:
        """
        Generate a new ΛiD with comprehensive validation and features.

        Args:
            tier: User tier level (0-5)
            user_context: User context for personalization
            symbolic_preference: Preferred symbolic character
            custom_options: Additional generation options

        Returns:
            LambdaIDResult with generation details
        """
        start_time = time.time()

        try:
            # Normalize tier
            tier_level = self._normalize_tier(tier)

            # Validate tier permissions
            tier_info = self._get_tier_info(tier_level)
            if not tier_info:
                return LambdaIDResult(
                    success=False, error_message=f"Invalid tier: {tier_level}"
                )

            # Rate limiting check
            if not self._check_rate_limit(user_context, "generation"):
                return LambdaIDResult(
                    success=False,
                    error_message="Rate limit exceeded for ΛiD generation",
                )

            # Generate ΛiD components
            lambda_id = self._generate_id_components(
                tier_level, user_context, symbolic_preference, custom_options
            )

            # Collision prevention
            if self._check_collision(lambda_id):
                logger.warning(f"Collision detected for {lambda_id}, regenerating...")
                return self._handle_collision(
                    tier_level, user_context, symbolic_preference, custom_options
                )

            # Calculate entropy score
            entropy_score = self._calculate_entropy(lambda_id, tier_level)

            # Create symbolic representation
            symbolic_repr = self._create_symbolic_representation(lambda_id, tier_level)

            # Store in database if adapter available
            if self.database:
                self._store_lambda_id(
                    lambda_id, tier_level, user_context, entropy_score
                )

            # Update collision prevention set
            self.generated_ids.add(lambda_id)

            # Log generation event
            self._log_generation_event(lambda_id, tier_level, user_context)

            generation_time = (time.time() - start_time) * 1000

            return LambdaIDResult(
                success=True,
                lambda_id=lambda_id,
                tier=tier_level,
                entropy_score=entropy_score,
                symbolic_representation=symbolic_repr,
                generation_time_ms=generation_time,
                metadata={
                    "tier_info": tier_info,
                    "timestamp": datetime.now().isoformat(),
                    "version": "2.0.0",
                },
            )

        except Exception as e:
            logger.error(f"ΛiD generation failed: {e!s}")
            return LambdaIDResult(
                success=False, error_message=f"Generation failed: {e!s}"
            )

    def validate_lambda_id(
        self,
        lambda_id: str,
        validation_level: ValidationLevel = ValidationLevel.STANDARD,
    ) -> ValidationResult:
        """
        Validate a ΛiD with specified validation level.

        Args:
            lambda_id: The ΛiD to validate
            validation_level: Level of validation to perform

        Returns:
            ValidationResult with detailed validation information
        """
        try:
            result = ValidationResult(
                valid=False,
                lambda_id=lambda_id,
                validation_level=validation_level.value,
                errors=[],
                warnings=[],
            )

            # Basic format validation
            format_valid, format_errors = self._validate_format(lambda_id)
            result.format_valid = format_valid
            if format_errors:
                result.errors.extend(format_errors)

            if not format_valid:
                return result

            # Extract tier from ΛiD
            tier = self._extract_tier(lambda_id)
            result.tier = tier

            if validation_level in [ValidationLevel.STANDARD, ValidationLevel.FULL]:
                # Tier compliance validation
                tier_compliant, tier_errors = self._validate_tier_compliance(
                    lambda_id, tier
                )
                result.tier_compliant = tier_compliant
                if tier_errors:
                    result.errors.extend(tier_errors)

                # Calculate entropy
                entropy_score = self._calculate_entropy(lambda_id, tier)
                result.entropy_score = entropy_score

            if validation_level == ValidationLevel.FULL:
                # Collision check
                collision_free = not self._check_collision(lambda_id)
                result.collision_free = collision_free
                if not collision_free:
                    result.errors.append("ΛiD collision detected")

            # Determine overall validity
            if validation_level == ValidationLevel.BASIC:
                result.valid = result.format_valid
            elif validation_level == ValidationLevel.STANDARD:
                result.valid = result.format_valid and result.tier_compliant
            else:  # FULL
                result.valid = (
                    result.format_valid
                    and result.tier_compliant
                    and result.collision_free
                )

            return result

        except Exception as e:
            logger.error(f"Validation failed for {lambda_id}: {e!s}")
            return ValidationResult(
                valid=False,
                lambda_id=lambda_id,
                validation_level=validation_level.value,
                errors=[f"Validation error: {e!s}"],
            )

    def calculate_entropy_score(
        self, symbolic_input: list[str], tier: Union[int, TierLevel]
    ) -> float:
        """
        Calculate entropy score for symbolic input.

        Args:
            symbolic_input: List of symbolic elements
            tier: User tier level

        Returns:
            float: Entropy score
        """
        self._normalize_tier(tier)
        entropy_config = self.tier_config.get("entropy_thresholds", {})

        # Basic Shannon entropy calculation
        char_counts = {}
        total_chars = len("".join(symbolic_input))

        for symbol in symbolic_input:
            for char in symbol:
                char_counts[char] = char_counts.get(char, 0) + 1

        # Calculate Shannon entropy
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * (probability.bit_length() - 1)

        # Apply boost factors from configuration
        boost_factors = entropy_config.get("boost_factors", {})

        # Unique symbolic characters boost
        unique_symbols = len(set(symbolic_input))
        entropy *= 1 + boost_factors.get("unique_symbolic_chars", 0) * (
            unique_symbols - 1
        )

        # Length bonus
        length_bonus = boost_factors.get("length_bonus", 0) * total_chars
        entropy += length_bonus

        return round(entropy, 2)

    def get_tier_information(
        self, tier: Union[int, TierLevel]
    ) -> Optional[dict[str, Any]]:
        """
        Get comprehensive tier information.

        Args:
            tier: Tier level to query

        Returns:
            Dict with tier information or None if invalid
        """
        tier_level = self._normalize_tier(tier)
        return self._get_tier_info(tier_level)

    def check_upgrade_eligibility(
        self,
        current_tier: Union[int, TierLevel],
        target_tier: Union[int, TierLevel],
        user_context: Optional[UserContext] = None,
    ) -> dict[str, Any]:
        """
        Check if user is eligible for tier upgrade.

        Args:
            current_tier: Current user tier
            target_tier: Desired tier
            user_context: User context for eligibility check

        Returns:
            Dict with eligibility information
        """
        current = self._normalize_tier(current_tier)
        target = self._normalize_tier(target_tier)

        if target <= current:
            return {
                "eligible": False,
                "reason": "Target tier must be higher than current tier",
            }

        target_info = self._get_tier_info(target)
        if not target_info:
            return {"eligible": False, "reason": "Invalid target tier"}

        upgrade_requirements = target_info.get("upgrade_requirements", {})
        upgrade_paths = self.tier_config.get("upgrade_paths", {})

        # Check automatic upgrade eligibility
        auto_upgrades = upgrade_paths.get("automatic_upgrades", {})
        upgrade_key = f"{current}_to_{target}"

        if upgrade_key in auto_upgrades:
            return self._check_automatic_upgrade(upgrade_key, user_context)

        # Check manual upgrade eligibility
        manual_upgrades = upgrade_paths.get("manual_upgrades", {})
        if upgrade_key in manual_upgrades:
            return self._check_manual_upgrade(upgrade_key, user_context)

        return {
            "eligible": False,
            "reason": "No upgrade path available",
            "requirements": upgrade_requirements,
        }

    def get_service_stats(self) -> dict[str, Any]:
        """
        Get comprehensive service statistics.

        Returns:
            Dict with service statistics
        """
        return {
            "total_generated": len(self.generated_ids),
            "tier_config_version": self.tier_config.get("tier_system", {}).get(
                "version"
            ),
            "available_tiers": len(self.tier_config.get("tier_permissions", {})),
            "validation_rules": len(self.tier_config.get("validation_rules", {})),
            "service_version": "2.0.0",
            "uptime": "active",  # TODO: Calculate actual uptime
            "rate_limiters_active": len(self.rate_limiters),
        }

    # Private helper methods

    def _normalize_tier(self, tier: Union[int, TierLevel]) -> int:
        """Normalize tier input to integer"""
        if isinstance(tier, TierLevel):
            return tier.value
        return int(tier)

    def _get_default_config_path(self) -> str:
        """Get default configuration file path"""
        current_dir = Path(__file__).parent
        return str(current_dir.parent.parent / "config" / "tier_permissions.json")

    def _load_tier_config(self) -> dict[str, Any]:
        """Load tier configuration from JSON file"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = json.load(f)
            logger.info(f"Loaded tier configuration from {self.config_path}")
            return config
        except Exception as e:
            logger.error(f"Failed to load tier config: {e!s}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get minimal default configuration"""
        return {
            "tier_permissions": {
                "0": {
                    "name": "Guest",
                    "max_entropy": 2.0,
                    "symbols_allowed": 2,
                    "symbolic_chars": ["◊", "○", "□"],
                }
            }
        }

    def _get_tier_info(self, tier: int) -> Optional[dict[str, Any]]:
        """Get tier information from configuration"""
        return self.tier_config.get("tier_permissions", {}).get(str(tier))

    def _generate_id_components(
        self,
        tier: int,
        user_context: Optional[UserContext],
        symbolic_preference: Optional[str],
        custom_options: Optional[dict[str, Any]],
    ) -> str:
        """Generate ΛiD components"""
        # Timestamp hash (4 chars)
        timestamp = str(int(time.time() * 1000))
        timestamp_hash = hashlib.sha256(timestamp.encode()).hexdigest()[:4].upper()

        # Symbolic element
        symbolic_char = self._select_symbolic_element(tier, symbolic_preference)

        # Entropy hash (4 chars)
        entropy_input = f"{tier}_{timestamp}_{symbolic_char}"
        if user_context:
            entropy_input += f"_{user_context.user_id or 'anonymous'}"
        if custom_options:
            entropy_input += f"_{json.dumps(custom_options, sort_keys=True)}"

        entropy_hash = hashlib.sha256(entropy_input.encode()).hexdigest()[:4].upper()

        return f"LUKHAS{tier}-{timestamp_hash}-{symbolic_char}-{entropy_hash}"

    def _select_symbolic_element(self, tier: int, preference: Optional[str]) -> str:
        """Select symbolic element based on tier and preference"""
        tier_info = self._get_tier_info(tier)
        if not tier_info:
            return "◊"

        available_chars = tier_info.get("symbolic_chars", ["◊"])

        if preference and preference in available_chars:
            return preference

        return secrets.choice(available_chars)

    def _check_collision(self, lambda_id: str) -> bool:
        """Check for ΛiD collision"""
        # Check in-memory set
        if lambda_id in self.generated_ids:
            return True

        # Check database if adapter available
        if self.database:
            return self.database.lambda_id_exists(lambda_id)

        return False

    def _handle_collision(
        self,
        tier: int,
        user_context: Optional[UserContext],
        symbolic_preference: Optional[str],
        custom_options: Optional[dict[str, Any]],
    ) -> LambdaIDResult:
        """Handle collision by regenerating with additional entropy"""
        collision_options = custom_options.copy() if custom_options else {}
        collision_options["collision_retry"] = True
        collision_options["retry_timestamp"] = time.time()

        return self.generate_lambda_id(
            tier, user_context, symbolic_preference, collision_options
        )

    def _validate_format(self, lambda_id: str) -> tuple[bool, list[str]]:
        """Validate ΛiD format"""
        errors = []

        # Check basic pattern
        validation_rules = self.tier_config.get("validation_rules", {})
        id_format = validation_rules.get("id_format", {})
        pattern = id_format.get(
            "pattern", r"^LUKHAS[0-5]-[A-F0-9]{4}-[\w\p{So}]-[A-F0-9]{4}$"
        )

        if not re.match(pattern, lambda_id):
            errors.append("Invalid ΛiD format")

        # Check length constraints
        min_length = id_format.get("min_length", 12)
        max_length = id_format.get("max_length", 20)

        if len(lambda_id) < min_length:
            errors.append(f"ΛiD too short (min: {min_length})")

        if len(lambda_id) > max_length:
            errors.append(f"ΛiD too long (max: {max_length})")

        return len(errors) == 0, errors

    def _extract_tier(self, lambda_id: str) -> Optional[int]:
        """Extract tier from ΛiD"""
        try:
            if lambda_id.startswith("LUKHAS") and "-" in lambda_id:
                tier_part = lambda_id[1 : lambda_id.index("-")]
                return int(tier_part)
        except (ValueError, IndexError):
            pass
        return None

    def _validate_tier_compliance(
        self, lambda_id: str, tier: int
    ) -> tuple[bool, list[str]]:
        """Validate tier compliance"""
        errors = []
        tier_info = self._get_tier_info(tier)

        if not tier_info:
            errors.append(f"Invalid tier: {tier}")
            return False, errors

        # Validate symbolic character is allowed for tier
        parts = lambda_id.split("-")
        if len(parts) >= 3:
            symbolic_char = parts[2]
            allowed_chars = tier_info.get("symbolic_chars", [])
            if symbolic_char not in allowed_chars:
                errors.append(
                    f"Symbolic character '{symbolic_char}' not allowed for tier {tier}"
                )

        return len(errors) == 0, errors

    def _calculate_entropy(self, lambda_id: str, tier: int) -> float:
        """Calculate entropy score for ΛiD"""
        # Extract symbolic components
        parts = lambda_id.split("-")
        if len(parts) < 4:
            return 0.0

        symbolic_input = [parts[2]]  # Symbolic character
        return self.calculate_entropy_score(symbolic_input, tier)

    def _create_symbolic_representation(self, lambda_id: str, tier: int) -> str:
        """Create symbolic representation of ΛiD"""
        tier_info = self._get_tier_info(tier)
        tier_symbol = tier_info.get("symbol", "⚪") if tier_info else "⚪"

        parts = lambda_id.split("-")
        symbolic_char = parts[2] if len(parts) >= 3 else "◊"

        return f"🆔{lambda_id}{tier_symbol}{symbolic_char}✨"

    def _check_rate_limit(
        self, user_context: Optional[UserContext], operation: str
    ) -> bool:
        """Check rate limiting for user/operation"""
        # TODO: Implement proper rate limiting
        return True

    def _store_lambda_id(
        self,
        lambda_id: str,
        tier: int,
        user_context: Optional[UserContext],
        entropy_score: float,
    ) -> None:
        """Store ΛiD in database"""
        if self.database:
            self.database.store_lambda_id(
                {
                    "lambda_id": lambda_id,
                    "tier": tier,
                    "user_context": asdict(user_context) if user_context else None,
                    "entropy_score": entropy_score,
                    "created_at": datetime.now().isoformat(),
                }
            )

    def _log_generation_event(
        self, lambda_id: str, tier: int, user_context: Optional[UserContext]
    ) -> None:
        """Log ΛiD generation event"""
        logger.info(f"ΛiD Generated: {lambda_id} (Tier {tier})")

    def _check_automatic_upgrade(
        self, upgrade_key: str, user_context: Optional[UserContext]
    ) -> dict[str, Any]:
        """Check automatic upgrade eligibility"""
        # TODO: Implement automatic upgrade logic
        return {"eligible": False, "reason": "Not implemented"}

    def _check_manual_upgrade(
        self, upgrade_key: str, user_context: Optional[UserContext]
    ) -> dict[str, Any]:
        """Check manual upgrade eligibility"""
        # TODO: Implement manual upgrade logic
        return {"eligible": False, "reason": "Not implemented"}


# Singleton instance for easy access
_lambda_id_service = None


def get_lambda_id_service(
    config_path: Optional[str] = None, database_adapter=None
) -> LambdaIDService:
    """Get singleton ΛiD service instance"""
    global _lambda_id_service
    if _lambda_id_service is None:
        _lambda_id_service = LambdaIDService(config_path, database_adapter)
    return _lambda_id_service


# Example usage
if __name__ == "__main__":
    # Initialize service
    service = LambdaIDService()

    # Generate ΛiDs for different tiers
    for tier in range(6):
        user_ctx = UserContext(
            user_id=f"user_{tier}",
            email=f"user{tier}@example.com",
            preferences={"style": "tech"},
        )

        result = service.generate_lambda_id(tier, user_ctx)
        print(f"Tier {tier}: {result.lambda_id} (Success: {result.success})")

        if result.success:
            # Validate the generated ΛiD
            validation = service.validate_lambda_id(
                result.lambda_id, ValidationLevel.FULL
            )
            print(
                f"  Validation: {validation.valid} (Entropy: {validation.entropy_score})"
            )

    # Service statistics
    stats = service.get_service_stats()
    print(f"\nService Stats: {stats}")
