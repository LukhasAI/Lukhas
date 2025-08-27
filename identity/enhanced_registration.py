"""
Enhanced LUKHAS Identity Registration System
===========================================
Supports custom user IDs, username validation, and improved user experience.
Maintains backward compatibility with existing email-based ID generation.
"""

import re
from datetime import datetime, timezone
from typing import Any, Optional

from .identity_core import AccessTier, identity_core


class UserIDValidator:
    """Validates and suggests user IDs for registration."""

    # Reserved usernames that cannot be used
    RESERVED_USERNAMES = {
        'admin', 'root', 'system', 'api', 'www', 'mail', 'ftp',
        'test', 'guest', 'anonymous', 'user', 'support', 'help',
        'lukhas', 'lambda', 'trinity', 'guardian', 'consciousness',
        'quantum', 'dream', 'emotion', 'governance'
    }

    def validate_user_id(self, user_id: str) -> tuple[bool, str, list[str]]:
        """
        Validate a proposed user ID.

        Returns:
            (is_valid, error_message, suggestions)
        """
        suggestions = []

        # Length validation
        if len(user_id) < 3:
            return False, "User ID must be at least 3 characters long", []

        if len(user_id) > 30:
            return False, "User ID must be 30 characters or less", []

        # Character validation
        if not re.match(r'^[a-zA-Z0-9_-]+$', user_id):
            return False, "User ID can only contain letters, numbers, underscore, and hyphen", []

        # Must start with letter
        if not user_id[0].isalpha():
            return False, "User ID must start with a letter", []

        # Reserved username check
        if user_id.lower() in self.RESERVED_USERNAMES:
            suggestions = self._generate_suggestions(user_id)
            return False, f"'{user_id}' is reserved. Try one of the suggestions.", suggestions

        # Check for inappropriate patterns
        inappropriate_patterns = [
            r'admin', r'root', r'password', r'123+', r'test+',
            r'fuck', r'shit', r'damn', r'hell'  # Basic profanity filter
        ]

        for pattern in inappropriate_patterns:
            if re.search(pattern, user_id.lower()):
                return False, "User ID contains inappropriate content", []

        # Availability check (simulated - in production would check database)
        if self._is_user_id_taken(user_id):
            suggestions = self._generate_suggestions(user_id)
            return False, f"User ID '{user_id}' is already taken", suggestions

        return True, "User ID is valid and available", []

    def _is_user_id_taken(self, user_id: str) -> bool:
        """Check if user ID is already taken (mock implementation)."""
        # In production, this would query the user database
        # For now, simulate some taken usernames
        taken_usernames = {'john', 'alice', 'test123', 'demo_user'}
        return user_id.lower() in taken_usernames

    def _generate_suggestions(self, base_user_id: str) -> list[str]:
        """Generate alternative user ID suggestions."""
        suggestions = []
        base = base_user_id.lower()

        # Add numbers
        for i in range(1, 4):
            suggestions.append(f"{base}{i}")

        # Add year
        current_year = datetime.now().year
        suggestions.append(f"{base}{current_year}")

        # Add random suffix
        import random
        for _ in range(2):
            suffix = random.randint(10, 99)
            suggestions.append(f"{base}_{suffix}")

        # Filter out any that might also be taken
        return suggestions[:5]  # Return top 5 suggestions

    def generate_from_email(self, email: str) -> str:
        """Generate user ID from email (backward compatibility)."""
        return email.split("@")[0].replace(".", "_").lower()

    def suggest_from_email(self, email: str) -> list[str]:
        """Generate suggestions based on email."""
        base = self.generate_from_email(email)
        name_part = email.split("@")[0]

        suggestions = [base]

        # Try removing dots instead of replacing with underscore
        if "." in name_part:
            suggestions.append(name_part.replace(".", "").lower())

        # Try first name only if email has multiple parts
        if "." in name_part:
            first_name = name_part.split(".")[0].lower()
            if len(first_name) >= 3:
                suggestions.append(first_name)

        # Add variations
        suggestions.extend(self._generate_suggestions(base))

        return list(dict.fromkeys(suggestions))  # Remove duplicates while preserving order


