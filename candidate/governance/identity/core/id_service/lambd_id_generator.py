"""Compatibility shim: re-export canonical generator implementation.

This shim keeps the legacy module path importable while the real
implementation lives in `lambda_id_generator.py` (canonical name).
"""

from .lambda_id_generator import LambdaIDGenerator

# Backwards-compatible alias
LambdIDGenerator = LambdaIDGenerator

__all__ = ["LambdIDGenerator", "LambdaIDGenerator"]
import hashlib
import json
import secrets
import time
from datetime import datetime
from enum import Enum
from typing import Optional


class UserContext:
    """User context for ID generation."""

    def __init__(self, user_id=None, metadata=None):
        self.user_id = user_id
        self.metadata = metadata or {}

    def to_dict(self):
        return {"user_id": self.user_id, "metadata": self.metadata}


"""
LUKHAS ΛiD Generator
===================

Core ΛiD generation logic with tier management, format handling, and hash generation.
Generates unique, symbolic, and tier-appropriate LUKHAS identities.

Features:
- Tier-based ID generation (0-5)
- Symbolic character integration
- Hash-based uniqueness
- Collision prevention
- Entropy scoring
- Format validation

Author: LUKHAS AI Systems
Created: 2025-07-05
"""


class TierLevel(Enum):
    """User tier levels for ΛiD generation"""

    GUEST = 0
    VISITOR = 1
    FRIEND = 2
    TRUSTED = 3
    INNER_CIRCLE = 4
    ROOT_DEV = 5


