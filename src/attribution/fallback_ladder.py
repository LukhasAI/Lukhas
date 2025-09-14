#!/usr/bin/env python3
"""
Attribution Fallback Ladder
Multi-tier attribution system with S2S postback and receipt matching
Ensures accurate revenue attribution even when primary methods fail
"""

import asyncio
import hashlib
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional

import aiohttp

logger = logging.getLogger(__name__)


class AttributionMethod(Enum):
    """Attribution methods in priority order (highest to lowest confidence)"""

    AFFILIATE_LINK = "affiliate_link"  # Primary: Direct affiliate tracking
    S2S_POSTBACK = "s2s_postback"  # Secondary: Server-to-server postback
    RECEIPT_MATCHING = "receipt_matching"  # Tertiary: Email receipt matching
    BEHAVIORAL_INFERENCE = "behavioral_inference"  # Fallback: Pattern-based inference
    LAST_TOUCH = "last_touch"  # Last resort: Time-based attribution


@dataclass
class AttributionAttempt:
    """Single attribution attempt with confidence score"""

    method: AttributionMethod
    confidence: float  # 0.0 to 1.0
    attribution_data: dict[str, Any]
    timestamp: float
    user_id: Optional[str] = None
    opportunity_id: Optional[str] = None
    conversion_id: Optional[str] = None
    success: bool = False
    error_reason: Optional[str] = None


@dataclass
class AttributionResult:
    """Final attribution result after fallback ladder"""

    method_used: AttributionMethod
    confidence: float
    user_id: str
    opportunity_id: str
    conversion_id: str
    attribution_data: dict[str, Any]
    fallback_attempts: list[AttributionAttempt]
    total_processing_time: float
    receipt_id: Optional[str] = None


