#!/usr/bin/env python3
"""
NIΛS Dream Commerce System - Comprehensive Test Suite
Tests real OpenAI API integration with fictional data scenarios
Including edge cases that should trigger ethical blocks
"""

import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

from lambda_products_pack.lambda_core.NIAS.consent_manager import (
    AIGenerationType,
    ConsentLevel,
    ConsentManager,
    ConsentScope,
    DataSource,
)
from lambda_products_pack.lambda_core.NIAS.dream_commerce_orchestrator import (
    DreamCommerceOrchestrator,
)
from lambda_products_pack.lambda_core.NIAS.dream_generator import (
    BioRhythm,
    DreamContext,
    DreamGenerator,
    DreamMood,
)
from lambda_products_pack.lambda_core.NIAS.user_data_integrator import (
    UserDataIntegrator,
    UserDataProfile,
)
from lambda_products_pack.lambda_core.NIAS.vendor_portal import (
    VendorPortal,
    VendorTier,
)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent.parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("NIAS.Test")

# Import NIAS components


# Test data scenarios
class TestDataGenerator:
    """Generate realistic fictional test data"""

    @staticmethod
    def generate_user_profiles() -> list[dict[str, Any]]:
        """Generate diverse user profiles with different scenarios"""
        return [
            {
                "user_id": "test_user_happy",
                "name": "Sarah Johnson",
                "email": "sarah.j@example.com",
                "age": 32,
                "tier": "premium",
                "emotional_state": {
                    "joy": 0.7,
                    "calm": 0.6,
                    "stress": 0.2,  # Low stress - should allow delivery
                    "longing": 0.4,
                },
                "data": {
                    "email_snippets": [
                        "Subject: Your Amazon order has shipped - Winter boots",
                        "Subject: Reminder: Emma's birthday next week",
                        "Subject: Sale alert: 30% off at your favorite store",
                    ],
                    "shopping_cart": [
                        {
                            "item": "Cozy Cashmere Sweater",
                            "price": 189.99,
                            "added": "2 days ago",
                        },
                        {
                            "item": "Winter Boots",
                            "price": 220.00,
                            "added": "5 days ago",
                        },
                    ],
                    "calendar_events": [
                        {
                            "event": "Emma's Birthday Party",
                            "date": "2024-12-15",
                            "type": "celebration",
                        },
                        {
                            "event": "Holiday Shopping",
                            "date": "2024-12-20",
                            "type": "reminder",
                        },
                    ],
                    "browsing_history": [
                        "winter fashion trends 2024",
                        "best cashmere sweaters",
                        "gift ideas for best friend",
                    ],
                },
                "expected_result": "ALLOW - Normal happy user with shopping intent",
            },
            {
                "user_id": "test_user_stressed",
                "name": "Michael Chen",
                "email": "m.chen@example.com",
                "age": 45,
                "tier": "basic",
                "emotional_state": {
                    "joy": 0.2,
                    "calm": 0.1,
                    "stress": 0.9,  # HIGH STRESS - should block delivery
                    "longing": 0.3,
                },
                "data": {
                    "email_snippets": [
                        "Subject: URGENT: Credit card payment overdue",
                        "Subject: Final notice - Account suspended",
                        "Subject: Meeting canceled - Performance review",
                    ],
                    "shopping_cart": [],  # Empty cart
                    "calendar_events": [
                        {
                            "event": "Doctor appointment",
                            "date": "2024-12-10",
                            "type": "medical",
                        },
                        {
                            "event": "Loan payment due",
                            "date": "2024-12-12",
                            "type": "financial",
                        },
                    ],
                    "browsing_history": [
                        "debt consolidation",
                        "stress management techniques",
                        "unemployment benefits",
                    ],
                },
                "expected_result": "BLOCK - High stress, financial distress",
            },
            {
                "user_id": "test_user_minor",
                "name": "Jamie Wilson",
                "email": "jamie.w@example.com",
                "age": 11,  # MINOR - should trigger special protections
                "tier": "free",
                "emotional_state": {
                    "joy": 0.8,
                    "calm": 0.7,
                    "stress": 0.1,
                    "longing": 0.5,
                },
                "data": {
                    "email_snippets": [
                        "Subject: Roblox - Your weekly summary",
                        "Subject: School project reminder",
                    ],
                    "shopping_cart": [
                        {"item": "Pokemon Cards", "price": 29.99, "added": "1 day ago"}
                    ],
                    "calendar_events": [
                        {
                            "event": "Soccer practice",
                            "date": "2024-12-11",
                            "type": "sports",
                        },
                        {"event": "Math test", "date": "2024-12-13", "type": "school"},
                    ],
                    "browsing_history": [
                        "minecraft tutorials",
                        "pokemon card values",
                        "cool science experiments",
                    ],
                },
                "expected_result": "BLOCK - Minor user, requires parental consent",
            },
            {
                "user_id": "test_user_vulnerable",
                "name": "Patricia Martinez",
                "email": "p.martinez@example.com",
                "age": 67,
                "tier": "basic",
                "emotional_state": {
                    "joy": 0.3,
                    "calm": 0.4,
                    "stress": 0.5,
                    "longing": 0.8,  # High longing - potentially vulnerable
                },
                "data": {
                    "email_snippets": [
                        "Subject: Remember to take your medication",
                        "Subject: Social Security update",
                        "Subject: Lonely? Meet singles in your area",  # Potential scam
                    ],
                    "shopping_cart": [
                        {
                            "item": "Blood Pressure Monitor",
                            "price": 45.99,
                            "added": "3 days ago",
                        },
                        {
                            "item": "Reading Glasses",
                            "price": 32.00,
                            "added": "1 week ago",
                        },
                    ],
                    "calendar_events": [
                        {
                            "event": "Doctor checkup",
                            "date": "2024-12-14",
                            "type": "medical",
                        },
                        {
                            "event": "Pharmacy pickup",
                            "date": "2024-12-16",
                            "type": "medical",
                        },
                    ],
                    "browsing_history": [
                        "medicare plans",
                        "senior discounts",
                        "health supplements",
                    ],
                },
                "expected_result": "CAUTION - Elderly user, extra ethical checks needed",
            },
            {
                "user_id": "test_user_gambling",
                "name": "Robert Thompson",
                "email": "r.thompson@example.com",
                "age": 38,
                "tier": "premium",
                "emotional_state": {
                    "joy": 0.4,
                    "calm": 0.3,
                    "stress": 0.6,
                    "longing": 0.9,  # Very high longing
                },
                "data": {
                    "email_snippets": [
                        "Subject: You've won! Claim your prize now!",
                        "Subject: Last chance - Double your money",
                        "Subject: Exclusive casino bonus just for you",
                    ],
                    "shopping_cart": [],
                    "calendar_events": [
                        {
                            "event": "Gamblers Anonymous",
                            "date": "2024-12-12",
                            "type": "recovery",
                        }
                    ],
                    "browsing_history": [
                        "online poker",
                        "sports betting odds",
                        "gambling addiction help",  # Mixed signals
                    ],
                },
                "expected_result": "BLOCK - Gambling addiction indicators",
            },
        ]

    @staticmethod
    def generate_vendor_seeds() -> list[dict[str, Any]]:
        """Generate vendor dream seeds with various ethical levels"""
        return [
            {
                "vendor_name": "Comfort Clothing Co",
                "seed_data": {
                    "type": "seasonal",
                    "title": "Winter Warmth Collection",
                    "narrative": "As snowflakes dance outside your window, imagine wrapping yourself in clouds of cashmere, where comfort meets elegance in the quiet moments of winter...",
                    "emotional_triggers": {
                        "joy": 0.6,
                        "calm": 0.8,
                        "stress": 0.0,  # No stress - ethical
                        "longing": 0.4,
                    },
                    "product_data": {
                        "id": "CC-001",
                        "name": "Cloud Cashmere Sweater",
                        "price": 189.99,
                        "category": "apparel",
                    },
                    "offer_details": {
                        "discount": 20,
                        "code": "WINTER20",
                        "valid_days": 14,
                    },
                    "targeting_criteria": {
                        "interests": ["fashion", "comfort", "luxury"],
                        "age_min": 25,
                        "age_max": 65,
                    },
                },
                "expected_result": "APPROVE - Ethical, gentle marketing",
            },
            {
                "vendor_name": "QuickCash Loans",
                "seed_data": {
                    "type": "reminder",
                    "title": "URGENT: Money in 5 Minutes!",
                    "narrative": "ACT NOW! Don't miss this LIMITED TIME offer! Your financial problems END TODAY! Instant approval GUARANTEED!",
                    "emotional_triggers": {
                        "joy": 0.2,
                        "calm": 0.0,
                        "stress": 0.8,  # HIGH STRESS - unethical
                        "longing": 0.9,
                    },
                    "product_data": {
                        "id": "LOAN-999",
                        "name": "Instant Payday Loan",
                        "price": 500,
                        "category": "financial",
                    },
                    "offer_details": {
                        "apr": 400,  # Predatory rate
                        "terms": "hidden",
                        "valid_days": 1,
                    },
                    "targeting_criteria": {
                        "interests": ["debt", "loans", "financial help"],
                        "vulnerable_groups": True,  # Targeting vulnerable
                    },
                },
                "expected_result": "REJECT - Predatory, high stress, aggressive",
            },
            {
                "vendor_name": "Happy Toys",
                "seed_data": {
                    "type": "discovery",
                    "title": "Magical Adventures Await",
                    "narrative": "In a world of imagination, where dragons play and unicorns dance...",
                    "emotional_triggers": {
                        "joy": 0.9,
                        "calm": 0.5,
                        "stress": 0.0,
                        "longing": 0.3,
                    },
                    "product_data": {
                        "id": "TOY-123",
                        "name": "Adventure Playset",
                        "price": 49.99,
                        "category": "toys",
                    },
                    "offer_details": {"discount": 15, "code": "PLAY15"},
                    "targeting_criteria": {
                        "interests": ["toys", "games", "children"],
                        "age_min": 5,  # Targeting children
                        "age_max": 12,
                    },
                },
                "expected_result": "REJECT - Targets minors directly",
            },
            {
                "vendor_name": "Wellness Garden",
                "seed_data": {
                    "type": "replenishment",
                    "title": "Your Monthly Wellness Journey",
                    "narrative": "Like the gentle rhythm of waves, your wellness routine flows naturally. Time to replenish your favorite supplements...",
                    "emotional_triggers": {
                        "joy": 0.5,
                        "calm": 0.7,
                        "stress": 0.0,
                        "longing": 0.2,
                    },
                    "product_data": {
                        "id": "WG-789",
                        "name": "Organic Vitamin Bundle",
                        "price": 65.00,
                        "category": "health",
                    },
                    "offer_details": {
                        "subscription_discount": 20,
                        "free_shipping": True,
                    },
                    "targeting_criteria": {
                        "interests": ["health", "wellness", "supplements"],
                        "age_min": 30,
                        "age_max": 70,
                        "purchase_history": ["vitamins", "supplements"],
                    },
                },
                "expected_result": "APPROVE - Gentle reminder, wellness-focused",
            },
            {
                "vendor_name": "Lucky Casino",
                "seed_data": {
                    "type": "exclusive",
                    "title": "VIP Players Only - Double Your Luck!",
                    "narrative": "The cards are in your favor! Feel the rush! Win BIG tonight! Your lucky streak starts NOW!",
                    "emotional_triggers": {
                        "joy": 0.3,
                        "calm": 0.0,
                        "stress": 0.7,  # High stress
                        "longing": 1.0,  # Maximum longing - exploitative
                    },
                    "product_data": {
                        "id": "CASINO-777",
                        "name": "VIP Gambling Credits",
                        "price": 100,
                        "category": "gambling",
                    },
                    "offer_details": {
                        "bonus": "200%",
                        "wagering_requirement": "50x",  # Hidden trap
                    },
                    "targeting_criteria": {
                        "interests": ["gambling", "casino", "betting"],
                        "vulnerable_groups": True,
                    },
                },
                "expected_result": "REJECT - Gambling, exploitative, high stress",
            },
        ]


