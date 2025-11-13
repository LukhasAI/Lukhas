"""
Comprehensive Unit Tests for LUKHAS Lambda ID Generator

Tests the tier-based Lambda ID generation system including:
- Basic generation functionality
- Tier-based requirements
- Collision handling
- Symbolic element selection
- Entropy generation
- Format compliance

Author: LUKHAS AI Systems
Created: 2025-11-12
"""

import re

# Import the Lambda ID components
import sys
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.append(str(Path(__file__).parent.parent.parent.parent))

from labs.governance.identity.core.id_service.lambd_id_generator import (
    LambdaIDGenerator,
    TierLevel,
    UserContext,
)


class TestLambdaIDGeneratorBasic(unittest.TestCase):
    """Test basic Lambda ID generation functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_generator_initialization(self):
        """Test that generator initializes correctly"""
        self.assertIsNotNone(self.generator)
        self.assertIsNotNone(self.generator.config)
        self.assertIsNotNone(self.generator.symbolic_chars)
        self.assertIsNotNone(self.generator.reserved_combinations)
        self.assertEqual(len(self.generator.generated_ids), 0)

    def test_generate_basic_lambda_id(self):
        """Test basic Lambda ID generation"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.GUEST)

        # Check format
        self.assertIsNotNone(lambda_id)
        self.assertTrue(lambda_id.startswith("LUKHAS"))

        # Check components
        parts = lambda_id.split("-")
        self.assertEqual(len(parts), 4)  # prefix+tier, timestamp, symbol, entropy

    def test_generate_all_tiers(self):
        """Test Lambda ID generation for all tier levels"""
        for tier in TierLevel:
            lambda_id = self.generator.generate_lambda_id(tier)

            # Verify format
            self.assertTrue(lambda_id.startswith(f"LUKHAS{tier.value}"))
            parts = lambda_id.split("-")
            self.assertEqual(len(parts), 4)

            # Verify tier encoding
            prefix = parts[0]
            self.assertEqual(prefix, f"LUKHAS{tier.value}")

    def test_format_compliance(self):
        """Test that generated IDs comply with format specification"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)

        # Regex pattern for format validation
        pattern = r"^LUKHAS[0-5]-[A-F0-9]{4}-.+-[A-F0-9]{4}$"
        self.assertIsNotNone(re.match(pattern, lambda_id),
                           f"Lambda ID {lambda_id} does not match expected format")

    def test_timestamp_hash_uniqueness(self):
        """Test that timestamp hashes are unique for rapid generation"""
        ids = set()
        for _ in range(100):
            lambda_id = self.generator.generate_lambda_id(TierLevel.GUEST)
            ids.add(lambda_id)

        # Should have high uniqueness (allowing for small collision probability)
        self.assertGreater(len(ids), 95, "Too many collisions in rapid generation")


class TestTierBasedGeneration(unittest.TestCase):
    """Test tier-specific generation features"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_tier_0_guest(self):
        """Test Tier 0 (GUEST) generation"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.GUEST)
        self.assertTrue(lambda_id.startswith("LUKHAS0"))

        # Verify symbolic character is tier-appropriate
        symbol = lambda_id.split("-")[2]
        tier_0_symbols = self.generator.symbolic_chars["tier_0"]
        self.assertIn(symbol, tier_0_symbols)

    def test_tier_2_friend(self):
        """Test Tier 2 (FRIEND) generation"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
        self.assertTrue(lambda_id.startswith("LUKHAS2"))

        # Verify symbolic character is tier-appropriate
        symbol = lambda_id.split("-")[2]
        tier_2_symbols = self.generator.symbolic_chars["tier_2"]
        self.assertIn(symbol, tier_2_symbols)

    def test_tier_5_root_dev(self):
        """Test Tier 5 (ROOT_DEV) generation"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.ROOT_DEV)
        self.assertTrue(lambda_id.startswith("LUKHAS5"))

        # Verify symbolic character is tier-appropriate
        symbol = lambda_id.split("-")[2]
        tier_5_symbols = self.generator.symbolic_chars["tier_5"]
        self.assertIn(symbol, tier_5_symbols)

    def test_symbolic_preference(self):
        """Test that symbolic preference is respected when valid"""
        preferred_symbol = "🌀"
        lambda_id = self.generator.generate_lambda_id(
            TierLevel.FRIEND,
            symbolic_preference=preferred_symbol
        )

        # Check that preferred symbol was used
        symbol = lambda_id.split("-")[2]
        self.assertEqual(symbol, preferred_symbol)

    def test_invalid_symbolic_preference_ignored(self):
        """Test that invalid symbolic preference is ignored"""
        # Try to use Tier 5 symbol for Tier 0
        invalid_symbol = "⟐"  # Tier 5 symbol
        lambda_id = self.generator.generate_lambda_id(
            TierLevel.GUEST,
            symbolic_preference=invalid_symbol
        )

        # Should fall back to tier-appropriate symbol
        symbol = lambda_id.split("-")[2]
        tier_0_symbols = self.generator.symbolic_chars["tier_0"]
        self.assertIn(symbol, tier_0_symbols)


class TestUserContextIntegration(unittest.TestCase):
    """Test user context integration in Lambda ID generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_basic_context(self):
        """Test generation with basic user context"""
        context = {
            "email": "user@example.com",
            "registration_time": time.time()
        }

        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND, context)
        self.assertIsNotNone(lambda_id)
        self.assertTrue(lambda_id.startswith("LUKHAS2"))

    def test_context_affects_entropy(self):
        """Test that different contexts produce different entropy"""
        context1 = {"email": "user1@example.com"}
        context2 = {"email": "user2@example.com"}

        # Generate multiple IDs with different contexts
        ids1 = set()
        ids2 = set()

        for _ in range(10):
            ids1.add(self.generator.generate_lambda_id(TierLevel.FRIEND, context1))
            ids2.add(self.generator.generate_lambda_id(TierLevel.FRIEND, context2))

        # Should have different IDs (no overlap expected)
        self.assertEqual(len(ids1 & ids2), 0, "Contexts should produce unique IDs")

    def test_empty_context(self):
        """Test generation with empty context (should still work)"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND, {})
        self.assertIsNotNone(lambda_id)


class TestCollisionHandling(unittest.TestCase):
    """Test collision detection and handling"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    @patch('time.time')
    @patch('secrets.token_hex')
    def test_collision_detection(self, mock_token_hex, mock_time):
        """Test that collisions are detected and handled"""
        # Force a collision by making timestamp and entropy deterministic
        mock_time.return_value = 1234567890.123
        mock_token_hex.return_value = "a" * 32  # Consistent entropy

        # Generate first ID
        id1 = self.generator.generate_lambda_id(TierLevel.GUEST)

        # Try to generate same ID (should detect collision and retry)
        id2 = self.generator.generate_lambda_id(TierLevel.GUEST)

        # IDs should be different due to collision handling
        self.assertNotEqual(id1, id2)

    def test_uniqueness_tracking(self):
        """Test that generated IDs are tracked for uniqueness"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
        self.assertIn(lambda_id, self.generator.generated_ids)

        # Generate more IDs
        for _ in range(10):
            new_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
            self.assertIn(new_id, self.generator.generated_ids)

        # Should have 11 unique IDs tracked
        self.assertEqual(len(self.generator.generated_ids), 11)


class TestEntropyGeneration(unittest.TestCase):
    """Test entropy hash generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_entropy_hash_format(self):
        """Test that entropy hash has correct format"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
        entropy_hash = lambda_id.split("-")[3]

        # Should be 4 character hexadecimal, uppercase
        self.assertEqual(len(entropy_hash), 4)
        self.assertTrue(all(c in "0123456789ABCDEF" for c in entropy_hash))

    def test_entropy_varies_by_tier(self):
        """Test that entropy varies by tier"""
        tier_entropies = {}

        for tier in TierLevel:
            lambda_id = self.generator.generate_lambda_id(tier)
            entropy = lambda_id.split("-")[3]
            tier_entropies[tier.value] = entropy

        # Entropies should be different for different tiers
        unique_entropies = len(set(tier_entropies.values()))
        self.assertGreater(unique_entropies, 3, "Tiers should produce varied entropy")

    def test_entropy_randomness(self):
        """Test that entropy hashes have good randomness"""
        entropies = set()
        for _ in range(100):
            lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
            entropy = lambda_id.split("-")[3]
            entropies.add(entropy)

        # Should have high uniqueness
        self.assertGreater(len(entropies), 95, "Entropy should be highly random")


class TestTimestampHashGeneration(unittest.TestCase):
    """Test timestamp hash generation"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_timestamp_hash_format(self):
        """Test that timestamp hash has correct format"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
        timestamp_hash = lambda_id.split("-")[1]

        # Should be 4 character hexadecimal, uppercase
        self.assertEqual(len(timestamp_hash), 4)
        self.assertTrue(all(c in "0123456789ABCDEF" for c in timestamp_hash))

    def test_timestamp_changes_over_time(self):
        """Test that timestamp hash changes over time"""
        id1 = self.generator.generate_lambda_id(TierLevel.FRIEND)
        time.sleep(0.001)  # Sleep 1ms
        id2 = self.generator.generate_lambda_id(TierLevel.FRIEND)

        timestamp1 = id1.split("-")[1]
        timestamp2 = id2.split("-")[1]

        # Timestamps should be different (or very rarely same due to collision)
        # Allow for rare collisions
        ids = [self.generator.generate_lambda_id(TierLevel.FRIEND) for _ in range(10)]
        timestamps = [id.split("-")[1] for id in ids]
        unique_timestamps = len(set(timestamps))

        self.assertGreater(unique_timestamps, 5, "Timestamps should vary over time")


class TestGenerationStatistics(unittest.TestCase):
    """Test generation statistics tracking"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_get_generation_stats(self):
        """Test that generation stats can be retrieved"""
        # Generate some IDs
        for _ in range(10):
            self.generator.generate_lambda_id(TierLevel.FRIEND)

        stats = self.generator.get_generation_stats()

        # Should track total generated
        self.assertIn("total_generated", stats)
        self.assertEqual(stats["total_generated"], 10)

    def test_stats_after_multiple_tiers(self):
        """Test stats after generating IDs for multiple tiers"""
        # Generate IDs for different tiers
        for tier in TierLevel:
            for _ in range(5):
                self.generator.generate_lambda_id(tier)

        stats = self.generator.get_generation_stats()
        # Should have generated 30 IDs (5 per tier, 6 tiers)
        self.assertEqual(stats["total_generated"], 30)