class AttributionFallbackLadder:
    """
    Multi-tier attribution system with graceful degradation

    Attribution Priority:
    1. Affiliate Link (0.95+ confidence) - Direct click tracking
    2. S2S Postback (0.85+ confidence) - Server-to-server verification
    3. Receipt Matching (0.75+ confidence) - Email receipt correlation
    4. Behavioral Inference (0.60+ confidence) - ML pattern matching
    5. Last Touch (0.40+ confidence) - Time-based fallback
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.confidence_thresholds = {
            AttributionMethod.AFFILIATE_LINK: 0.95,
            AttributionMethod.S2S_POSTBACK: 0.85,
            AttributionMethod.RECEIPT_MATCHING: 0.75,
            AttributionMethod.BEHAVIORAL_INFERENCE: 0.60,
            AttributionMethod.LAST_TOUCH: 0.40,
        }

        # Initialize service connections
        self.session = None
        self.receipt_matcher = ReceiptMatcher(config.get("receipt_matching", {}))
        # Initialize behavioral analyzer (fixed corrupted identifier)
        self.behavioral_analyzer = BehavioralAnalyzer(config.get("behavioral_analysis", {}))

    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    async def attribute_conversion(self, conversion_data: dict[str, Any], context: dict[str, Any]) -> AttributionResult:
        """
        Main attribution function - tries methods in priority order

        Args:
            conversion_data: Purchase/conversion details
            context: Additional context (user session, timestamps, etc.)

        Returns:
            AttributionResult with best available attribution
        """
        start_time = time.time()
        attempts = []

        # Extract key identifiers
        user_id = conversion_data.get("user_id")
        order_id = conversion_data.get("order_id")
        conversion_data.get("amount", 0)
        conversion_data.get("timestamp", time.time())

        # Try each attribution method in priority order
        attribution_methods = [
            (AttributionMethod.AFFILIATE_LINK, self._try_affiliate_attribution),
            (AttributionMethod.S2S_POSTBACK, self._try_s2s_postback),
            (AttributionMethod.RECEIPT_MATCHING, self._try_receipt_matching),
            (AttributionMethod.BEHAVIORAL_INFERENCE, self._try_behavioral_inference),
            (AttributionMethod.LAST_TOUCH, self._try_last_touch_attribution),
        ]

        for method, handler in attribution_methods:
            try:
                logger.info(f"Attempting attribution via {method.value}")

                attempt = await handler(conversion_data, context)
                attempts.append(attempt)

                # Check if attempt meets confidence threshold
                threshold = self.confidence_thresholds[method]

                if attempt.success and attempt.confidence >= threshold:
                    logger.info(f"Attribution successful via {method.value} (confidence: {attempt.confidence:.3f})")

                    return AttributionResult(
                        method_used=method,
                        confidence=attempt.confidence,
                        user_id=attempt.user_id or user_id,
                        opportunity_id=attempt.opportunity_id,
                        conversion_id=attempt.conversion_id,
                        attribution_data=attempt.attribution_data,
                        fallback_attempts=attempts,
                        total_processing_time=time.time() - start_time,
                    )

                logger.info(f"Attribution via {method.value} below threshold (confidence: {attempt.confidence:.3f})")

            except Exception as e:
                logger.error(f"Attribution method {method.value} failed: {e!s}")
                attempts.append(
                    AttributionAttempt(
                        method=method,
                        confidence=0.0,
                        attribution_data={},
                        timestamp=time.time(),
                        success=False,
                        error_reason=str(e),
                    )
                )

        # If all methods fail, create a fallback result
        logger.warning("All attribution methods failed, creating fallback result")

        return AttributionResult(
            method_used=AttributionMethod.LAST_TOUCH,
            confidence=0.1,  # Very low confidence
            user_id=user_id,
            opportunity_id="unknown",
            conversion_id=f"fallback_{order_id}",
            attribution_data={"fallback_reason": "all_methods_failed"},
            fallback_attempts=attempts,
            total_processing_time=time.time() - start_time,
        )

    async def _try_affiliate_attribution(self, conversion_data, context) -> AttributionAttempt:
        """
        Primary: Direct affiliate link attribution
        Highest confidence when click tracking parameters are present
        """

        # Look for affiliate tracking parameters
        affiliate_params = context.get("affiliate_params", {})
        referrer = context.get("referrer", "")
        click_id = context.get("click_id")

        if not (affiliate_params or click_id or "lukhas" in referrer.lower()):
            return AttributionAttempt(
                method=AttributionMethod.AFFILIATE_LINK,
                confidence=0.0,
                attribution_data={},
                timestamp=time.time(),
                success=False,
                error_reason="No affiliate tracking parameters found",
            )

        # Extract attribution data
        attribution_data = {
            "click_id": click_id,
            "affiliate_params": affiliate_params,
            "referrer": referrer,
            "tracking_method": "direct_affiliate",
        }

        # Calculate confidence based on data quality
        confidence = 0.95  # Base confidence for affiliate links

        if not click_id:
            confidence -= 0.1  # Reduce if no click ID
        if not affiliate_params.get("campaign_id"):
            confidence -= 0.05  # Reduce if no campaign ID
        if not affiliate_params.get("source"):
            confidence -= 0.05  # Reduce if no source

        # Verify click timestamp is recent (within 30 days)
        click_timestamp = affiliate_params.get("timestamp")
        if click_timestamp:
            click_age_hours = (time.time() - click_timestamp) / 3600
            if click_age_hours > 24 * 30:  # Older than 30 days
                confidence -= 0.2

        return AttributionAttempt(
            method=AttributionMethod.AFFILIATE_LINK,
            confidence=max(confidence, 0.0),
            attribution_data=attribution_data,
            timestamp=time.time(),
            user_id=conversion_data.get("user_id"),
            opportunity_id=affiliate_params.get("opportunity_id"),
            conversion_id=f"affiliate_{conversion_data.get('order_id')}",
            success=confidence >= self.confidence_thresholds[AttributionMethod.AFFILIATE_LINK],
        )

    async def _try_s2s_postback(self, conversion_data, context) -> AttributionAttempt:
        """
        Secondary: Server-to-server postback verification
        High confidence when merchant confirms the conversion
        """

        # Prepare S2S postback request
        postback_data = {
            "conversion_id": conversion_data.get("order_id"),
            "user_id": conversion_data.get("user_id"),
            "amount": conversion_data.get("amount"),
            "timestamp": conversion_data.get("timestamp"),
            "verification_token": self._generate_verification_token(conversion_data),
        }

        # Try to verify with merchant S2S endpoint
        merchant_endpoint = context.get("merchant_s2s_endpoint")
        if not merchant_endpoint:
            return AttributionAttempt(
                method=AttributionMethod.S2S_POSTBACK,
                confidence=0.0,
                attribution_data={},
                timestamp=time.time(),
                success=False,
                error_reason="No merchant S2S endpoint configured",
            )

        try:
            async with self.session.post(
                merchant_endpoint,
                json=postback_data,
                headers={"Authorization": f"Bearer {self.config.get('s2s_token')}"},
            ) as response:
                if response.status == 200:
                    s2s_response = await response.json()

                    attribution_data = {
                        "s2s_verified": True,
                        "merchant_confirmation": s2s_response,
                        "verification_token": postback_data["verification_token"],
                        "tracking_method": "s2s_postback",
                    }

                    # High confidence for successful S2S verification
                    confidence = 0.90

                    # Boost confidence if merchant provides additional data
                    if s2s_response.get("opportunity_id"):
                        confidence = 0.95
                        attribution_data["opportunity_id"] = s2s_response["opportunity_id"]

                    return AttributionAttempt(
                        method=AttributionMethod.S2S_POSTBACK,
                        confidence=confidence,
                        attribution_data=attribution_data,
                        timestamp=time.time(),
                        user_id=conversion_data.get("user_id"),
                        opportunity_id=s2s_response.get("opportunity_id"),
                        conversion_id=f"s2s_{conversion_data.get('order_id')}",
                        success=True,
                    )

                else:
                    error_text = await response.text()
                    return AttributionAttempt(
                        method=AttributionMethod.S2S_POSTBACK,
                        confidence=0.0,
                        attribution_data={},
                        timestamp=time.time(),
                        success=False,
                        error_reason=f"S2S verification failed: {response.status} - {error_text}",
                    )

        except Exception as e:
            return AttributionAttempt(
                method=AttributionMethod.S2S_POSTBACK,
                confidence=0.0,
                attribution_data={},
                timestamp=time.time(),
                success=False,
                error_reason=f"S2S request failed: {e!s}",
            )

    async def _try_receipt_matching(self, conversion_data, context) -> AttributionAttempt:
        """
        Tertiary: Email receipt matching
        Medium confidence based on email content correlation
        """

        try:
            receipt_result = await self.receipt_matcher.match_purchase_receipt(
                user_id=conversion_data.get("user_id"),
                order_id=conversion_data.get("order_id"),
                amount=conversion_data.get("amount"),
                merchant=conversion_data.get("merchant"),
                timestamp_window=context.get("receipt_window_hours", 24),
            )

            if receipt_result["matched"]:
                attribution_data = {
                    "receipt_matched": True,
                    "receipt_details": receipt_result["receipt"],
                    "match_confidence": receipt_result["confidence"],
                    "tracking_method": "receipt_matching",
                }

                # Confidence based on receipt match quality
                confidence = receipt_result["confidence"] * 0.85  # Max 85% for receipt matching

                return AttributionAttempt(
                    method=AttributionMethod.RECEIPT_MATCHING,
                    confidence=confidence,
                    attribution_data=attribution_data,
                    timestamp=time.time(),
                    user_id=conversion_data.get("user_id"),
                    opportunity_id=receipt_result.get("opportunity_id"),
                    conversion_id=f"receipt_{conversion_data.get('order_id')}",
                    success=confidence >= self.confidence_thresholds[AttributionMethod.RECEIPT_MATCHING],
                )

            else:
                return AttributionAttempt(
                    method=AttributionMethod.RECEIPT_MATCHING,
                    confidence=0.0,
                    attribution_data={},
                    timestamp=time.time(),
                    success=False,
                    error_reason="No matching receipt found",
                )

        except Exception as e:
            return AttributionAttempt(
                method=AttributionMethod.RECEIPT_MATCHING,
                confidence=0.0,
                attribution_data={},
                timestamp=time.time(),
                success=False,
                error_reason=f"Receipt matching failed: {e!s}",
            )

    async def _try_behavioral_inference(self, conversion_data, context) -> AttributionAttempt:
        """
        Quaternary: Behavioral pattern inference
        Medium-low confidence based on user behavior analysis
        """

        try:
            behavioral_result = await self.behavioral_analyzer.infer_attribution(
                user_id=conversion_data.get("user_id"),
                purchase_data=conversion_data,
                context=context,
            )

            if behavioral_result["attribution_likely"]:
                attribution_data = {
                    "behavioral_signals": behavioral_result["signals"],
                    "pattern_match": behavioral_result["pattern"],
                    "inference_confidence": behavioral_result["confidence"],
                    "tracking_method": "behavioral_inference",
                }

                # Confidence capped at 70% for behavioral inference
                confidence = min(behavioral_result["confidence"], 0.70)

                return AttributionAttempt(
                    method=AttributionMethod.BEHAVIORAL_INFERENCE,
                    confidence=confidence,
                    attribution_data=attribution_data,
                    timestamp=time.time(),
                    user_id=conversion_data.get("user_id"),
                    opportunity_id=behavioral_result.get("opportunity_id"),
                    conversion_id=f"behavioral_{conversion_data.get('order_id')}",
                    success=confidence >= self.confidence_thresholds[AttributionMethod.BEHAVIORAL_INFERENCE],
                )

            else:
                return AttributionAttempt(
                    method=AttributionMethod.BEHAVIORAL_INFERENCE,
                    confidence=0.0,
                    attribution_data={},
                    timestamp=time.time(),
                    success=False,
                    error_reason="No behavioral attribution pattern detected",
                )

        except Exception as e:
            return AttributionAttempt(
                method=AttributionMethod.BEHAVIORAL_INFERENCE,
                confidence=0.0,
                attribution_data={},
                timestamp=time.time(),
                success=False,
                error_reason=f"Behavioral inference failed: {e!s}",
            )

    async def _try_last_touch_attribution(self, conversion_data, context) -> AttributionAttempt:
        """
        Last resort: Time-based attribution
        Low confidence but always succeeds as fallback
        """

        # Use any available context data for last touch attribution
        attribution_data = {
            "last_interaction_time": context.get("last_lukhas_interaction"),
            "session_data": context.get("session_data", {}),
            "tracking_method": "last_touch_fallback",
        }

        # Base confidence for last touch (always low)
        confidence = 0.45

        # Reduce confidence if interaction was too long ago
        last_interaction = context.get("last_lukhas_interaction")
        if last_interaction:
            hours_since_interaction = (time.time() - last_interaction) / 3600
            if hours_since_interaction > 168:  # More than 1 week
                confidence = 0.30
            elif hours_since_interaction > 72:  # More than 3 days
                confidence = 0.35
        else:
            confidence = 0.25  # No interaction data

        return AttributionAttempt(
            method=AttributionMethod.LAST_TOUCH,
            confidence=confidence,
            attribution_data=attribution_data,
            timestamp=time.time(),
            user_id=conversion_data.get("user_id"),
            opportunity_id="unknown",
            conversion_id=f"lasttouch_{conversion_data.get('order_id')}",
            success=True,  # Last touch always succeeds
        )

    def _generate_verification_token(self, conversion_data: dict[str, Any]) -> str:
        """Generate secure verification token for S2S postback"""

        token_data = (
            f"{conversion_data.get('order_id')}:{conversion_data.get('amount')}:{self.config.get('s2s_secret')}"
        )
        return hashlib.sha256(token_data.encode()).hexdigest()[:16]


class ReceiptMatcher:
    """
    Email receipt matching system
    Correlates purchase receipts with LUKHAS interactions
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.email_connectors = {}  # Gmail, Outlook, etc. connectors

    async def match_purchase_receipt(
        self, user_id: str, order_id: str, amount: float, merchant: str, timestamp_window: int = 24
    ) -> dict[str, Any]:
        """
        Match purchase against email receipts
        """

        # Search for receipt emails within time window
        search_params = {
            "user_id": user_id,
            "merchant": merchant,
            "amount_range": (amount * 0.95, amount * 1.05),  # 5% tolerance
            "time_window_hours": timestamp_window,
        }

        receipt_results = await self._search_receipt_emails(search_params)

        if not receipt_results:
            return {"matched": False, "confidence": 0.0}

        # Score receipt matches
        best_match = None
        best_score = 0.0

        for receipt in receipt_results:
            score = self._score_receipt_match(receipt, order_id, amount, merchant)
            if score > best_score:
                best_score = score
                best_match = receipt

        if best_score > 0.6:  # Minimum match threshold
            # Check if receipt contains LUKHAS attribution markers
            lukhas_attribution = self._extract_lukhas_attribution(best_match)

            return {
                "matched": True,
                "confidence": best_score,
                "receipt": best_match,
                "opportunity_id": lukhas_attribution.get("opportunity_id"),
                "attribution_markers": lukhas_attribution,
            }

        return {"matched": False, "confidence": best_score}

    async def _search_receipt_emails(self, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Search user's email for purchase receipts"""

        # This would integrate with Gmail/Outlook APIs
        # For now, return mock data
        return [
            {
                "subject": f"Receipt from {params['merchant']}",
                "body": f"Order total: ${params['amount_range'][0]:.2f}",
                "timestamp": time.time() - 3600,
                "sender": f"noreply@{params['merchant'].lower()}.com",
            }
        ]

    def _score_receipt_match(self, receipt: dict[str, Any], order_id: str, amount: float, merchant: str) -> float:
        """Score how well receipt matches purchase data"""

        score = 0.0

        # Merchant match
        if merchant.lower() in receipt.get("sender", "").lower():
            score += 0.3
        if merchant.lower() in receipt.get("subject", "").lower():
            score += 0.2

        # Amount match (with tolerance)
        receipt_amounts = self._extract_amounts_from_receipt(receipt)
        for receipt_amount in receipt_amounts:
            if abs(receipt_amount - amount) / amount < 0.05:  # Within 5%
                score += 0.4
                break

        # Order ID match
        if order_id in receipt.get("body", ""):
            score += 0.3

        return min(score, 1.0)

    def _extract_amounts_from_receipt(self, receipt: dict[str, Any]) -> list[float]:
        """Extract monetary amounts from receipt text"""

        import re

        text = receipt.get("body", "") + " " + receipt.get("subject", "")

        # Regex pattern for currency amounts
        amount_pattern = r"\$\s*(\d+(?:,\d{3})*\.?\d*)"
        matches = re.findall(amount_pattern, text)

        amounts = []
        for match in matches:
            try:
                amount = float(match.replace(",", ""))
                amounts.append(amount)
            except ValueError:
                continue

        return amounts

    def _extract_lukhas_attribution(self, receipt: dict[str, Any]) -> dict[str, Any]:
        """Extract LUKHAS attribution markers from receipt"""

        text = receipt.get("body", "")

        attribution = {}

        # Look for common attribution patterns
        if "lukhas" in text.lower():
            attribution["lukhas_mention"] = True

        # Look for opportunity ID patterns
        import re

        opp_match = re.search(r"opp_[a-zA-Z0-9_]+", text)
        if opp_match:
            attribution["opportunity_id"] = opp_match.group()

        return attribution


class BehavioralAnalyzer:
    """
    Behavioral pattern analysis for attribution inference
    Uses ML patterns to infer likely LUKHAS attribution
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config

    async def infer_attribution(
        self, user_id: str, purchase_data: dict[str, Any], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Infer attribution based on behavioral patterns
        """

        # Collect behavioral signals
        signals = await self._collect_behavioral_signals(user_id, purchase_data)

        # Analyze patterns
        pattern_score = self._analyze_attribution_patterns(signals, purchase_data)

        if pattern_score > 0.6:
            return {
                "attribution_likely": True,
                "confidence": pattern_score,
                "signals": signals,
                "pattern": "lukhas_influenced_purchase",
                "opportunity_id": signals.get("likely_opportunity_id"),
            }

        return {
            "attribution_likely": False,
            "confidence": pattern_score,
            "signals": signals,
            "pattern": "no_clear_pattern",
        }

    async def _collect_behavioral_signals(self, user_id: str, purchase_data: dict[str, Any]) -> dict[str, Any]:
        """Collect behavioral signals for analysis"""

        # This would query user behavior databases
        # For now, return mock signals
        return {
            "recent_lukhas_interactions": 3,
            "product_views_before_purchase": 5,
            "time_between_last_interaction_and_purchase": 7200,  # 2 hours
            "similar_product_interactions": True,
            "price_comparison_behavior": True,
            "typical_purchase_pattern": "research_then_buy",
        }

    def _analyze_attribution_patterns(self, signals: dict[str, Any], purchase_data: dict[str, Any]) -> float:
        """Analyze behavioral patterns for attribution likelihood"""

        score = 0.0

        # Recent interactions boost score
        recent_interactions = signals.get("recent_lukhas_interactions", 0)
        if recent_interactions > 0:
            score += min(recent_interactions * 0.1, 0.3)

        # Product research behavior
        if signals.get("product_views_before_purchase", 0) > 2:
            score += 0.2

        # Time proximity
        time_gap = signals.get("time_between_last_interaction_and_purchase", float("inf"))
        if time_gap < 3600:  # Within 1 hour
            score += 0.3
        elif time_gap < 24 * 3600:  # Within 24 hours
            score += 0.2

        # Similar product interactions
        if signals.get("similar_product_interactions"):
            score += 0.15

        # Price comparison behavior (indicates research/consideration)
        if signals.get("price_comparison_behavior"):
            score += 0.1

        return min(score, 1.0)


# Usage Example and Testing
async def main():
    """Example usage of attribution fallback ladder"""

    config = {
        "s2s_token": "test_token_123",
        "s2s_secret": "test_secret_456",
        "receipt_matching": {"enabled": True, "email_providers": ["gmail", "outlook"]},
        "behavioral_analysis": {"enabled": True, "confidence_threshold": 0.6},
    }

    async with AttributionFallbackLadder(config) as attribution:
        # Test conversion data
        conversion_data = {
            "user_id": "lukhas_user_12345",
            "order_id": "order_67890",
            "amount": 299.99,
            "merchant": "TechStore",
            "timestamp": time.time(),
        }

        # Test context data
        context = {
            "affiliate_params": {
                "campaign_id": "summer_sale_2024",
                "source": "lukhas_nias",
                "opportunity_id": "opp_tech_headphones_123",
                "timestamp": time.time() - 1800,  # 30 minutes ago
            },
            "click_id": "click_abcdef123456",
            "referrer": "https://lukhas.ai/r/tech-headphones",
            "session_data": {"device": "desktop", "browser": "chrome"},
            "last_lukhas_interaction": time.time() - 3600,  # 1 hour ago
            "merchant_s2s_endpoint": "https://techstore.com/api/lukhas/verify",
        }

        # Run attribution
        result = await attribution.attribute_conversion(conversion_data, context)

        print("Attribution Result:")
        print(f"  Method: {result.method_used.value}")
        print(f"  Confidence: {result.confidence:.3f}")
        print(f"  User ID: {result.user_id}")
        print(f"  Opportunity ID: {result.opportunity_id}")
        print(f"  Processing Time: {result.total_processing_time:.3f}s")
        print(f"  Attempts Made: {len(result.fallback_attempts)}")

        for i, attempt in enumerate(result.fallback_attempts):
            print(
                f"  Attempt {i + 1}: {attempt.method.value} - {attempt.confidence:.3f} - {'✓' if attempt.success else '✗'}"
            )


if __name__ == "__main__":
    asyncio.run(main())
