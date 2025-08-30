#!/usr/bin/env python3
"""
NIΛS User Data Integrator - Ethical data collection with granular opt-in
Part of the Lambda Products Suite by LUKHAS AI

This module handles user data integration from various sources with full
consent management and privacy protection.
"""

import asyncio
import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("Lambda.NIΛS.UserData")


class DataSource(Enum):
    """Available data sources for user integration"""

    EMAIL = "email"
    SHOPPING = "shopping"
    SOCIAL = "social"
    CALENDAR = "calendar"
    LOCATION = "location"
    PAYMENT = "payment"
    BROWSING = "browsing"
    HEALTH = "health"


class DataPermission(Enum):
    """Granular permission levels for data access"""

    NONE = "none"
    METADATA_ONLY = "metadata_only"  # Just categories, no details
    AGGREGATED = "aggregated"  # Statistical summaries
    ANONYMIZED = "anonymized"  # Details but anonymized
    FULL = "full"  # Complete access (requires T3+)


@dataclass
class UserDataPreferences:
    """User preferences for data sharing"""

    user_id: str
    data_sources: dict[DataSource, dict[str, Any]]
    privacy_settings: dict[str, Any]
    vendor_sharing: str  # none, aggregated_only, selected_vendors, all
    retention_days: int = 90
    anonymize_by_default: bool = True
    require_explicit_consent: bool = True
    last_updated: datetime = None

    def __post_init__(self):
        if self.last_updated is None:
            self.last_updated = datetime.now()


@dataclass
class UserDataProfile:
    """Aggregated user data profile from all sources"""

    user_id: str
    interests: list[str]
    shopping_patterns: dict[str, Any]
    emotional_preferences: dict[str, float]
    schedule_patterns: dict[str, Any]
    spending_categories: list[str]
    brand_affinities: dict[str, float]
    dream_symbols: list[str]
    data_completeness: float  # 0-1 score
    last_sync: datetime = None


class EmailIntegrator:
    """Integration with email providers for receipt and preference extraction"""

    def __init__(self):
        self.supported_providers = ["gmail", "outlook", "yahoo", "proton"]
        self.receipt_patterns = {
            "amazon": r"Order\s+#[\d\-]+",
            "receipt": r"(?i)(receipt|invoice|order\s+confirmation)",
            "tracking": r"(?i)(tracking\s+number|shipment)",
            "subscription": r"(?i)(subscription|renewal|billing)",
        }

    async def scan_receipts(
        self, email_access_token: str, provider: str, scan_depth_days: int = 30
    ) -> dict[str, Any]:
        """
        Scan email for shopping receipts and extract patterns

        Returns:
            Dictionary with shopping patterns and preferences
        """
        if provider not in self.supported_providers:
            logger.warning(f"Unsupported email provider: {provider}")
            return {}

        # Simulated email scanning - would connect to actual email API
        patterns = {
            "frequent_merchants": [],
            "product_categories": [],
            "avg_order_value": 0.0,
            "purchase_frequency": "weekly",
            "subscription_services": [],
            "preferred_brands": [],
        }

        # In production, would use provider APIs (Gmail API, Outlook Graph API, etc.)
        # For now, return sample data
        patterns["frequent_merchants"] = ["Amazon", "Whole Foods", "Nike"]
        patterns["product_categories"] = ["Electronics", "Groceries", "Fitness"]
        patterns["subscription_services"] = ["Netflix", "Spotify", "Adobe"]

        logger.info(
            f"Scanned emails for user, found {len(patterns['frequent_merchants'])} merchants"
        )
        return patterns

    def extract_preferences_from_newsletters(self, email_content: list[str]) -> list[str]:
        """Extract user interests from newsletter subscriptions"""
        interests = set()

        newsletter_categories = {
            "tech": ["techcrunch", "wired", "verge", "hackernews"],
            "fitness": ["runner", "fitness", "workout", "gym"],
            "finance": ["market", "invest", "crypto", "stock"],
            "cooking": ["recipe", "food", "cooking", "chef"],
            "travel": ["travel", "vacation", "destination", "hotel"],
        }

        for content in email_content:
            content_lower = content.lower()
            for category, keywords in newsletter_categories.items():
                if any(keyword in content_lower for keyword in keywords):
                    interests.add(category)

        return list(interests)


