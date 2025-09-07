#!/usr/bin/env python3
"""
Attribution Fallback Ladder - Production Implementation
Multi-tier attribution with confidence scoring and S2S postback integration
"""

import asyncio
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class AttributionMethod(Enum):
    AFFILIATE_LINK = "affiliate_link"
    S2S_POSTBACK = "s2s_postback"
    RECEIPT_MATCHING = "receipt_matching"
    BEHAVIORAL_INFERENCE = "behavioral_inference"
    LAST_TOUCH = "last_touch"
    DEFAULT_FALLBACK = "default_fallback"


@dataclass
class AttributionResult:
    method: AttributionMethod
    confidence: float
    opportunity_id: str
    publisher_id: str
    merchant_id: str
    conversion_value_usd: float
    attribution_data: dict
    timestamp: datetime
    expires_at: datetime


class AttributionFallbackLadder:
    """
    Production-ready attribution system with 6-tier fallback
    Ensures reliable attribution even when primary methods fail
    """

    def __init__(self, redis_client=None, webhook_secret: Optional[str] = None):
        self.redis_client = redis_client
        self.webhook_secret = webhook_secret or "default_webhook_secret"

        # Confidence thresholds for each attribution method
        self.confidence_thresholds = {
            AttributionMethod.AFFILIATE_LINK: 0.95,
            AttributionMethod.S2S_POSTBACK: 0.85,
            AttributionMethod.RECEIPT_MATCHING: 0.75,
            AttributionMethod.BEHAVIORAL_INFERENCE: 0.60,
            AttributionMethod.LAST_TOUCH: 0.40,
            AttributionMethod.DEFAULT_FALLBACK: 0.20,
        }

        # Attribution windows (how long attribution is valid)
        self.attribution_windows = {
            AttributionMethod.AFFILIATE_LINK: timedelta(days=7),
            AttributionMethod.S2S_POSTBACK: timedelta(days=7),
            AttributionMethod.RECEIPT_MATCHING: timedelta(days=3),
            AttributionMethod.BEHAVIORAL_INFERENCE: timedelta(days=1),
            AttributionMethod.LAST_TOUCH: timedelta(hours=24),
            AttributionMethod.DEFAULT_FALLBACK: timedelta(hours=1),
        }

    async def attribute_conversion(self, conversion_event: dict, user_context: dict) -> AttributionResult:
        """
        Main attribution function - attempts all methods in priority order

        Args:
            conversion_event: Purchase/conversion data
            user_context: User session and behavior data

        Returns:
            AttributionResult with highest confidence match
        """

        attribution_attempts = []

        # Tier 1: Affiliate Link Attribution (0.95+ confidence)
        affiliate_result = await self._try_affiliate_attribution(conversion_event, user_context)
        if (
            affiliate_result
            and affiliate_result.confidence >= self.confidence_thresholds[AttributionMethod.AFFILIATE_LINK]
        ):
            return affiliate_result
        if affiliate_result:
            attribution_attempts.append(affiliate_result)

        # Tier 2: S2S Postback Attribution (0.85+ confidence)
        s2s_result = await self._try_s2s_attribution(conversion_event, user_context)
        if s2s_result and s2s_result.confidence >= self.confidence_thresholds[AttributionMethod.S2S_POSTBACK]:
            return s2s_result
        if s2s_result:
            attribution_attempts.append(s2s_result)

        # Tier 3: Receipt Matching Attribution (0.75+ confidence)
        receipt_result = await self._try_receipt_matching(conversion_event, user_context)
        if (
            receipt_result
            and receipt_result.confidence >= self.confidence_thresholds[AttributionMethod.RECEIPT_MATCHING]
        ):
            return receipt_result
        if receipt_result:
            attribution_attempts.append(receipt_result)

        # Tier 4: Behavioral Inference Attribution (0.60+ confidence)
        behavioral_result = await self._try_behavioral_inference(conversion_event, user_context)
        if (
            behavioral_result
            and behavioral_result.confidence >= self.confidence_thresholds[AttributionMethod.BEHAVIORAL_INFERENCE]
        ):
            return behavioral_result
        if behavioral_result:
            attribution_attempts.append(behavioral_result)

        # Tier 5: Last Touch Attribution (0.40+ confidence)
        last_touch_result = await self._try_last_touch_attribution(conversion_event, user_context)
        if (
            last_touch_result
            and last_touch_result.confidence >= self.confidence_thresholds[AttributionMethod.LAST_TOUCH]
        ):
            return last_touch_result
        if last_touch_result:
            attribution_attempts.append(last_touch_result)

        # Tier 6: Default Fallback (0.20 confidence)
        fallback_result = await self._default_fallback_attribution(conversion_event, user_context)
        attribution_attempts.append(fallback_result)

        # Return highest confidence result
        best_result = max(attribution_attempts, key=lambda r: r.confidence)
        return best_result

    async def _try_affiliate_attribution(
        self, conversion_event: dict, user_context: dict
    ) -> Optional[AttributionResult]:
        """Tier 1: Direct affiliate link attribution"""

        # Check for LUKHAS affiliate parameters in referrer or URL
        referrer_url = user_context.get("referrer_url", "")
        current_url = user_context.get("current_url", "")

        # Look for LUKHAS tracking parameters
        tracking_params = self._extract_tracking_params(referrer_url) or self._extract_tracking_params(current_url)

        if not tracking_params:
            return None

        # Validate tracking signature
        if not self._validate_tracking_signature(tracking_params):
            return None

        # Extract attribution data
        opportunity_id = tracking_params.get("opp_id")
        publisher_id = tracking_params.get("pub_id")
        merchant_id = tracking_params.get("merchant_id")

        if not all([opportunity_id, publisher_id, merchant_id]):
            return None

        # Check attribution window
        click_timestamp = tracking_params.get("timestamp")
        if click_timestamp:
            click_time = datetime.fromtimestamp(int(click_timestamp))
            if datetime.now(timezone.utc) - click_time > self.attribution_windows[AttributionMethod.AFFILIATE_LINK]:
                return None

        # High confidence for direct affiliate attribution
        confidence = 0.98 if self._verify_direct_click_path(user_context) else 0.95

        return AttributionResult(
            method=AttributionMethod.AFFILIATE_LINK,
            confidence=confidence,
            opportunity_id=opportunity_id,
            publisher_id=publisher_id,
            merchant_id=merchant_id,
            conversion_value_usd=conversion_event.get("value_usd", 0.0),
            attribution_data={
                "click_timestamp": click_timestamp,
                "referrer_url": referrer_url,
                "tracking_params": tracking_params,
                "direct_path": self._verify_direct_click_path(user_context),
            },
            timestamp=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.AFFILIATE_LINK],
        )

    async def _try_s2s_attribution(self, conversion_event: dict, user_context: dict) -> Optional[AttributionResult]:
        """Tier 2: Server-to-Server postback attribution"""

        # Look for S2S postback data in recent conversions
        user_id = user_context.get("user_id")
        if not user_id:
            return None

        # Check for recent S2S postbacks in cache/database
        s2s_key = f"s2s_attribution:{user_id}"

        if self.redis_client:
            s2s_data = await self.redis_client.get(s2s_key)
            if s2s_data:
                s2s_record = json.loads(s2s_data)

                # Verify postback timestamp within window
                postback_time = datetime.fromisoformat(s2s_record["timestamp"])
                if datetime.now(timezone.utc) - postback_time <= self.attribution_windows[AttributionMethod.S2S_POSTBACK]:
                    # Validate postback signature
                    if self._validate_postback_signature(s2s_record):
                        confidence = 0.90 if self._match_conversion_details(s2s_record, conversion_event) else 0.85

                        return AttributionResult(
                            method=AttributionMethod.S2S_POSTBACK,
                            confidence=confidence,
                            opportunity_id=s2s_record["opportunity_id"],
                            publisher_id=s2s_record["publisher_id"],
                            merchant_id=s2s_record["merchant_id"],
                            conversion_value_usd=conversion_event.get("value_usd", 0.0),
                            attribution_data={
                                "postback_data": s2s_record,
                                "value_match": self._match_conversion_details(s2s_record, conversion_event),
                            },
                            timestamp=datetime.now(timezone.utc),
                            expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.S2S_POSTBACK],
                        )

        return None

    async def _try_receipt_matching(self, conversion_event: dict, user_context: dict) -> Optional[AttributionResult]:
        """Tier 3: Receipt-based attribution matching"""

        # Extract purchase details for matching
        purchase_details = {
            "amount": conversion_event.get("value_usd"),
            "timestamp": conversion_event.get("timestamp"),
            "merchant": conversion_event.get("merchant"),
            "products": conversion_event.get("products", []),
        }

        # Look for matching opportunities in recent browsing history
        user_id = user_context.get("user_id")
        recent_opportunities = await self._get_recent_opportunities(user_id)

        best_match = None
        best_confidence = 0.0

        for opportunity in recent_opportunities:
            match_confidence = self._calculate_receipt_match_confidence(purchase_details, opportunity)

            if match_confidence > best_confidence and match_confidence >= 0.75:
                best_match = opportunity
                best_confidence = match_confidence

        if best_match:
            return AttributionResult(
                method=AttributionMethod.RECEIPT_MATCHING,
                confidence=best_confidence,
                opportunity_id=best_match["opportunity_id"],
                publisher_id=best_match["publisher_id"],
                merchant_id=best_match["merchant_id"],
                conversion_value_usd=conversion_event.get("value_usd", 0.0),
                attribution_data={
                    "matched_opportunity": best_match,
                    "match_factors": self._get_match_factors(purchase_details, best_match),
                    "match_confidence": best_confidence,
                },
                timestamp=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.RECEIPT_MATCHING],
            )

        return None

    async def _try_behavioral_inference(
        self, conversion_event: dict, user_context: dict
    ) -> Optional[AttributionResult]:
        """Tier 4: Behavioral pattern attribution"""

        user_id = user_context.get("user_id")
        if not user_id:
            return None

        # Analyze recent behavioral patterns
        behavioral_data = await self._analyze_user_behavior(user_id, conversion_event)

        if behavioral_data["confidence"] >= 0.60:
            # Find most likely opportunity based on behavioral signals
            likely_opportunity = await self._infer_opportunity_from_behavior(behavioral_data)

            if likely_opportunity:
                return AttributionResult(
                    method=AttributionMethod.BEHAVIORAL_INFERENCE,
                    confidence=behavioral_data["confidence"],
                    opportunity_id=likely_opportunity["opportunity_id"],
                    publisher_id=likely_opportunity["publisher_id"],
                    merchant_id=likely_opportunity["merchant_id"],
                    conversion_value_usd=conversion_event.get("value_usd", 0.0),
                    attribution_data={
                        "behavioral_signals": behavioral_data["signals"],
                        "inference_factors": behavioral_data["factors"],
                        "pattern_match": likely_opportunity,
                    },
                    timestamp=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.BEHAVIORAL_INFERENCE],
                )

        return None

    async def _try_last_touch_attribution(
        self, conversion_event: dict, user_context: dict
    ) -> Optional[AttributionResult]:
        """Tier 5: Last touch attribution"""

        user_id = user_context.get("user_id")
        if not user_id:
            return None

        # Get last LUKHAS interaction within 24 hours
        last_interaction = await self._get_last_lukhas_interaction(user_id)

        if last_interaction:
            interaction_time = datetime.fromisoformat(last_interaction["timestamp"])
            if datetime.now(timezone.utc) - interaction_time <= self.attribution_windows[AttributionMethod.LAST_TOUCH]:
                confidence = 0.50 if interaction_time > datetime.now(timezone.utc) - timedelta(hours=6) else 0.40

                return AttributionResult(
                    method=AttributionMethod.LAST_TOUCH,
                    confidence=confidence,
                    opportunity_id=last_interaction["opportunity_id"],
                    publisher_id=last_interaction["publisher_id"],
                    merchant_id=last_interaction["merchant_id"],
                    conversion_value_usd=conversion_event.get("value_usd", 0.0),
                    attribution_data={
                        "last_interaction": last_interaction,
                        "time_gap_hours": (datetime.now(timezone.utc) - interaction_time).total_seconds() / 3600,
                    },
                    timestamp=datetime.now(timezone.utc),
                    expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.LAST_TOUCH],
                )

        return None

    async def _default_fallback_attribution(self, conversion_event: dict, user_context: dict) -> AttributionResult:
        """Tier 6: Default fallback attribution"""

        # Default to most active publisher/merchant pair for this user
        user_id = user_context.get("user_id")
        default_attribution = await self._get_default_attribution(user_id)

        return AttributionResult(
            method=AttributionMethod.DEFAULT_FALLBACK,
            confidence=0.20,
            opportunity_id=default_attribution.get("opportunity_id", "fallback_opportunity"),
            publisher_id=default_attribution.get("publisher_id", "default_publisher"),
            merchant_id=default_attribution.get("merchant_id", "default_merchant"),
            conversion_value_usd=conversion_event.get("value_usd", 0.0),
            attribution_data={
                "fallback_reason": "No higher-confidence attribution available",
                "default_data": default_attribution,
            },
            timestamp=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + self.attribution_windows[AttributionMethod.DEFAULT_FALLBACK],
        )

    # Helper methods

    def _extract_tracking_params(self, url: str) -> Optional[dict]:
        """Extract LUKHAS tracking parameters from URL"""
        if "lukhas" not in url.lower():
            return None

        try:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            tracking_data = {}
            for key, value in params.items():
                if key.startswith(("lukhas_", "lks_")):
                    tracking_data[key.replace("lukhas_", "").replace("lks_", "")] = value[0]

            return tracking_data if tracking_data else None
        except:
            return None

    def _validate_tracking_signature(self, tracking_params: dict) -> bool:
        """Validate HMAC signature of tracking parameters"""
        if "signature" not in tracking_params:
            return False

        # Rebuild signature from parameters
        param_string = "&".join([f"{k}={v}" for k, v in sorted(tracking_params.items()) if k != "signature"])
        expected_signature = hmac.new(self.webhook_secret.encode(), param_string.encode(), hashlib.sha256).hexdigest()

        return hmac.compare_digest(tracking_params["signature"], expected_signature)

    def _verify_direct_click_path(self, user_context: dict) -> bool:
        """Verify user came directly from affiliate link without detours"""
        session_data = user_context.get("session_history", [])

        # Check if user went directly from affiliate link to purchase
        if len(session_data) <= 2:  # Link -> Product -> Purchase
            return True

        # Allow some navigation but penalize excessive browsing
        return len(session_data) <= 5

    def _validate_postback_signature(self, s2s_record: dict) -> bool:
        """Validate S2S postback signature"""
        if "signature" not in s2s_record:
            return False

        # Rebuild postback signature
        postback_string = json.dumps(s2s_record.get("data", {}), sort_keys=True)
        expected_signature = hmac.new(
            self.webhook_secret.encode(), postback_string.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(s2s_record["signature"], expected_signature)

    def _match_conversion_details(self, s2s_record: dict, conversion_event: dict) -> bool:
        """Match S2S postback details with actual conversion"""
        s2s_value = s2s_record.get("expected_value", 0)
        actual_value = conversion_event.get("value_usd", 0)

        # Allow 10% variance in value
        value_match = abs(s2s_value - actual_value) / max(s2s_value, actual_value) <= 0.10

        # Check timing - conversion should happen within reasonable time of postback
        postback_time = datetime.fromisoformat(s2s_record["timestamp"])
        conversion_time = datetime.fromisoformat(conversion_event.get("timestamp", datetime.now(timezone.utc).isoformat()))
        time_match = abs((conversion_time - postback_time).total_seconds()) <= 3600  # 1 hour

        return value_match and time_match

    async def _get_recent_opportunities(self, user_id: str) -> list[dict]:
        """Get user's recent opportunity interactions"""
        # In production, this would query the opportunities database
        # For now, return mock data
        return [
            {
                "opportunity_id": "opp_123",
                "publisher_id": "pub_456",
                "merchant_id": "merchant_789",
                "product": "Premium Headphones",
                "price": 299.99,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat(),
                "interaction_type": "view",
            }
        ]

    def _calculate_receipt_match_confidence(self, purchase_details: dict, opportunity: dict) -> float:
        """Calculate confidence score for receipt matching"""
        confidence = 0.0

        # Exact product match
        if opportunity.get("product", "").lower() in str(purchase_details.get("products", [])).lower():
            confidence += 0.4

        # Price match (within 10%)
        opp_price = opportunity.get("price", 0)
        purchase_price = purchase_details.get("amount", 0)
        if opp_price > 0 and purchase_price > 0:
            price_variance = abs(opp_price - purchase_price) / opp_price
            if price_variance <= 0.10:
                confidence += 0.3
            elif price_variance <= 0.25:
                confidence += 0.15

        # Timing match (within opportunity window)
        opp_time = datetime.fromisoformat(opportunity["timestamp"])
        purchase_time = datetime.fromisoformat(purchase_details["timestamp"])
        time_gap = abs((purchase_time - opp_time).total_seconds())

        if time_gap <= 3600:  # 1 hour
            confidence += 0.2
        elif time_gap <= 86400:  # 24 hours
            confidence += 0.1

        # Merchant match
        if opportunity.get("merchant_id") == purchase_details.get("merchant"):
            confidence += 0.1

        return min(confidence, 1.0)

    def _get_match_factors(self, purchase_details: dict, opportunity: dict) -> dict:
        """Get detailed matching factors for receipt attribution"""
        return {
            "product_match": opportunity.get("product", "").lower()
            in str(purchase_details.get("products", [])).lower(),
            "price_variance": abs(opportunity.get("price", 0) - purchase_details.get("amount", 0))
            / max(opportunity.get("price", 1), 1),
            "time_gap_hours": abs(
                (
                    datetime.fromisoformat(purchase_details["timestamp"])
                    - datetime.fromisoformat(opportunity["timestamp"])
                ).total_seconds()
            )
            / 3600,
            "merchant_match": opportunity.get("merchant_id") == purchase_details.get("merchant"),
        }

    async def _analyze_user_behavior(self, user_id: str, conversion_event: dict) -> dict:
        """Analyze behavioral patterns for attribution inference"""
        # Mock behavioral analysis - in production this would use ML models
        return {
            "confidence": 0.65,
            "signals": ["repeated_product_views", "price_comparison_behavior", "category_affinity"],
            "factors": {"view_frequency": 0.8, "time_on_product": 0.7, "category_match": 0.9},
        }

    async def _infer_opportunity_from_behavior(self, behavioral_data: dict) -> Optional[dict]:
        """Infer most likely opportunity from behavioral patterns"""
        # Mock inference - in production this would use behavioral models
        return {
            "opportunity_id": "opp_behavioral_123",
            "publisher_id": "pub_behavioral_456",
            "merchant_id": "merchant_behavioral_789",
            "inferred_product": "Smart Watch",
            "confidence_factors": behavioral_data["factors"],
        }

    async def _get_last_lukhas_interaction(self, user_id: str) -> Optional[dict]:
        """Get user's last interaction with LUKHAS system"""
        # Mock data - in production this would query interaction logs
        return {
            "opportunity_id": "opp_last_123",
            "publisher_id": "pub_last_456",
            "merchant_id": "merchant_last_789",
            "interaction_type": "click",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat(),
        }

    async def _get_default_attribution(self, user_id: str) -> dict:
        """Get default attribution for fallback scenarios"""
        # Mock default attribution
        return {
            "opportunity_id": "opp_default_000",
            "publisher_id": "pub_default_000",
            "merchant_id": "merchant_default_000",
            "reason": "Most frequent publisher/merchant for user",
        }


# S2S Postback Handler
class S2SPostbackHandler:
    """Handle incoming server-to-server postbacks for attribution"""

    def __init__(self, redis_client, webhook_secret: str):
        self.redis_client = redis_client
        self.webhook_secret = webhook_secret

    async def handle_postback(self, postback_data: dict, signature: str) -> dict:
        """Process incoming S2S postback"""

        # Validate signature
        if not self._validate_signature(postback_data, signature):
            return {"status": "error", "message": "Invalid signature"}

        # Extract attribution data
        user_id = postback_data.get("user_id")
        opportunity_id = postback_data.get("opportunity_id")
        publisher_id = postback_data.get("publisher_id")
        merchant_id = postback_data.get("merchant_id")
        expected_value = postback_data.get("expected_value_usd", 0.0)

        if not all([user_id, opportunity_id, publisher_id, merchant_id]):
            return {"status": "error", "message": "Missing required fields"}

        # Store for attribution matching
        s2s_record = {
            "postback_id": self._generate_postback_id(),
            "user_id": user_id,
            "opportunity_id": opportunity_id,
            "publisher_id": publisher_id,
            "merchant_id": merchant_id,
            "expected_value": expected_value,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "signature": signature,
            "data": postback_data,
        }

        # Store in Redis with 7-day expiration
        cache_key = f"s2s_attribution:{user_id}"
        await self.redis_client.setex(
            cache_key,
            7 * 24 * 3600,  # 7 days
            json.dumps(s2s_record),
        )

        return {
            "status": "success",
            "postback_id": s2s_record["postback_id"],
            "cached_until": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
        }

    def _validate_signature(self, postback_data: dict, signature: str) -> bool:
        """Validate HMAC signature of postback"""
        postback_string = json.dumps(postback_data, sort_keys=True)
        expected_signature = hmac.new(
            self.webhook_secret.encode(), postback_string.encode(), hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    def _generate_postback_id(self) -> str:
        """Generate unique postback ID"""
        return f"pb_{int(time.time())}_{hashlib.md5(str(time.time()).encode()).hexdigest()}[:8]}"


# Usage example
async def main():
    """Demo usage of attribution fallback ladder"""

    # Initialize attribution system
    attribution_ladder = AttributionFallbackLadder()

    # Mock conversion event
    conversion_event = {
        "conversion_id": "conv_123456",
        "value_usd": 299.99,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "merchant": "merchant_789",
        "products": ["Premium Wireless Headphones"],
        "user_agent": "Mozilla/5.0...",
    }

    # Mock user context
    user_context = {
        "user_id": "user_abc123",
        "referrer_url": "https://example.com/article?lukhas_opp_id=opp_123&lukhas_pub_id=pub_456&lukhas_merchant_id=merchant_789&lukhas_timestamp=1640995200&lukhas_signature=abcdef123456",
        "current_url": "https://store.example.com/checkout/success",
        "session_history": [
            {"url": "https://example.com/article", "timestamp": "2024-01-01T10:00:00Z"},
            {
                "url": "https://store.example.com/product/headphones",
                "timestamp": "2024-01-01T10:05:00Z",
            },
            {"url": "https://store.example.com/checkout", "timestamp": "2024-01-01T10:15:00Z"},
        ],
    }

    # Perform attribution
    result = await attribution_ladder.attribute_conversion(conversion_event, user_context)

    print("Attribution Result:")
    print(f"  Method: {result.method.value}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Opportunity: {result.opportunity_id}")
    print(f"  Publisher: {result.publisher_id}")
    print(f"  Merchant: {result.merchant_id}")
    print(f"  Value: ${result.conversion_value_usd}")
    print(f"  Timestamp: {result.timestamp}")
    print(f"  Expires: {result.expires_at}")


if __name__ == "__main__":
    asyncio.run(main())
