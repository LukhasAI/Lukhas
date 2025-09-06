#!/usr/bin/env python3
"""
NIΛS Vendor Portal & SDK - Commercial vendor integration for dream commerce
Part of the Lambda Products Suite by LUKHAS AI
"""

import hashlib
import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from .user_data_integrator import UserDataIntegrator

logger = logging.getLogger("Lambda.NIΛS.VendorPortal", timezone)


class VendorTier(Enum):
    """Vendor partnership tiers"""

    TRIAL = "trial"  # 30-day trial, limited features
    BASIC = "basic"  # Basic dream seed creation
    PROFESSIONAL = "professional"  # Advanced analytics, A/B testing
    ENTERPRISE = "enterprise"  # Full API access, custom integration
    STRATEGIC = "strategic"  # Co-creation, revenue sharing


class DreamSeedType(Enum):
    """Types of dream seeds vendors can create"""

    REMINDER = "reminder"  # Gentle product reminders
    DISCOVERY = "discovery"  # New product discovery
    SEASONAL = "seasonal"  # Holiday/seasonal offers
    REPLENISHMENT = "replenishment"  # Auto-replenishment suggestions
    EXCLUSIVE = "exclusive"  # VIP/exclusive offers
    NARRATIVE = "narrative"  # Story-driven experiences
    EXPERIENTIAL = "experiential"  # Virtual try-before-buy


@dataclass
class VendorProfile:
    """Vendor profile and capabilities"""

    vendor_id: str
    company_name: str
    tier: VendorTier
    created_at: datetime
    api_key: str
    api_secret: str
    domains: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    ethical_score: float = 0.0
    active: bool = True
    settings: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, Any] = field(default_factory=dict)

    def generate_api_credentials(self) -> tuple[str, str]:
        """Generate new API credentials for vendor"""
        api_key = f"vk_{uuid.uuid4().hex}"
        api_secret = hashlib.sha256(f"{self.vendor_id}_{datetime.now(timezone.utc).isoformat()}".encode()).hexdigest()
        return api_key, api_secret


@dataclass
class DreamSeed:
    """A dream seed created by a vendor"""

    seed_id: str
    vendor_id: str
    seed_type: DreamSeedType
    title: str
    narrative: str  # Poetic narrative content
    emotional_triggers: dict[str, float]  # Joy, Calm, Stress, Longing scores
    product_data: dict[str, Any]
    offer_details: dict[str, Any]
    media_assets: list[dict[str, str]]  # URLs to images/videos
    targeting_criteria: dict[str, Any]
    affiliate_link: str
    one_click_data: dict[str, Any]  # Pre-filled purchase data
    expiry: Optional[datetime] = None
    ethical_validation: dict[str, Any] = field(default_factory=dict)
    performance_metrics: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def is_valid(self) -> bool:
        """Check if dream seed is still valid"""
        if self.expiry and datetime.now(timezone.utc) > self.expiry:
            return False
        return self.ethical_validation.get("approved", False)