class ShoppingIntegrator:
    """Integration with e-commerce platforms"""

    def __init__(self):
        self.supported_platforms = ["amazon", "ebay", "shopify", "etsy", "walmart"]
        self.product_categories = {}

    async def get_shopping_history(
        self, platform: str, api_token: str, months_back: int = 6
    ) -> dict[str, Any]:
        """
        Retrieve shopping history from e-commerce platform

        Returns:
            Shopping patterns and preferences
        """
        if platform not in self.supported_platforms:
            return {}

        # Simulated API call - would use actual platform APIs
        history = {
            "total_orders": 42,
            "categories": {
                "Electronics": 0.3,
                "Books": 0.2,
                "Home & Garden": 0.15,
                "Clothing": 0.25,
                "Sports": 0.1,
            },
            "avg_order_value": 67.50,
            "preferred_shipping": "2-day",
            "wishlist_items": [],
            "cart_abandonment_rate": 0.15,
            "review_participation": 0.6,
            "brand_loyalty": {"Nike": 0.8, "Apple": 0.9, "Samsung": 0.3},
        }

        # Extract wish list for dream seed generation
        history["wishlist_items"] = [
            {"item": "Running Shoes", "category": "Sports", "price_range": "100-150"},
            {
                "item": "Smart Watch",
                "category": "Electronics",
                "price_range": "200-300",
            },
            {"item": "Yoga Mat", "category": "Fitness", "price_range": "30-50"},
        ]

        logger.info(f"Retrieved {history['total_orders']} orders from {platform}")
        return history

    async def get_browsing_patterns(self, platform: str, session_token: str) -> dict[str, Any]:
        """Get browsing patterns without purchase"""
        patterns = {
            "viewed_categories": [],
            "avg_session_duration": 0,
            "price_sensitivity": "medium",  # low, medium, high
            "comparison_shopping": False,
            "impulse_buyer_score": 0.0,
        }

        # Would integrate with platform analytics
        patterns["viewed_categories"] = ["Electronics", "Books", "Outdoor"]
        patterns["avg_session_duration"] = 12.5  # minutes
        patterns["comparison_shopping"] = True
        patterns["impulse_buyer_score"] = 0.3

        return patterns


class CalendarIntegrator:
    """Integration with calendar for schedule awareness"""

    async def get_schedule_patterns(self, calendar_token: str) -> dict[str, Any]:
        """Extract schedule patterns for optimal ad timing"""
        patterns = {
            "busy_hours": [],
            "free_slots": [],
            "recurring_events": [],
            "work_schedule": {},
            "personal_time": {},
            "optimal_engagement_times": [],
        }

        # Would integrate with Google Calendar, Outlook Calendar, etc.
        patterns["busy_hours"] = ["9-12", "14-17"]
        patterns["free_slots"] = ["12-13", "17-18", "20-22"]
        patterns["optimal_engagement_times"] = ["12:30", "18:00", "21:00"]

        return patterns


