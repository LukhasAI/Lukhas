#!/usr/bin/env python3
"""
════════════════════════════════════════════════════════════════════════════════
║ 🧠 LUKHAS AI - USER TIER MAPPING SERVICE
║ Maps ΛID (Lambda ID) to tier levels for access control
║ Copyright (c) 2025 LUKHAS AI. All rights reserved.
╠═══════════════════════════════════════════════════════════════════════════════
║ Module: user_tier_mapping.py
║ Path: lukhas/identity/core/user_tier_mapping.py
║ Version: 1.0.0 | Created: 2025-07-26 | Modified: 2025-07-26
║ Authors: LUKHAS AI Identity Team
╠═══════════════════════════════════════════════════════════════════════════════
║ DESCRIPTION
╠═══════════════════════════════════════════════════════════════════════════════
║ This module provides a proper mapping between ΛID (user_id) and tier levels,
║ replacing the simplistic prefix-based approach with a robust database-backed
║ system that tracks user tiers, permissions, and access history.
╚═══════════════════════════════════════════════════════════════════════════════
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

# Database file for persistent storage (would be actual DB in production)
TIER_DB_PATH = os.environ.get("LUKHAS_TIER_DB", "/tmp/lukhas_user_tiers.json")


class LambdaTier(Enum):
    """LUKHAS Lambda Tier Levels for Access Control"""

    LAMBDA_TIER_0 = (0, "PUBLIC", "Basic public access")
    LAMBDA_TIER_1 = (1, "AUTHENTICATED", "Standard authenticated user")
    LAMBDA_TIER_2 = (2, "ELEVATED", "Elevated permissions for advanced features")
    LAMBDA_TIER_3 = (3, "PRIVILEGED", "Privileged access for premium features")
    LAMBDA_TIER_4 = (4, "ADMIN", "Administrative access")
    LAMBDA_TIER_5 = (5, "SYSTEM", "System-level access")

    def __init__(self, level: int, name: str, description: str):
        self.level = level
        self.tier_name = name
        self.description = description

    @classmethod
    def from_string(cls, tier_str: str) -> "LambdaTier":
        """Convert string like 'LAMBDA_TIER_2' to enum."""
        try:
            return cls[tier_str]
        except KeyError:
            # Try to parse from name
            for tier in cls:
                if tier.tier_name == tier_str:
                    return tier
            return cls.LAMBDA_TIER_0  # Default to public


@dataclass
class UserTierProfile:
    """Complete tier profile for a user"""

    lambda_id: str  # The ΛID
    current_tier: LambdaTier
    tier_history: list[dict[str, Any]]  # Track tier changes
    permissions: dict[str, bool]  # Specific permissions
    metadata: dict[str, Any]  # Additional user metadata
    created_at: datetime
    updated_at: datetime
    tier_expiry: Optional[datetime] = None  # For temporary tier elevations

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "lambda_id": self.lambda_id,
            "current_tier": self.current_tier.name,
            "tier_level": self.current_tier.level,
            "tier_history": self.tier_history,
            "permissions": self.permissions,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tier_expiry": self.tier_expiry.isoformat() if self.tier_expiry else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UserTierProfile":
        """Create from dictionary."""
        return cls(
            lambda_id=data["lambda_id"],
            current_tier=LambdaTier.from_string(data["current_tier"]),
            tier_history=data.get("tier_history", []),
            permissions=data.get("permissions", {}),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            tier_expiry=(
                datetime.fromisoformat(data["tier_expiry"])
                if data.get("tier_expiry")
                else None
            ),
        )


class UserTierMappingService:
    """
    Service for managing the mapping between ΛID and tier levels.

    This replaces the simplistic prefix-based approach with a proper
    database-backed system that can handle:
    - Persistent tier assignments
    - Temporary tier elevations
    - Tier history tracking
    - Permission overrides
    - Metadata storage
    """

    def __init__(self, db_path: str = TIER_DB_PATH):
        self.db_path = db_path
        self.cache: dict[str, UserTierProfile] = {}
        self._load_database()

    def _load_database(self):
        """Load tier mappings from persistent storage."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path) as f:
                    data = json.load(f)
                    for lambda_id, profile_data in data.items():
                        self.cache[lambda_id] = UserTierProfile.from_dict(profile_data)
                logger.info(f"Loaded {len(self.cache)} user tier profiles")
            except Exception as e:
                logger.error(f"Failed to load tier database: {e}")
                self.cache = {}
        else:
            logger.info("No existing tier database found, starting fresh")
            self._initialize_default_users()

    def _save_database(self):
        """Save tier mappings to persistent storage."""
        try:
            data = {lid: profile.to_dict() for lid, profile in self.cache.items()}
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            with open(self.db_path, "w") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Saved {len(data)} user tier profiles")
        except Exception as e:
            logger.error(f"Failed to save tier database: {e}")

    def _initialize_default_users(self):
        """Initialize some default users for testing."""
        now = datetime.now(timezone.utc)

        # System users
        self.cache["system_root"] = UserTierProfile(
            lambda_id="system_root",
            current_tier=LambdaTier.LAMBDA_TIER_5,
            tier_history=[
                {
                    "tier": "LAMBDA_TIER_5",
                    "timestamp": now.isoformat(),
                    "reason": "System initialization",
                }
            ],
            permissions={"*": True},  # All permissions
            metadata={"type": "system", "description": "Root system user"},
            created_at=now,
            updated_at=now,
        )

        # Admin users
        self.cache["admin_001"] = UserTierProfile(
            lambda_id="admin_001",
            current_tier=LambdaTier.LAMBDA_TIER_4,
            tier_history=[
                {
                    "tier": "LAMBDA_TIER_4",
                    "timestamp": now.isoformat(),
                    "reason": "Admin account",
                }
            ],
            permissions={"admin": True, "user_management": True, "system_config": True},
            metadata={"type": "admin", "name": "Primary Administrator"},
            created_at=now,
            updated_at=now,
        )

        # Test users with different tiers
        test_users = [
            (
                "test_user_tier0",
                LambdaTier.LAMBDA_TIER_0,
                {"type": "test", "name": "Public Test User"},
            ),
            (
                "test_user_tier1",
                LambdaTier.LAMBDA_TIER_1,
                {"type": "test", "name": "Basic Test User"},
            ),
            (
                "test_user_tier2",
                LambdaTier.LAMBDA_TIER_2,
                {"type": "test", "name": "Elevated Test User"},
            ),
            (
                "test_user_tier3",
                LambdaTier.LAMBDA_TIER_3,
                {"type": "test", "name": "Privileged Test User"},
            ),
        ]

        for lambda_id, tier, metadata in test_users:
            self.cache[lambda_id] = UserTierProfile(
                lambda_id=lambda_id,
                current_tier=tier,
                tier_history=[
                    {
                        "tier": tier.name,
                        "timestamp": now.isoformat(),
                        "reason": "Test account",
                    }
                ],
                permissions=self._get_default_permissions(tier),
                metadata=metadata,
                created_at=now,
                updated_at=now,
            )

        self._save_database()

    def _get_default_permissions(self, tier: LambdaTier) -> dict[str, bool]:
        """Get default permissions for a tier level."""
        permissions = {
            "read_public": True,
            "read_personal": tier.level >= 1,
            "write_personal": tier.level >= 1,
            "memory_access": tier.level >= 2,
            "memory_write": tier.level >= 2,
            "dream_generation": tier.level >= 3,
            "consciousness_access": tier.level >= 3,
            "quantum_access": tier.level >= 4,
            "admin_access": tier.level >= 4,
            "system_access": tier.level >= 5,
        }
        return permissions

    def get_user_tier(self, lambda_id: str) -> LambdaTier:
        """
        Get the current tier for a ΛID.

        Args:
            lambda_id: The user's Lambda ID

        Returns:
            LambdaTier: The user's current tier level
        """
        # Check cache first
        if lambda_id in self.cache:
            profile = self.cache[lambda_id]

            # Check if tier has expired
            if profile.tier_expiry and datetime.now(timezone.utc) > profile.tier_expiry:
                logger.info(f"Tier expired for {lambda_id}, reverting to base tier")
                self._revert_to_base_tier(lambda_id)

            return profile.current_tier

        # Not in cache - check for special prefixes (backward compatibility)
        if lambda_id.startswith("system_"):
            return LambdaTier.LAMBDA_TIER_5
        elif lambda_id.startswith("admin_"):
            return LambdaTier.LAMBDA_TIER_4
        elif lambda_id.startswith("test_user_tier"):
            # Extract tier number from test user ID
            try:
                tier_num = int(lambda_id.split("tier")[1][0])
                return list(LambdaTier)[tier_num]
            except BaseException:
                pass

        # Default for authenticated users
        if lambda_id and lambda_id != "anonymous":
            return LambdaTier.LAMBDA_TIER_1

        # Default to public
        return LambdaTier.LAMBDA_TIER_0

    def set_user_tier(
        self,
        lambda_id: str,
        tier: LambdaTier,
        reason: str,
        duration_minutes: Optional[int] = None,
    ) -> bool:
        """
        Set or update a user's tier level.

        Args:
            lambda_id: The user's Lambda ID
            tier: The new tier level
            reason: Reason for the tier change
            duration_minutes: Optional duration for temporary elevation

        Returns:
            bool: True if successful
        """
        now = datetime.now(timezone.utc)

        if lambda_id in self.cache:
            profile = self.cache[lambda_id]
            old_tier = profile.current_tier

            # Update tier
            profile.current_tier = tier
            profile.updated_at = now

            # Add to history
            profile.tier_history.append(
                {
                    "from_tier": old_tier.name,
                    "to_tier": tier.name,
                    "timestamp": now.isoformat(),
                    "reason": reason,
                    "temporary": duration_minutes is not None,
                }
            )

            # Set expiry if temporary
            if duration_minutes:
                profile.tier_expiry = now + timedelta(minutes=duration_minutes)
            else:
                profile.tier_expiry = None

            # Update permissions
            profile.permissions.update(self._get_default_permissions(tier))

        else:
            # Create new profile
            profile = UserTierProfile(
                lambda_id=lambda_id,
                current_tier=tier,
                tier_history=[
                    {"tier": tier.name, "timestamp": now.isoformat(), "reason": reason}
                ],
                permissions=self._get_default_permissions(tier),
                metadata={},
                created_at=now,
                updated_at=now,
                tier_expiry=(
                    now + timedelta(minutes=duration_minutes)
                    if duration_minutes
                    else None
                ),
            )
            self.cache[lambda_id] = profile

        self._save_database()

        logger.info(
            f"Set tier for {lambda_id} to {tier.name}",
            temporary=duration_minutes is not None,
            duration_minutes=duration_minutes,
        )

        return True

    def _revert_to_base_tier(self, lambda_id: str):
        """Revert user to their base tier after temporary elevation expires."""
        if lambda_id not in self.cache:
            return

        profile = self.cache[lambda_id]

        # Find the last non-temporary tier from history
        base_tier = LambdaTier.LAMBDA_TIER_1  # Default
        for entry in reversed(profile.tier_history):
            if not entry.get("temporary", False):
                base_tier = LambdaTier.from_string(
                    entry.get("to_tier", entry.get("tier"))
                )
                break

        profile.current_tier = base_tier
        profile.tier_expiry = None
        profile.updated_at = datetime.now(timezone.utc)
        profile.permissions = self._get_default_permissions(base_tier)

        self._save_database()

    def check_permission(self, lambda_id: str, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            lambda_id: The user's Lambda ID
            permission: The permission to check

        Returns:
            bool: True if user has the permission
        """
        if lambda_id in self.cache:
            profile = self.cache[lambda_id]
            # Check for wildcard permission (system users)
            if profile.permissions.get("*", False):
                return True
            return profile.permissions.get(permission, False)

        # Use tier-based defaults
        tier = self.get_user_tier(lambda_id)
        default_perms = self._get_default_permissions(tier)
        return default_perms.get(permission, False)

    def get_user_profile(self, lambda_id: str) -> Optional[dict[str, Any]]:
        """Get complete user profile including tier and permissions."""
        if lambda_id in self.cache:
            return self.cache[lambda_id].to_dict()

        # Create temporary profile for unknown users
        tier = self.get_user_tier(lambda_id)
        return {
            "lambda_id": lambda_id,
            "current_tier": tier.name,
            "tier_level": tier.level,
            "permissions": self._get_default_permissions(tier),
            "temporary": True,
        }


# Global instance for easy access
_tier_mapping_service = None


def get_tier_mapping_service() -> UserTierMappingService:
    """Get or create the global tier mapping service."""
    global _tier_mapping_service
    if _tier_mapping_service is None:
        _tier_mapping_service = UserTierMappingService()
    return _tier_mapping_service


# Convenience functions
def get_user_tier(lambda_id: str) -> str:
    """Get tier name for a user."""
    service = get_tier_mapping_service()
    tier = service.get_user_tier(lambda_id)
    return tier.name


def check_tier_access(lambda_id: str, required_tier: str) -> bool:
    """Check if user meets the required tier level."""
    service = get_tier_mapping_service()
    user_tier = service.get_user_tier(lambda_id)
    required = LambdaTier.from_string(required_tier)
    return user_tier.level >= required.level


def elevate_user_tier(
    lambda_id: str, target_tier: str, reason: str, duration_minutes: int = 60
) -> bool:
    """Temporarily elevate a user's tier."""
    service = get_tier_mapping_service()
    tier = LambdaTier.from_string(target_tier)
    return service.set_user_tier(lambda_id, tier, reason, duration_minutes)


if __name__ == "__main__":
    # Test the service
    service = get_tier_mapping_service()

    # Test getting tiers
    print(f"system_root tier: {service.get_user_tier('system_root').name}")
    print(f"admin_001 tier: {service.get_user_tier('admin_001').name}")
    print(f"test_user_tier2 tier: {service.get_user_tier('test_user_tier2').name}")
    print(f"unknown_user tier: {service.get_user_tier('unknown_user').name}")

    # Test permissions
    print(
        f"\ntest_user_tier2 can access memory: {service.check_permission('test_user_tier2', 'memory_access')}"
    )
    print(
        f"test_user_tier2 can access quantum: {service.check_permission('test_user_tier2', 'quantum_access')}"
    )

    # Test tier elevation
    print("\nElevating test_user_tier2 to TIER_4 for 5 minutes...")
    service.set_user_tier(
        "test_user_tier2", LambdaTier.LAMBDA_TIER_4, "Testing elevation", 5
    )
    print(
        f"test_user_tier2 can now access quantum: {service.check_permission('test_user_tier2', 'quantum_access')}"
    )