class EnhancedRegistrationSystem:
    """Enhanced registration with custom user ID support."""

    def __init__(self):
        self.validator = UserIDValidator()

    def register_user_enhanced(
        self,
        email: str,
        password: str,
        requested_tier: Optional[str] = None,
        custom_user_id: Optional[str] = None,
        display_name: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Enhanced user registration with custom user ID support.

        Args:
            email: User's email address (required)
            password: User's password (required)
            requested_tier: Desired tier (T1-T5)
            custom_user_id: Optional custom user ID
            display_name: Optional display name for UI

        Returns:
            Registration result with user_id, token, and metadata
        """

        # Validate email
        if not self._validate_email(email):
            return {
                "success": False,
                "error": "Invalid email format",
                "suggestions": []
            }

        # Determine user ID
        if custom_user_id:
            # Validate custom user ID
            is_valid, error_msg, suggestions = self.validator.validate_user_id(custom_user_id)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "suggestions": suggestions,
                    "fallback_user_id": self.validator.generate_from_email(email)
                }
            user_id = custom_user_id.lower()
        else:
            # Generate from email (backward compatibility)
            user_id = self.validator.generate_from_email(email)

        # Determine tier
        tier_map = {
            "T1": AccessTier.T1,
            "T2": AccessTier.T2,
            "T3": AccessTier.T3,
            "T4": AccessTier.T4,
            "T5": AccessTier.T5,
        }
        tier = tier_map.get(requested_tier, AccessTier.T2)

        # Create enhanced metadata
        metadata = {
            "email": email,
            "user_id": user_id,
            "display_name": display_name or user_id,
            "custom_id_chosen": custom_user_id is not None,
            "consent": True,
            "trinity_score": 0.3,
            "drift_score": 0.0,
            "cultural_profile": "universal",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "registration_method": "enhanced",
            "id_source": "custom" if custom_user_id else "email_derived"
        }

        # Create token and glyphs
        token = identity_core.create_token(user_id, tier, metadata)
        glyphs = identity_core.generate_identity_glyph(user_id)

        return {
            "success": True,
            "user_id": user_id,
            "display_name": metadata["display_name"],
            "token": token,
            "tier": tier.value,
            "glyphs": glyphs,
            "message": f"User registered successfully with tier {tier.value}",
            "custom_id_used": custom_user_id is not None,
            "email": email
        }

    def check_user_id_availability(self, user_id: str) -> dict[str, Any]:
        """Check if a user ID is available and get suggestions."""
        is_valid, error_msg, suggestions = self.validator.validate_user_id(user_id)

        return {
            "user_id": user_id,
            "available": is_valid,
            "message": error_msg if not is_valid else "User ID is available",
            "suggestions": suggestions
        }

    def get_user_id_suggestions(self, email: str) -> dict[str, Any]:
        """Get user ID suggestions based on email."""
        suggestions = self.validator.suggest_from_email(email)

        return {
            "email": email,
            "suggestions": suggestions,
            "default": suggestions[0] if suggestions else None,
            "message": f"Generated {len(suggestions)} suggestions from email"
        }

    def _validate_email(self, email: str) -> bool:
        """Basic email validation."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None


# Global instance for backward compatibility
enhanced_registration = EnhancedRegistrationSystem()


# Enhanced API functions
def register_user_with_custom_id(
    email: str,
    password: str,
    custom_user_id: str,
    requested_tier: Optional[str] = None,
    display_name: Optional[str] = None
) -> dict[str, Any]:
    """Register user with custom user ID."""
    return enhanced_registration.register_user_enhanced(
        email=email,
        password=password,
        requested_tier=requested_tier,
        custom_user_id=custom_user_id,
        display_name=display_name
    )


def check_username_availability(user_id: str) -> dict[str, Any]:
    """Check if username is available."""
    return enhanced_registration.check_user_id_availability(user_id)


def get_username_suggestions(email: str) -> dict[str, Any]:
    """Get username suggestions from email."""
    return enhanced_registration.get_user_id_suggestions(email)


# Backward compatibility wrapper
def register_user(
    email: str, password: str, requested_tier: Optional[str] = None
) -> dict[str, Any]:
    """Legacy registration function with enhanced features."""
    return enhanced_registration.register_user_enhanced(
        email=email,
        password=password,
        requested_tier=requested_tier,
        custom_user_id=None  # Use email-derived ID
    )