class UserDataIntegrator:
    """
    Main integrator class that orchestrates all data sources
    """

    def __init__(self, consent_manager):
        self.consent_manager = consent_manager
        self.email_integrator = EmailIntegrator()
        self.shopping_integrator = ShoppingIntegrator()
        self.calendar_integrator = CalendarIntegrator()
        self.user_profiles: dict[str, UserDataProfile] = {}
        self.data_preferences: dict[str, UserDataPreferences] = {}

        logger.info("NIΛS User Data Integrator initialized")

    async def setup_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> bool:
        """
        Setup user data sharing preferences

        Args:
            user_id: User identifier
            preferences: Dictionary with data source permissions

        Returns:
            True if preferences saved successfully
        """
        try:
            # Create preference object
            user_prefs = UserDataPreferences(
                user_id=user_id,
                data_sources=self._parse_data_sources(preferences.get("data_sources", {})),
                privacy_settings=preferences.get("privacy_settings", {}),
                vendor_sharing=preferences.get("vendor_sharing", "aggregated_only"),
                retention_days=preferences.get("retention_days", 90),
                anonymize_by_default=preferences.get("anonymize_by_default", True),
            )

            self.data_preferences[user_id] = user_prefs

            # Log consent for audit
            await self.consent_manager.grant_consent(
                user_id=user_id,
                scope="data_integration",
                level="enhanced",
                context={"preferences": asdict(user_prefs)},
            )

            logger.info(f"User preferences configured for {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error setting up user preferences: {e}")
            return False

    def _parse_data_sources(self, sources: dict) -> dict[DataSource, dict]:
        """Parse and validate data source permissions"""
        parsed = {}

        for source_str, config in sources.items():
            try:
                source = DataSource(source_str)
                parsed[source] = {
                    "enabled": config.get("enabled", False),
                    "permission": DataPermission(config.get("permission", "none")),
                    "providers": config.get("providers", []),
                    "sync_frequency": config.get("sync_frequency", "daily"),
                    "specific_permissions": config.get("specific_permissions", {}),
                }
            except ValueError:
                logger.warning(f"Unknown data source: {source_str}")

        return parsed

    async def sync_user_data(self, user_id: str, force_refresh: bool = False) -> UserDataProfile:
        """
        Sync all permitted user data sources

        Args:
            user_id: User identifier
            force_refresh: Force data refresh even if recently synced

        Returns:
            Updated user data profile
        """
        if user_id not in self.data_preferences:
            logger.warning(f"No preferences found for user {user_id}")
            return None

        prefs = self.data_preferences[user_id]
        profile = self.user_profiles.get(
            user_id,
            UserDataProfile(
                user_id=user_id,
                interests=[],
                shopping_patterns={},
                emotional_preferences={},
                schedule_patterns={},
                spending_categories=[],
                brand_affinities={},
                dream_symbols=[],
                data_completeness=0.0,
            ),
        )

        # Check if sync needed
        if not force_refresh and profile.last_sync:
            if datetime.now() - profile.last_sync < timedelta(hours=24):
                logger.info(f"Using cached profile for {user_id}")
                return profile

        data_points = 0

        # Sync email data if permitted
        if DataSource.EMAIL in prefs.data_sources:
            email_config = prefs.data_sources[DataSource.EMAIL]
            if email_config["enabled"]:
                for provider in email_config.get("providers", []):
                    # Would get actual tokens from secure storage
                    email_data = await self.email_integrator.scan_receipts("dummy_token", provider)
                    profile.shopping_patterns.update(email_data)
                    data_points += 1

        # Sync shopping data if permitted
        if DataSource.SHOPPING in prefs.data_sources:
            shopping_config = prefs.data_sources[DataSource.SHOPPING]
            if shopping_config["enabled"]:
                for platform in shopping_config.get("providers", []):
                    shopping_data = await self.shopping_integrator.get_shopping_history(
                        platform, "dummy_token"
                    )

                    # Update profile with shopping data
                    profile.spending_categories = list(shopping_data.get("categories", {}).keys())
                    profile.brand_affinities.update(shopping_data.get("brand_loyalty", {}))

                    # Generate dream symbols from wishlist
                    for item in shopping_data.get("wishlist_items", []):
                        profile.dream_symbols.append(self._item_to_symbol(item))

                    data_points += 1

        # Sync calendar data if permitted
        if DataSource.CALENDAR in prefs.data_sources:
            calendar_config = prefs.data_sources[DataSource.CALENDAR]
            if calendar_config["enabled"]:
                schedule_data = await self.calendar_integrator.get_schedule_patterns("dummy_token")
                profile.schedule_patterns = schedule_data
                data_points += 1

        # Calculate data completeness
        total_sources = len(DataSource)
        profile.data_completeness = data_points / total_sources
        profile.last_sync = datetime.now()

        # Anonymize if required
        if prefs.anonymize_by_default:
            profile = self._anonymize_profile(profile)

        self.user_profiles[user_id] = profile
        logger.info(
            f"Synced user data for {user_id}, completeness: {profile.data_completeness:.1%}"
        )

        return profile

    def _item_to_symbol(self, item: dict) -> str:
        """Convert wishlist item to dream symbol"""
        category_symbols = {
            "Sports": "🏃",
            "Electronics": "📱",
            "Fitness": "💪",
            "Books": "📚",
            "Home": "🏠",
            "Fashion": "👕",
            "Food": "🍽️",
        }

        category = item.get("category", "")
        return category_symbols.get(category, "🎁")

    def _anonymize_profile(self, profile: UserDataProfile) -> UserDataProfile:
        """Anonymize sensitive data in profile"""
        # Hash user ID
        profile.user_id = hashlib.sha256(profile.user_id.encode()).hexdigest()[:16]

        # Generalize specific brands to categories
        generalized_brands = {}
        for brand, affinity in profile.brand_affinities.items():
            category = self._brand_to_category(brand)
            if category not in generalized_brands:
                generalized_brands[category] = []
            generalized_brands[category].append(affinity)

        # Average affinities by category
        profile.brand_affinities = {
            cat: sum(affs) / len(affs) for cat, affs in generalized_brands.items()
        }

        return profile

    def _brand_to_category(self, brand: str) -> str:
        """Map brand to general category"""
        brand_categories = {
            "Nike": "Sportswear",
            "Apple": "Technology",
            "Samsung": "Technology",
            "Amazon": "Marketplace",
            "Whole Foods": "Grocery",
        }
        return brand_categories.get(brand, "General")

    async def get_vendor_safe_profile(self, user_id: str, vendor_id: str) -> dict[str, Any]:
        """
        Get user profile safe for vendor consumption

        Args:
            user_id: User identifier
            vendor_id: Vendor requesting data

        Returns:
            Vendor-safe anonymized profile
        """
        if user_id not in self.user_profiles:
            await self.sync_user_data(user_id)

        if user_id not in self.user_profiles:
            return {}

        profile = self.user_profiles[user_id]
        prefs = self.data_preferences[user_id]

        # Check vendor sharing preference
        if prefs.vendor_sharing == "none":
            return {}

        vendor_profile = {
            "profile_id": hashlib.sha256(f"{user_id}{vendor_id}".encode()).hexdigest()[:16],
            "data_completeness": profile.data_completeness,
        }

        if prefs.vendor_sharing in ["aggregated_only", "selected_vendors", "all"]:
            # Add aggregated data
            vendor_profile.update(
                {
                    "interests": profile.interests[:5],  # Top 5 only
                    "spending_categories": profile.spending_categories[:3],  # Top 3
                    "schedule_availability": self._generalize_schedule(profile.schedule_patterns),
                    "engagement_score": min(0.8, profile.data_completeness + 0.3),
                }
            )

        if prefs.vendor_sharing == "all":
            # Add more detailed data for full sharing
            vendor_profile.update(
                {
                    "brand_affinities": {
                        k: round(v, 1) for k, v in list(profile.brand_affinities.items())[:5]
                    },
                    "dream_symbols": profile.dream_symbols[:3],
                }
            )

        logger.info(f"Generated vendor-safe profile for {vendor_id}")
        return vendor_profile

    def _generalize_schedule(self, schedule: dict) -> dict:
        """Generalize schedule to protect privacy"""
        if not schedule:
            return {"availability": "standard"}

        return {
            "best_times": schedule.get("optimal_engagement_times", []),
            "availability": ("flexible" if len(schedule.get("free_slots", [])) > 3 else "busy"),
        }

    async def cleanup_old_data(self, retention_days: Optional[int] = None):
        """Clean up data older than retention period"""
        for user_id, prefs in self.data_preferences.items():
            days = retention_days or prefs.retention_days
            cutoff = datetime.now() - timedelta(days=days)

            if user_id in self.user_profiles:
                profile = self.user_profiles[user_id]
                if profile.last_sync and profile.last_sync < cutoff:
                    del self.user_profiles[user_id]
                    logger.info(f"Cleaned up old data for user {user_id}")