class VendorPortal:
    """
    Commercial vendor portal for NIΛS dream commerce

    Features:
    - Vendor onboarding and management
    - Dream seed creation and validation
    - One-click commerce integration
    - Performance analytics
    - Ethical compliance checking
    - Revenue sharing management
    """

    def __init__(self, config: Optional[dict] = None, consent_manager: Optional[Any] = None):
        self.config = config or self._default_config()
        self.vendors: dict[str, VendorProfile] = {}
        self.dream_seeds: dict[str, list[DreamSeed]] = {}
        self.pending_seeds: list[DreamSeed] = []
        # Create consent manager if not provided
        if consent_manager is None:
            from .consent_manager import ConsentManager

            consent_manager = ConsentManager()
        self.user_data_integrator = UserDataIntegrator(consent_manager)
        self.performance_tracker: dict[str, dict] = {}

        logger.info("NIΛS Vendor Portal initialized")

    def _default_config(self) -> dict:
        """Default vendor portal configuration"""
        return {
            "trial_duration_days": 30,
            "min_ethical_score": 0.8,
            "require_ethical_validation": True,
            "enable_one_click_commerce": True,
            "revenue_share_percentage": 30,  # NIAS takes 30%
            "max_seeds_per_vendor": {
                "trial": 10,
                "basic": 100,
                "professional": 1000,
                "enterprise": 10000,
                "strategic": -1,  # Unlimited
            },
            "analytics_retention_days": 90,
            "require_ssl": True,
        }

    async def onboard_vendor(
        self,
        company_name: str,
        domains: list[str],
        categories: list[str],
        tier: VendorTier = VendorTier.TRIAL,
    ) -> dict[str, Any]:
        """
        Onboard a new vendor to the platform

        Args:
            company_name: Company name
            domains: List of company domains
            categories: Product categories
            tier: Initial vendor tier

        Returns:
            Vendor profile with API credentials
        """
        try:
            vendor_id = f"vendor_{uuid.uuid4().hex[:12]}"

            # Create vendor profile
            vendor = VendorProfile(
                vendor_id=vendor_id,
                company_name=company_name,
                tier=tier,
                created_at=datetime.now(timezone.utc),
                api_key="",
                api_secret="",
                domains=domains,
                categories=categories,
                ethical_score=1.0,  # Start with perfect score
            )

            # Generate API credentials
            api_key, api_secret = vendor.generate_api_credentials()
            vendor.api_key = api_key
            vendor.api_secret = api_secret

            # Store vendor
            self.vendors[vendor_id] = vendor
            self.dream_seeds[vendor_id] = []

            logger.info(f"Vendor onboarded: {company_name} ({vendor_id})")

            return {
                "vendor_id": vendor_id,
                "api_key": api_key,
                "api_secret": api_secret,
                "tier": tier.value,
                "webhook_url": f"https://api.nias.ai/vendor/{vendor_id}/webhook",
                "sdk_download": "https://sdk.nias.ai/download",
                "documentation": "https://docs.nias.ai/vendor",
                "sandbox_mode": tier == VendorTier.TRIAL,
            }

        except Exception as e:
            logger.error(f"Error onboarding vendor: {e}")
            return {"error": str(e)}

    async def create_dream_seed(self, vendor_id: str, seed_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new dream seed for vendor's products/offers

        Args:
            vendor_id: Vendor identifier
            seed_data: Dream seed configuration

        Returns:
            Created dream seed with validation status
        """
        try:
            if vendor_id not in self.vendors:
                return {"error": "Vendor not found"}

            vendor = self.vendors[vendor_id]

            # Check seed limit for vendor tier
            max_seeds = self.config["max_seeds_per_vendor"].get(vendor.tier.value, 10)
            if max_seeds != -1 and len(self.dream_seeds[vendor_id]) >= max_seeds:
                return {"error": f"Seed limit reached for {vendor.tier.value} tier"}

            # Create dream seed
            seed_id = f"seed_{uuid.uuid4().hex[:16]}"

            # Extract and validate seed data
            seed = DreamSeed(
                seed_id=seed_id,
                vendor_id=vendor_id,
                seed_type=DreamSeedType(seed_data.get("type", "reminder")),
                title=seed_data.get("title", ""),
                narrative=seed_data.get("narrative", ""),
                emotional_triggers=seed_data.get(
                    "emotional_triggers",
                    {"joy": 0.5, "calm": 0.5, "stress": 0.0, "longing": 0.3},
                ),
                product_data=seed_data.get("product_data", {}),
                offer_details=seed_data.get("offer_details", {}),
                media_assets=seed_data.get("media_assets", []),
                targeting_criteria=seed_data.get("targeting_criteria", {}),
                affiliate_link=seed_data.get("affiliate_link", ""),
                one_click_data=seed_data.get("one_click_data", {}),
                expiry=datetime.now(timezone.utc) + timedelta(days=seed_data.get("validity_days", 30)),
            )

            # Validate dream seed ethically
            ethical_validation = await self._validate_dream_seed(seed)
            seed.ethical_validation = ethical_validation

            if ethical_validation["approved"]:
                # Add to active seeds
                self.dream_seeds[vendor_id].append(seed)
                status = "approved"
            else:
                # Add to pending seeds for review
                self.pending_seeds.append(seed)
                status = "pending_review"

            logger.info(f"Dream seed created: {seed_id} for vendor {vendor_id} - Status: {status}")

            return {
                "seed_id": seed_id,
                "status": status,
                "ethical_validation": ethical_validation,
                "targeting_reach": await self._estimate_reach(seed.targeting_criteria),
                "preview_url": f"https://preview.nias.ai/seed/{seed_id}",
            }

        except Exception as e:
            logger.error(f"Error creating dream seed: {e}")
            return {"error": str(e)}

    async def _validate_dream_seed(self, seed: DreamSeed) -> dict[str, Any]:
        """Validate dream seed for ethical compliance"""
        validation_results = {"approved": True, "score": 1.0, "checks": {}}

        # Check emotional manipulation
        stress_level = seed.emotional_triggers.get("stress", 0)
        if stress_level > 0.3:
            validation_results["checks"]["emotional_manipulation"] = False
            validation_results["approved"] = False
            validation_results["score"] *= 0.5
        else:
            validation_results["checks"]["emotional_manipulation"] = True

        # Check for aggressive marketing language
        aggressive_words = [
            "buy now",
            "limited time",
            "act fast",
            "don't miss",
            "hurry",
        ]
        narrative_lower = seed.narrative.lower()
        has_aggressive = any(word in narrative_lower for word in aggressive_words)

        if has_aggressive:
            validation_results["checks"]["aggressive_marketing"] = False
            validation_results["score"] *= 0.7
        else:
            validation_results["checks"]["aggressive_marketing"] = True

        # Check for truthfulness (simplified - would use AI in production)
        if not seed.product_data or not seed.offer_details:
            validation_results["checks"]["transparency"] = False
            validation_results["score"] *= 0.8
        else:
            validation_results["checks"]["transparency"] = True

        # Check targeting ethics
        targeting = seed.targeting_criteria
        if targeting.get("vulnerable_groups") or targeting.get("age_min", 18) < 13:
            validation_results["checks"]["ethical_targeting"] = False
            validation_results["approved"] = False
            validation_results["score"] *= 0.3
        else:
            validation_results["checks"]["ethical_targeting"] = True

        # Final approval based on score
        if validation_results["score"] < self.config["min_ethical_score"]:
            validation_results["approved"] = False

        return validation_results

    async def _estimate_reach(self, targeting_criteria: dict[str, Any]) -> dict[str, Any]:
        """Estimate potential reach for targeting criteria"""
        # Simplified estimation - would use real user data in production
        base_reach = 100000

        # Apply targeting filters
        if targeting_criteria.get("interests"):
            base_reach *= 0.3
        if targeting_criteria.get("location"):
            base_reach *= 0.5
        if targeting_criteria.get("age_range"):
            base_reach *= 0.4
        if targeting_criteria.get("purchase_history"):
            base_reach *= 0.2

        return {
            "estimated_users": int(base_reach),
            "confidence": 0.7,
            "segments": targeting_criteria.keys(),
        }

    async def generate_affiliate_link(self, vendor_id: str, product_id: str, user_context: dict[str, Any]) -> str:
        """
        Generate a one-click affiliate link with pre-filled user data

        Args:
            vendor_id: Vendor identifier
            product_id: Product identifier
            user_context: User preferences and data

        Returns:
            One-click purchase URL
        """
        try:
            # Create tracking ID
            tracking_id = f"nias_{uuid.uuid4().hex[:8]}"

            # Build affiliate parameters
            params = {
                "vendor": vendor_id,
                "product": product_id,
                "tracking": tracking_id,
                "source": "nias_dream",
                "user_prefs": {
                    "size": user_context.get("preferences", {}).get("size"),
                    "color": user_context.get("preferences", {}).get("color"),
                    "shipping": user_context.get("shipping_preference", "standard"),
                    "payment": user_context.get("payment_method", "saved"),
                },
            }

            # Encode parameters
            import base64
            import urllib.parse

            encoded_params = base64.b64encode(json.dumps(params).encode()).decode()

            # Generate affiliate link
            vendor = self.vendors.get(vendor_id)
            base_url = f"https://{vendor.domains[0]}" if vendor and vendor.domains else "https://checkout.nias.ai"

            affiliate_link = f"{base_url}/quick-buy?data={urllib.parse.quote(encoded_params)}"

            # Store tracking data
            self.performance_tracker[tracking_id] = {
                "vendor_id": vendor_id,
                "product_id": product_id,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "user_segment": user_context.get("segment", "default"),
            }

            return affiliate_link

        except Exception as e:
            logger.error(f"Error generating affiliate link: {e}")
            return ""

    async def get_vendor_analytics(
        self, vendor_id: str, date_range: Optional[tuple[datetime, datetime]] = None
    ) -> dict[str, Any]:
        """Get performance analytics for a vendor"""
        if vendor_id not in self.vendors:
            return {"error": "Vendor not found"}

        vendor = self.vendors[vendor_id]
        seeds = self.dream_seeds.get(vendor_id, [])

        # Calculate metrics
        total_seeds = len(seeds)
        active_seeds = len([s for s in seeds if s.is_valid()])

        # Aggregate performance metrics
        total_impressions = sum(s.performance_metrics.get("impressions", 0) for s in seeds)
        total_clicks = sum(s.performance_metrics.get("clicks", 0) for s in seeds)
        total_conversions = sum(s.performance_metrics.get("conversions", 0) for s in seeds)

        # Calculate rates
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

        # Revenue calculation
        total_revenue = sum(s.performance_metrics.get("revenue", 0) for s in seeds)
        nias_commission = total_revenue * (self.config["revenue_share_percentage"] / 100)
        vendor_revenue = total_revenue - nias_commission

        return {
            "vendor_id": vendor_id,
            "company_name": vendor.company_name,
            "tier": vendor.tier.value,
            "ethical_score": vendor.ethical_score,
            "seeds": {
                "total": total_seeds,
                "active": active_seeds,
                "pending": len([s for s in self.pending_seeds if s.vendor_id == vendor_id]),
            },
            "performance": {
                "impressions": total_impressions,
                "clicks": total_clicks,
                "conversions": total_conversions,
                "ctr": round(ctr, 2),
                "conversion_rate": round(conversion_rate, 2),
            },
            "revenue": {
                "total": round(total_revenue, 2),
                "vendor_share": round(vendor_revenue, 2),
                "nias_commission": round(nias_commission, 2),
                "currency": "USD",
            },
            "top_performing_seeds": self._get_top_seeds(seeds, 5),
        }

    def _get_top_seeds(self, seeds: list[DreamSeed], limit: int = 5) -> list[dict[str, Any]]:
        """Get top performing dream seeds"""
        # Sort by conversion rate
        sorted_seeds = sorted(
            seeds,
            key=lambda s: s.performance_metrics.get("conversion_rate", 0),
            reverse=True,
        )[:limit]

        return [
            {
                "seed_id": s.seed_id,
                "title": s.title,
                "type": s.seed_type.value,
                "conversions": s.performance_metrics.get("conversions", 0),
                "revenue": s.performance_metrics.get("revenue", 0),
            }
            for s in sorted_seeds
        ]

    async def update_seed_performance(self, seed_id: str, event_type: str, event_data: dict[str, Any]) -> bool:
        """Update performance metrics for a dream seed"""
        try:
            # Find the seed
            seed = None
            for vendor_seeds in self.dream_seeds.values():
                for s in vendor_seeds:
                    if s.seed_id == seed_id:
                        seed = s
                        break
                if seed:
                    break

            if not seed:
                logger.warning(f"Seed not found for performance update: {seed_id}")
                return False

            # Update metrics based on event type
            if event_type == "impression":
                seed.performance_metrics["impressions"] = seed.performance_metrics.get("impressions", 0) + 1
            elif event_type == "click":
                seed.performance_metrics["clicks"] = seed.performance_metrics.get("clicks", 0) + 1
            elif event_type == "conversion":
                seed.performance_metrics["conversions"] = seed.performance_metrics.get("conversions", 0) + 1
                seed.performance_metrics["revenue"] = seed.performance_metrics.get("revenue", 0) + event_data.get(
                    "amount", 0
                )

            # Update vendor ethical score based on user feedback
            if event_type == "user_feedback":
                vendor = self.vendors.get(seed.vendor_id)
                if vendor:
                    feedback_score = event_data.get("score", 0)
                    # Weighted average with existing score
                    vendor.ethical_score = (vendor.ethical_score * 0.9) + (feedback_score * 0.1)

            return True

        except Exception as e:
            logger.error(f"Error updating seed performance: {e}")
            return False

    async def get_vendor_sdk_code(self, vendor_id: str, language: str = "python") -> str:
        """Generate SDK code for vendor integration"""
        if vendor_id not in self.vendors:
            return ""

        vendor = self.vendors[vendor_id]

        if language == "python":
            return f'''
"""
NIAS Dream Commerce SDK for {vendor.company_name}
Generated for vendor: {vendor_id}
"""

import requests
import json
from typing import Dict, Any

class NIASDreamSDK:
    def __init__(self):
        self.api_key = "{vendor.api_key}"
        self.api_secret = "YOUR_API_SECRET"  # Store securely
        self.base_url = "https://api.nias.ai/v1"
        self.vendor_id = "{vendor_id}"

    def create_dream_seed(self, seed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new dream seed"""
        endpoint = f"{{self.base_url}}/vendor/{{self.vendor_id}}/seeds"

        headers = {{
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json"
        }}

        response = requests.post(endpoint, json=seed_data, headers=headers)
        return response.json()

    def get_analytics(self, date_from: str = None, date_to: str = None) -> Dict[str, Any]:
        """Get performance analytics"""
        endpoint = f"{{self.base_url}}/vendor/{{self.vendor_id}}/analytics"

        params = {{}}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to

        headers = {{
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret
        }}

        response = requests.get(endpoint, params=params, headers=headers)
        return response.json()

    def create_poetic_narrative(self, product_name: str, context: str) -> str:
        """Generate a poetic narrative for your product"""
        # This would call the NIAS narrative generation service
        endpoint = f"{{self.base_url}}/vendor/{{self.vendor_id}}/narrative"

        data = {{
            "product_name": product_name,
            "context": context,
            "style": "poetic_dream"
        }}

        headers = {{
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json"
        }}

        response = requests.post(endpoint, json=data, headers=headers)
        return response.json().get("narrative", "")

# Example usage
sdk = NIASDreamSDK()

# Create a dream seed for a product
seed = sdk.create_dream_seed({{
    "type": "seasonal",
    "title": "Winter Warmth Collection",
    "narrative": "As snowflakes dance outside your window, imagine wrapping yourself in clouds...",
    "emotional_triggers": {{
        "joy": 0.7,
        "calm": 0.8,
        "stress": 0.0,
        "longing": 0.5
    }},
    "product_data": {{
        "id": "WW-001",
        "name": "Cashmere Cloud Sweater",
        "price": 189.99,
        "category": "apparel"
    }},
    "offer_details": {{
        "discount": 20,
        "code": "WINTER20",
        "valid_until": "2024-02-29"
    }},
    "targeting_criteria": {{
        "interests": ["fashion", "comfort", "luxury"],
        "season": "winter"
    }}
}})

print(f"Dream seed created: {{seed}}")
'''

        elif language == "javascript":
            return f"""
/**
 * NIAS Dream Commerce SDK for {vendor.company_name}
 * Generated for vendor: {vendor_id}
 */

const axios = require('axios');

class NIASDreamSDK {{
    constructor() {{
        this.apiKey = '{vendor.api_key}';
        this.apiSecret = process.env.NIAS_API_SECRET; // Store securely
        this.baseUrl = 'https://api.nias.ai/v1';
        this.vendorId = '{vendor_id}';
    }}

    async createDreamSeed(seedData) {{
        const endpoint = `${{this.baseUrl}}/vendor/${{this.vendorId}}/seeds`;

        try {{
            const response = await axios.post(endpoint, seedData, {{
                headers: {{
                    'X-API-Key': this.apiKey,
                    'X-API-Secret': this.apiSecret,
                    'Content-Type': 'application/json'
                }}
            }});

            return response.data;
        }} catch (error) {{
            console.error('Error creating dream seed:', error);
            throw error;
        }}
    }}

    async getAnalytics(dateFrom = null, dateTo = null) {{
        const endpoint = `${{this.baseUrl}}/vendor/${{this.vendorId}}/analytics`;

        const params = {{}};
        if (dateFrom) params.from = dateFrom;
        if (dateTo) params.to = dateTo;

        try {{
            const response = await axios.get(endpoint, {{
                params,
                headers: {{
                    'X-API-Key': this.apiKey,
                    'X-API-Secret': this.apiSecret
                }}
            }});

            return response.data;
        }} catch (error) {{
            console.error('Error fetching analytics:', error);
            throw error;
        }}
    }}
}}

module.exports = NIASDreamSDK;
"""

        return ""