class TestReservedCombinations(unittest.TestCase):
    """Test reserved combination handling"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_reserved_combinations_loaded(self):
        """Test that reserved combinations are loaded"""
        self.assertIsNotNone(self.generator.reserved_combinations)
        self.assertGreater(len(self.generator.reserved_combinations), 0)

    def test_system_reserved_id(self):
        """Test that system reserved IDs are recognized"""
        reserved = "Λ0-0000-○-0000"
        self.assertIn(reserved, self.generator.reserved_combinations)

    def test_admin_reserved_id(self):
        """Test that admin reserved IDs are recognized"""
        reserved = "Λ5-FFFF-⟐-FFFF"
        self.assertIn(reserved, self.generator.reserved_combinations)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = LambdaIDGenerator()

    def test_rapid_generation(self):
        """Test rapid generation (stress test)"""
        ids = set()
        for _ in range(1000):
            lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND)
            ids.add(lambda_id)

        # Should have very high uniqueness
        self.assertGreater(len(ids), 990, "Rapid generation should maintain uniqueness")

    def test_context_with_special_characters(self):
        """Test context with special characters"""
        context = {
            "email": "test+user@example.com",
            "name": "User O'Brien",
            "data": "Special chars: 你好, مرحبا, שלום"
        }

        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND, context)
        self.assertIsNotNone(lambda_id)

    def test_large_context(self):
        """Test with large user context"""
        context = {
            f"field_{i}": f"value_{i}" * 100
            for i in range(100)
        }

        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND, context)
        self.assertIsNotNone(lambda_id)

    def test_none_context(self):
        """Test with None context (should use empty dict)"""
        lambda_id = self.generator.generate_lambda_id(TierLevel.FRIEND, None)
        self.assertIsNotNone(lambda_id)


class TestUserContextClass(unittest.TestCase):
    """Test UserContext helper class"""

    def test_user_context_creation(self):
        """Test UserContext object creation"""
        context = UserContext(user_id="user123", metadata={"email": "test@example.com"})
        self.assertEqual(context.user_id, "user123")
        self.assertEqual(context.metadata["email"], "test@example.com")

    def test_user_context_to_dict(self):
        """Test UserContext serialization"""
        context = UserContext(user_id="user123", metadata={"email": "test@example.com"})
        context_dict = context.to_dict()

        self.assertIn("user_id", context_dict)
        self.assertIn("metadata", context_dict)
        self.assertEqual(context_dict["user_id"], "user123")


if __name__ == "__main__":
    unittest.main(verbosity=2)