# Example usage
async def demo_user_data_integration():
    """Demonstrate user data integration"""

    # Mock consent manager
    class MockConsentManager:
        async def grant_consent(self, **kwargs):
            return True

    consent_mgr = MockConsentManager()
    integrator = UserDataIntegrator(consent_mgr)

    # Setup user preferences
    user_preferences = {
        "data_sources": {
            "email": {
                "enabled": True,
                "permission": "anonymized",
                "providers": ["gmail"],
                "specific_permissions": {
                    "scan_receipts": True,
                    "scan_newsletters": True,
                },
            },
            "shopping": {
                "enabled": True,
                "permission": "aggregated",
                "providers": ["amazon"],
                "specific_permissions": {
                    "share_wishlist": True,
                    "share_history": False,
                },
            },
            "calendar": {
                "enabled": True,
                "permission": "metadata_only",
                "providers": ["google"],
            },
        },
        "privacy_settings": {"anonymize_by_default": True, "retention_days": 30},
        "vendor_sharing": "aggregated_only",
    }

    # Setup preferences
    await integrator.setup_user_preferences("user_123", user_preferences)

    # Sync user data
    profile = await integrator.sync_user_data("user_123")

    print("User Profile Synced:")
    print(f"  Interests: {profile.interests}")
    print(f"  Shopping Categories: {profile.spending_categories}")
    print(f"  Brand Affinities: {profile.brand_affinities}")
    print(f"  Dream Symbols: {profile.dream_symbols}")
    print(f"  Data Completeness: {profile.data_completeness:.1%}")

    # Get vendor-safe profile
    vendor_profile = await integrator.get_vendor_safe_profile("user_123", "vendor_abc")
    print("\nVendor-Safe Profile:")
    print(json.dumps(vendor_profile, indent=2))


if __name__ == "__main__":
    import asyncio

    asyncio.run(demo_user_data_integration())