class NIASDreamCommerceTest:
    """Main test orchestrator for NIAS Dream Commerce System"""

    def __init__(self):
        self.consent_manager = ConsentManager()
        self.user_integrator = UserDataIntegrator(self.consent_manager)
        self.vendor_portal = VendorPortal(consent_manager=self.consent_manager)
        self.dream_generator = DreamGenerator()
        self.orchestrator = DreamCommerceOrchestrator()

        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "blocked_correctly": 0,
            "allowed_incorrectly": 0,
            "details": [],
        }

        # Check for OpenAI API key
        self.openai_available = os.getenv("OPENAI_API_KEY") is not None
        if not self.openai_available:
            logger.warning("⚠️  OpenAI API key not found. Will use fallback generation.")
            logger.info(
                "💡 To use real OpenAI generation, set OPENAI_API_KEY environment variable"
            )

    async def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "=" * 80)
        print("🧪 NIΛS DREAM COMMERCE SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 80 + "\n")

        if self.openai_available:
            print("✅ OpenAI API Key detected - Using real AI generation")
        else:
            print("⚠️  No OpenAI API Key - Using fallback generation")

        print("\n" + "-" * 80)
        print("📝 TEST SCENARIOS")
        print("-" * 80 + "\n")

        # 1. Test user consent flow
        await self.test_consent_management()

        # 2. Test vendor onboarding and seed creation
        await self.test_vendor_portal()

        # 3. Test dream generation with different emotional states
        await self.test_dream_generation()

        # 4. Test ethical blocking scenarios
        await self.test_ethical_blocks()

        # 5. Test end-to-end dream commerce flow
        await self.test_full_commerce_flow()

        # Print results
        self.print_test_results()

    async def test_consent_management(self):
        """Test consent management system"""
        print("\n🔐 TESTING CONSENT MANAGEMENT")
        print("-" * 40)

        test_user = "test_user_consent"

        # Test granting data source consent
        result = await self.consent_manager.grant_data_source_consent(
            test_user,
            [DataSource.EMAIL, DataSource.SHOPPING_HISTORY, DataSource.CALENDAR],
            {"purpose": "personalized_dreams", "retention_days": 30},
        )

        self.log_test("Grant data source consent", result, True)

        # Test AI generation consent
        result = await self.consent_manager.grant_ai_generation_consent(
            test_user,
            [AIGenerationType.NARRATIVE, AIGenerationType.IMAGE],
            ethical_checks=True,
            openai_api=True,
        )

        self.log_test("Grant AI generation consent", result, True)

        # Test vendor-specific consent
        result = await self.consent_manager.grant_vendor_consent(
            test_user,
            "vendor_test_123",
            {"view_profile": True, "send_dreams": True},
            [DataSource.SHOPPING_HISTORY],
        )

        self.log_test("Grant vendor consent", result, True)

        # Test consent checking
        result = await self.consent_manager.check_data_source_permission(
            test_user, DataSource.EMAIL
        )

        self.log_test("Check email permission", result, True)

        # Test denied permission
        result = await self.consent_manager.check_data_source_permission(
            test_user, DataSource.FINANCIAL  # Not granted
        )

        self.log_test("Check financial permission (not granted)", result, False)

        # Get comprehensive profile
        profile = await self.consent_manager.get_comprehensive_consent_profile(
            test_user
        )

        print("\n📊 Consent Profile Summary:")
        print(
            f"   - Data sources granted: {sum(1 for v in profile['data_sources'].values() if v)}"
        )
        print(
            f"   - AI generation enabled: {profile['ai_generation'].get('openai_api_enabled', False)}"
        )
        print(f"   - Vendors allowed: {len(profile['vendors'])}")

    async def test_vendor_portal(self):
        """Test vendor portal and seed creation"""
        print("\n\n🏪 TESTING VENDOR PORTAL")
        print("-" * 40)

        data_gen = TestDataGenerator()
        vendor_seeds = data_gen.generate_vendor_seeds()

        for vendor_data in vendor_seeds[:2]:  # Test first 2 vendors
            # Onboard vendor
            result = await self.vendor_portal.onboard_vendor(
                vendor_data["vendor_name"],
                [f"{vendor_data['vendor_name'].lower().replace(' ', '')}.com"],
                ["retail"],
                VendorTier.BASIC,
            )

            if "vendor_id" in result:
                vendor_id = result["vendor_id"]
                print(f"\n✅ Vendor onboarded: {vendor_data['vendor_name']}")
                print(f"   Vendor ID: {vendor_id}")
                print(f"   API Key: {result['api_key'][:20]}...")

                # Create dream seed
                seed_result = await self.vendor_portal.create_dream_seed(
                    vendor_id, vendor_data["seed_data"]
                )

                if "seed_id" in seed_result:
                    status = seed_result["status"]
                    ethical_score = seed_result["ethical_validation"].get("score", 0)

                    print("\n   📱 Dream Seed Created:")
                    print(f"      - Seed ID: {seed_result['seed_id']}")
                    print(f"      - Status: {status}")
                    print(f"      - Ethical Score: {ethical_score:.2f}")
                    print(f"      - Expected: {vendor_data['expected_result']}")

                    # Check if result matches expectation
                    if vendor_data["expected_result"].startswith("APPROVE"):
                        expected_approved = True
                    else:
                        expected_approved = False

                    actual_approved = status == "approved"

                    self.log_test(
                        f"Seed validation for {vendor_data['vendor_name']}",
                        actual_approved,
                        expected_approved,
                    )

    async def test_dream_generation(self):
        """Test dream generation with OpenAI"""
        print("\n\n🌙 TESTING DREAM GENERATION")
        print("-" * 40)

        if not self.openai_available:
            print("⚠️  Skipping OpenAI generation tests (no API key)")
            return

        # Create test context
        test_context = DreamContext(
            user_id="test_user_dreams",
            user_profile={
                "interests": ["fashion", "wellness", "technology"],
                "tier": "premium",
            },
            mood=DreamMood.SERENE,
            bio_rhythm=BioRhythm.EVENING_WIND,
            personal_data={
                "upcoming_events": [{"type": "birthday", "date": "2024-12-15"}],
                "interests": ["sustainable fashion", "meditation"],
            },
        )

        print("\n🎨 Generating dream with OpenAI...")
        dream = await self.dream_generator.generate_dream(test_context)

        print("\n✨ Generated Dream:")
        print(f"   Dream ID: {dream.dream_id}")
        print("\n   📝 Narrative (first 200 chars):")
        print(f"   '{dream.narrative[:200]}...'")
        print("\n   🎯 Emotional Profile:")
        for emotion, value in dream.emotional_profile.items():
            print(f"      - {emotion}: {value:.2f}")
        print(f"\n   🔮 Symbolism: {', '.join(dream.symbolism)}")
        print(f"   ⚖️  Ethical Score: {dream.ethical_score:.2f}")

        if dream.image_url:
            print(f"   🖼️  Image Generated: {dream.image_url[:50]}...")

        self.log_test("Dream generation", dream.dream_id is not None, True)
        self.log_test("Ethical score acceptable", dream.ethical_score >= 0.8, True)

    async def test_ethical_blocks(self):
        """Test scenarios that should trigger ethical blocks"""
        print("\n\n🛡️ TESTING ETHICAL BLOCKS")
        print("-" * 40)

        data_gen = TestDataGenerator()
        user_profiles = data_gen.generate_user_profiles()

        for profile in user_profiles:
            print(f"\n👤 Testing User: {profile['name']} (ID: {profile['user_id']})")
            print(f"   Age: {profile['age']}")
            print(
                f"   Emotional State: Stress={profile['emotional_state']['stress']:.1f}"
            )
            print(f"   Expected: {profile['expected_result']}")

            # Create user profile
            user_data = UserDataProfile(
                user_id=profile["user_id"],
                interests=["general"],
                shopping_patterns={},
                emotional_preferences=profile["emotional_state"],
                schedule_patterns={},
                spending_categories=[],
                brand_affinities={},
                dream_symbols=[],
                data_completeness=0.5,
            )

            # Add extra fields as attributes
            user_data.tier = profile["tier"]
            user_data.contextual_triggers = {}
            user_data.activity_patterns = {}
            user_data.preferences = {}
            user_data.current_context = {"emotional_state": profile["emotional_state"]}
            user_data.risk_factors = {}

            # Simulate adding user data
            self.user_integrator.user_profiles[profile["user_id"]] = user_data

            # Test dream commerce initiation
            result = await self.orchestrator.initiate_dream_commerce(profile["user_id"])

            print(f"   Result: {result['status']}")

            # Check if blocking worked correctly
            should_block = (
                "BLOCK" in profile["expected_result"]
                or "CAUTION" in profile["expected_result"]
            )
            was_blocked = result["status"] in [
                "deferred",
                "consent_required",
                "blocked",
            ]

            if should_block and was_blocked:
                print(f"   ✅ Correctly blocked: {result.get('reason', 'N/A')}")
                self.test_results["blocked_correctly"] += 1
            elif not should_block and not was_blocked:
                print("   ✅ Correctly allowed")
            else:
                print(
                    f"   ❌ Incorrect: Should {'block' if should_block else 'allow'}, but {'blocked' if was_blocked else 'allowed'}"
                )
                if not should_block and was_blocked:
                    self.test_results["allowed_incorrectly"] += 1

            self.log_test(
                f"Ethical check for {profile['name']}", was_blocked, should_block
            )

    async def test_full_commerce_flow(self):
        """Test complete end-to-end flow"""
        print("\n\n🔄 TESTING FULL COMMERCE FLOW")
        print("-" * 40)

        # 1. Create a safe test user
        test_user_id = "test_user_e2e"
        print(f"\n1️⃣ Creating test user: {test_user_id}")

        # 2. Grant consents
        await self.consent_manager.grant_consent(
            test_user_id, ConsentScope.GLOBAL, ConsentLevel.DREAM_AWARE
        )

        await self.consent_manager.grant_data_source_consent(
            test_user_id,
            [DataSource.EMAIL, DataSource.SHOPPING_HISTORY],
            {"purpose": "dream_commerce"},
        )

        await self.consent_manager.grant_ai_generation_consent(
            test_user_id, [AIGenerationType.NARRATIVE, AIGenerationType.IMAGE]
        )

        print("   ✅ Consents granted")

        # 3. Create user profile with safe emotional state
        user_profile = UserDataProfile(
            user_id=test_user_id,
            interests=["fashion", "wellness"],
            shopping_patterns={},
            emotional_preferences={
                "joy": 0.6,
                "calm": 0.7,
                "stress": 0.2,  # Low stress
                "longing": 0.3,
            },
            schedule_patterns={},
            spending_categories=["apparel", "wellness"],
            brand_affinities={},
            dream_symbols=[],
            data_completeness=0.7,
        )

        # Add extra fields as attributes
        user_profile.tier = "premium"
        user_profile.current_context = {
            "emotional_state": {
                "joy": 0.6,
                "calm": 0.7,
                "stress": 0.2,  # Low stress
                "longing": 0.3,
            }
        }
        user_profile.activity_patterns = {
            "recent_searches": ["winter fashion", "cozy sweaters"]
        }
        user_profile.contextual_triggers = {}
        user_profile.preferences = {}

        self.user_integrator.user_profiles[test_user_id] = user_profile
        print("   ✅ User profile created")

        # 4. Create a vendor and ethical seed
        vendor_result = await self.vendor_portal.onboard_vendor(
            "Test Fashion Co", ["testfashion.com"], ["apparel"], VendorTier.BASIC
        )

        if "vendor_id" in vendor_result:
            vendor_id = vendor_result["vendor_id"]
            print(f"   ✅ Vendor created: {vendor_id}")

            # 5. Create an ethical dream seed
            seed_result = await self.vendor_portal.create_dream_seed(
                vendor_id,
                {
                    "type": "seasonal",
                    "title": "Cozy Winter Dreams",
                    "narrative": "In the soft glow of winter mornings...",
                    "emotional_triggers": {
                        "joy": 0.6,
                        "calm": 0.8,
                        "stress": 0.0,
                        "longing": 0.3,
                    },
                    "product_data": {
                        "id": "TEST-001",
                        "name": "Dream Sweater",
                        "price": 99.99,
                    },
                    "offer_details": {"discount": 20},
                    "targeting_criteria": {
                        "interests": ["fashion"],
                        "age_min": 25,
                        "age_max": 65,
                    },
                },
            )

            if "seed_id" in seed_result:
                seed_id = seed_result["seed_id"]
                print(f"   ✅ Dream seed created: {seed_id}")

                # 6. Grant vendor consent
                await self.consent_manager.grant_vendor_consent(
                    test_user_id,
                    vendor_id,
                    {"send_dreams": True},
                    [DataSource.SHOPPING_HISTORY],
                )

                # 7. Initiate dream commerce
                init_result = await self.orchestrator.initiate_dream_commerce(
                    test_user_id
                )
                print("\n2️⃣ Dream Commerce Initiated:")
                print(f"   Status: {init_result['status']}")

                if init_result["status"] == "initiated":
                    print(f"   Session: {init_result['session_id']}")
                    print(f"   Bio-rhythm: {init_result.get('bio_rhythm', 'N/A')}")

                    # 8. Simulate user interaction
                    print("\n3️⃣ Simulating User Interaction:")

                    interaction_result = await self.orchestrator.process_user_action(
                        test_user_id,
                        "click",
                        {
                            "dream_id": "test_dream_123",
                            "seed_id": seed_id,
                            "vendor_id": vendor_id,
                            "product_id": "TEST-001",
                        },
                    )

                    print(
                        f"   Click tracked: {interaction_result.get('status', 'unknown')}"
                    )

                    if interaction_result.get("affiliate_link"):
                        print(
                            f"   Affiliate link: {interaction_result['affiliate_link'][:50]}..."
                        )
                        print(
                            f"   One-click ready: {interaction_result.get('one_click_ready', False)}"
                        )

                    # 9. Get system metrics
                    metrics = self.orchestrator.get_system_metrics()
                    print("\n4️⃣ System Metrics:")
                    print(f"   Active sessions: {metrics['active_sessions']}")
                    print(
                        f"   Dreams delivered: {metrics['metrics']['dreams_delivered']}"
                    )
                    print(f"   Ethical blocks: {metrics['metrics']['ethical_blocks']}")

                    self.log_test("End-to-end flow", True, True)
                else:
                    print(
                        f"   ⚠️  Could not initiate: {init_result.get('reason', 'unknown')}"
                    )
                    self.log_test("End-to-end flow", False, True)

    def log_test(self, test_name: str, result: Any, expected: Any):
        """Log test result"""
        self.test_results["total_tests"] += 1

        if result == expected:
            self.test_results["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["failed"] += 1
            status = "❌ FAIL"

        self.test_results["details"].append(
            {
                "test": test_name,
                "result": result,
                "expected": expected,
                "status": status,
            }
        )

        print(f"   {status}: {test_name}")

    def print_test_results(self):
        """Print comprehensive test results"""
        print("\n\n" + "=" * 80)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 80)

        print(f"\nTotal Tests Run: {self.test_results['total_tests']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        print(f"🛡️ Correctly Blocked: {self.test_results['blocked_correctly']}")
        print(f"⚠️  Incorrectly Allowed: {self.test_results['allowed_incorrectly']}")

        success_rate = (
            (self.test_results["passed"] / self.test_results["total_tests"] * 100)
            if self.test_results["total_tests"] > 0
            else 0
        )
        print(f"\n📈 Success Rate: {success_rate:.1f}%")

        if self.test_results["failed"] > 0:
            print("\n❌ Failed Tests:")
            for detail in self.test_results["details"]:
                if detail["status"] == "❌ FAIL":
                    print(f"   - {detail['test']}")
                    print(
                        f"     Expected: {detail['expected']}, Got: {detail['result']}"
                    )

        print("\n" + "=" * 80)

        # Save results to file
        results_file = "NIAS_TEST_RESULTS.json"
        with open(results_file, "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\n💾 Detailed results saved to: {results_file}")


async def main():
    """Main test runner"""
    print("\n🚀 Starting NIΛS Dream Commerce System Tests")
    print("=" * 80)

    # Check for OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  WARNING: No OpenAI API key found!")
        print("To test with real AI generation, set your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-your-api-key-here'")
        print("\nContinuing with fallback generation...\n")

        # Skip interactive prompt in automated testing
        # response = input("Would you like to enter your OpenAI API key now? (y/n): ")
        # if response.lower() == 'y':
        #     api_key = input("Enter your OpenAI API key: ")
        #     os.environ["OPENAI_API_KEY"] = api_key
        #     print("✅ API key set for this session")

    # Run tests
    tester = NIASDreamCommerceTest()
    await tester.run_all_tests()

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    asyncio.run(main())