class LambdaIDGenerator:
    """
    Core ΛiD generation system with tier management and symbolic integration.

    Generates unique LUKHAS identities in the format:
    LUKHAS{tier}-{timestamp_hash}-{symbolic_element}-{entropy_hash}

    Examples:
    - Λ2-A9F3-🌀-X7K1 (Tier 2 Friend)
    - Λ5-B2E8-⟐-Z9M4 (Tier 5 Root/Dev)
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the ΛiD generator with configuration"""
        self.config = self._load_config(config_path)
        self.symbolic_chars = self._load_symbolic_chars()
        self.reserved_combinations = self._load_reserved_combinations()
        self.generated_ids = set()  # Collision prevention

    def generate_lambda_id(
        self,
        tier: TierLevel,
        user_context: Optional[dict] = None,
        symbolic_preference: Optional[str] = None,
    ) -> str:
        """
        Generate a new ΛiD with tier-appropriate characteristics.

        Args:
            tier: User tier level (0-5)
            user_context: Optional user context for personalization
            symbolic_preference: Optional symbolic character preference

        Returns:
            str: Generated ΛiD in format LUKHAS{tier}-{hash}-{symbol}-{entropy}
        """
        # Generate timestamp-based component
        timestamp_component = self._generate_timestamp_hash()

        # Select symbolic element based on tier and preference
        symbolic_element = self._select_symbolic_element(tier, symbolic_preference)

        # Generate entropy hash
        entropy_hash = self._generate_entropy_hash(tier, user_context)

        # Construct ΛiD
        lambda_id = f"LUKHAS{tier.value}-{timestamp_component}-{symbolic_element}-{entropy_hash}"

        # Validate uniqueness
        if lambda_id in self.generated_ids:
            return self._handle_collision(tier, user_context, symbolic_preference)

        self.generated_ids.add(lambda_id)

        # Log generation event
        self._log_generation(lambda_id, tier, user_context)

        return lambda_id

    def _generate_timestamp_hash(self) -> str:
        """Generate 4-character timestamp-based hash"""
        timestamp = str(int(time.time() * 1000))  # Millisecond precision
        hash_obj = hashlib.sha256(timestamp.encode())
        return hash_obj.hexdigest()[:4].upper()

    def _select_symbolic_element(self, tier: TierLevel, preference: Optional[str] = None) -> str:
        """
        Select appropriate symbolic character based on tier and preference.

        Higher tiers get access to more complex symbolic characters.
        """
        tier_symbols = self.symbolic_chars.get(f"tier_{tier.value}", [])

        if preference and preference in tier_symbols:
            return preference

        # Random selection from tier-appropriate symbols
        return secrets.choice(tier_symbols) if tier_symbols else "◊"

    def _generate_entropy_hash(self, tier: TierLevel, user_context: Optional[dict] = None) -> str:
        """Generate 4-character entropy hash with tier-specific complexity"""
        # Base entropy from secure random
        base_entropy = secrets.token_hex(16)

        # Add user context if available
        if user_context:
            context_str = json.dumps(user_context, sort_keys=True)
            base_entropy += context_str

        # Add tier-specific salt
        tier_salt = f"tier_{tier.value}_{datetime.now(timezone.utc).isoformat(}"
        combined_entropy = base_entropy + tier_salt

        # Generate hash
        hash_obj = hashlib.sha256(combined_entropy.encode())
        return hash_obj.hexdigest()[:4].upper()

    def _handle_collision(
        self,
        tier: TierLevel,
        user_context: Optional[dict] = None,
        symbolic_preference: Optional[str] = None,
    ) -> str:
        """Handle ΛiD collision by regenerating with additional entropy"""
        # Add collision counter to context
        collision_context = user_context.copy() if user_context else {}
        collision_context["collision_retry"] = True
        collision_context["retry_timestamp"] = time.time()

        return self.generate_lambda_id(tier, collision_context, symbolic_preference)

    def _load_config(self, config_path: Optional[str] = None) -> dict:
        """Load ΛiD generation configuration"""
        # TODO: Load from actual config file
        return {
            "id_length": 4,
            "max_retries": 5,
            "symbolic_enabled": True,
            "tier_restrictions": True,
        }

    def _load_symbolic_chars(self) -> dict[str, list[str]]:
        """Load tier-appropriate symbolic characters"""
        return {
            "tier_0": ["◊", "○", "□"],  # Basic shapes for guests
            "tier_1": ["◊", "○", "□", "△", "▽"],  # Additional basic shapes
            "tier_2": ["🌀", "✨", "🔮", "◊", "⟐"],  # Mystical symbols
            "tier_3": ["🌀", "✨", "🔮", "⟐", "◈", "⬟"],  # Advanced symbols
            "tier_4": ["⟐", "◈", "⬟", "⬢", "⟁", "◐"],  # Complex geometrics
            "tier_5": ["⟐", "◈", "⬟", "⬢", "⟁", "◐", "◑", "⬧"],  # Full symbolic set
        }

    def _load_reserved_combinations(self) -> list[str]:
        """Load reserved ΛiD combinations that should not be generated"""
        return [
            "Λ0-0000-○-0000",  # Reserved system ID
            "Λ5-FFFF-⟐-FFFF",  # Reserved admin ID
            # Add more reserved combinations
        ]

    def _log_generation(self, lambda_id: str, tier: TierLevel, user_context: Optional[dict] = None) -> None:
        """Log ΛiD generation event for audit trail"""
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lambda_id": lambda_id,
            "tier": tier.value,
            "context": user_context or {},
            "generator_version": "1.0.0",
        }

        # TODO: Implement actual logging to file/database
        print(f"ΛiD Generated: {lambda_id} (Tier {tier.value})")

    def get_generation_stats(self) -> dict:
        """Get statistics about generated ΛiDs"""
        return {
            "total_generated": len(self.generated_ids),
            "collision_rate": 0.0,  # TODO: Calculate actual collision rate
            "tier_distribution": {},  # TODO: Calculate tier distribution
            "symbolic_usage": {},  # TODO: Calculate symbolic character usage
        }


# Alias for compatibility
LambdIDGenerator = LambdaIDGenerator


# Validator class
class LambdIDValidator:
    """Lambda ID validator"""

    def __init__(self):
        pass

    def validate(self, lambda_id: str) -> bool:
        """Validate Lambda ID format"""
        if not lambda_id or not isinstance(lambda_id, str):
            return False

        parts = lambda_id.split("-")
        if len(parts) != 4:
            return False

        # Check format: LUKHAS{tier}-{hash}-{symbol}-{entropy}
        return parts[0].startswith("LUKHAS")


# Export main classes
__all__ = [
    "LambdIDGenerator",
    "LambdIDValidator",
    "LambdaIDGenerator",
    "TierLevel",
    "UserContext",
]

# Example usage and testing
if __name__ == "__main__":
    generator = LambdaIDGenerator()

    # Generate ΛiDs for different tiers
    for tier in TierLevel:
        lambda_id = generator.generate_lambda_id(tier)
        print(f"Tier {tier.value} ({tier.name}): {lambda_id}")

    # Generate with user context
    user_context = {
        "email": "user@example.com",
        "registration_time": time.time(),
        "preferences": {"symbolic_style": "mystical"},
    }

    personalized_id = generator.generate_lambda_id(TierLevel.FRIEND, user_context, symbolic_preference="🌀")
    print(f"Personalized ΛiD: {personalized_id}")

    print(f"Generation Stats: {generator.get_generation_stats(}")
