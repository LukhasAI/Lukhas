"""
Test suite for core/identity/manager.py - AdvancedIdentityManager and components
Following AUTONOMOUS_GUIDE_TEST_COVERAGE.md Phase 4: Systematic Test Writing

COVERAGE TARGET: 75%+ for core/identity/manager.py
PRIORITY: HIGH (critical identity and authentication system with emotional memory)

Test Categories:
1. EmotionalMemoryVector tests
2. SymbolicIdentityHash tests  
3. TraumaLock tests
4. AdvancedIdentityManager tests
5. Authentication and registration tests
6. Privacy and security tests
"""
import asyncio
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

from core.identity.manager import (
    AdvancedIdentityManager,
    EmotionalMemoryVector,
    SymbolicIdentityHash,
    TraumaLock,
)


class TestEmotionalMemoryVector:
    """Test EmotionalMemoryVector functionality."""

    def test_init(self):
        """Test EmotionalMemoryVector initialization."""
        emv = EmotionalMemoryVector()

        assert emv.vectors == {}
        assert emv.decay_rate == 0.05
        assert emv.memory_retention == 100

    def test_extract_vector_basic(self):
        """Test basic emotional vector extraction."""
        emv = EmotionalMemoryVector()
        user_input = {"text": "I am happy and excited about this"}

        vector = emv.extract_vector(user_input)

        assert isinstance(vector, dict)
        assert "valence" in vector
        assert "arousal" in vector
        assert "dominance" in vector
        assert "trust" in vector
        assert "timestamp" in vector

        # Should have positive valence for "happy"
        assert vector["valence"] > 0

    def test_extract_vector_positive_sentiment(self):
        """Test extraction of positive emotional content."""
        emv = EmotionalMemoryVector()
        user_input = {"text": "This is great! I love it and feel excellent"}

        vector = emv.extract_vector(user_input)

        # Should have high positive valence
        assert vector["valence"] > 0.4

    def test_extract_vector_negative_sentiment(self):
        """Test extraction of negative emotional content."""
        emv = EmotionalMemoryVector()
        user_input = {"text": "This is terrible and awful, I hate it"}

        vector = emv.extract_vector(user_input)

        # Should have negative valence
        assert vector["valence"] < 0

    def test_update_vector_new_user(self):
        """Test updating vector for new user."""
        emv = EmotionalMemoryVector()
        user_id = "test_user"
        test_vector = {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.5,
            "trust": 0.7,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        emv.update_vector(user_id, test_vector)

        assert user_id in emv.vectors
        assert len(emv.vectors[user_id]["history"]) == 1
        assert emv.vectors[user_id]["history"][0] == test_vector
        assert emv.vectors[user_id]["composite"]["valence"] == 0.5

    def test_get_vector_existing_user(self):
        """Test getting vector for existing user."""
        emv = EmotionalMemoryVector()
        user_id = "test_user"
        test_vector = {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.5,
            "trust": 0.7,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        emv.update_vector(user_id, test_vector)
        retrieved = emv.get_vector(user_id)

        assert retrieved is not None
        assert retrieved["valence"] == 0.5

    def test_get_vector_nonexistent_user(self):
        """Test getting vector for non-existent user."""
        emv = EmotionalMemoryVector()

        retrieved = emv.get_vector("nonexistent_user")

        assert retrieved is None


class TestSymbolicIdentityHash:
    """Test SymbolicIdentityHash functionality."""

    def test_init(self):
        """Test SymbolicIdentityHash initialization."""
        sih = SymbolicIdentityHash()

        assert sih.identity_hashes == {}
        assert sih.salt is not None
        assert sih.hash_version == 1

    def test_create_hash_valid_input(self):
        """Test hash creation with valid emotional vector."""
        sih = SymbolicIdentityHash()
        emotional_vector = {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.5,
            "trust": 0.7
        }

        hash_data = sih.create_hash(emotional_vector)

        assert hash_data is not None
        assert "hash" in hash_data
        assert "version" in hash_data
        assert "created" in hash_data
        assert len(hash_data["hash"]) == 64  # SHA256 length

    def test_create_hash_empty_input(self):
        """Test hash creation with empty input."""
        sih = SymbolicIdentityHash()

        hash_data = sih.create_hash(None)

        assert hash_data is None

    def test_hash_consistency(self):
        """Test that same input produces same hash."""
        sih = SymbolicIdentityHash()
        emotional_vector = {
            "valence": 0.5,
            "arousal": 0.3,
            "dominance": 0.5,
            "trust": 0.7
        }

        hash1 = sih.create_hash(emotional_vector)
        hash2 = sih.create_hash(emotional_vector)

        assert hash1["hash"] == hash2["hash"]


class TestTraumaLock:
    """Test TraumaLock functionality."""

    def test_init(self):
        """Test TraumaLock initialization."""
        tl = TraumaLock()

        assert tl.locked_memories == {}
        assert tl.unlock_codes == {}
        assert tl.trauma_threshold == 0.7

    def test_check_and_lock_no_trauma(self):
        """Test memory with no trauma indicators."""
        tl = TraumaLock()
        safe_vector = {
            "valence": 0.5,
            "arousal": 0.3,
            "trust": 0.8
        }

        result_vector, was_locked = tl.check_and_lock(safe_vector)

        assert was_locked is False
        assert result_vector == safe_vector

    def test_check_and_lock_with_trauma(self):
        """Test memory with trauma indicators."""
        tl = TraumaLock()
        trauma_vector = {
            "valence": -0.8,  # Very negative
            "arousal": 0.9,   # Very high arousal
            "trust": 0.1      # Very low trust
        }

        result_vector, was_locked = tl.check_and_lock(trauma_vector)

        assert was_locked is True
        assert result_vector["locked"] is True
        assert "lock_id" in result_vector
        assert result_vector["valence"] >= 0  # Should be sanitized


class TestAdvancedIdentityManager:
    """Test AdvancedIdentityManager functionality."""

    def test_init(self):
        """Test AdvancedIdentityManager initialization."""
        aim = AdvancedIdentityManager()

        assert isinstance(aim.emotional_memory, EmotionalMemoryVector)
        assert isinstance(aim.symbolic_identity_hash, SymbolicIdentityHash)
        assert isinstance(aim.trauma_lock, TraumaLock)
        assert aim.users == {}
        assert aim.anonymous_usage_allowed is True
        assert aim.identity_events == []

    @pytest.mark.asyncio
    async def test_get_user_identity_new_user(self):
        """Test getting identity for new user."""
        aim = AdvancedIdentityManager()
        user_id = "new_user"

        identity = await aim.get_user_identity(user_id)

        assert identity is not None
        assert user_id in aim.users

    @pytest.mark.asyncio
    async def test_register_user_new(self):
        """Test registering a new user."""
        aim = AdvancedIdentityManager()
        user_id = "test_user"
        user_input = {"text": "Hello, I'm happy to be here"}

        await aim.register_user(user_id, user_input)

        # Should complete without error
        assert user_id in aim.users

    def test_privacy_preservation(self):
        """Test that emotional vectors don't store raw user input."""
        aim = AdvancedIdentityManager()
        user_input = {"text": "This is sensitive personal information"}

        vector = aim.emotional_memory.extract_vector(user_input)

        # Vector should not contain the original text
        assert "text" not in vector
        assert "This is sensitive personal information" not in str(vector)

    def test_emotional_analysis_accuracy(self):
        """Test emotional analysis produces reasonable results."""
        aim = AdvancedIdentityManager()

        # Test positive emotions
        positive_input = {"text": "I love this! It's amazing and wonderful!"}
        positive_vector = aim.emotional_memory.extract_vector(positive_input)
        assert positive_vector["valence"] > 0

        # Test negative emotions
        negative_input = {"text": "This is terrible and awful, I hate it"}
        negative_vector = aim.emotional_memory.extract_vector(negative_input)
        assert negative_vector["valence"] < 0

    @pytest.mark.asyncio
    async def test_complete_user_workflow(self):
        """Test complete user registration and authentication workflow."""
        aim = AdvancedIdentityManager()
        user_id = "workflow_test_user"
        registration_input = {"text": "Hello, I'm excited to register"}
        auth_input = {"text": "Hi, it's me again, still excited"}

        # 1. Register user
        await aim.register_user(user_id, registration_input)

        # 2. Verify user exists
        identity = await aim.get_user_identity(user_id)
        assert identity is not None

        # 3. Authenticate user
        auth_result = await aim.authenticate_user(auth_input, user_id)
        assert isinstance(auth_result, dict)

        # 4. Check that emotional memory was created
        user_vector = aim.emotional_memory.get_vector(user_id)
        assert user_vector is not None


class TestAdvancedIdentityManagerIntegration:
    """Integration tests for the complete identity management system."""

    def test_trauma_protection_integration(self):
        """Test that trauma protection is integrated into the system."""
        aim = AdvancedIdentityManager()

        # TraumaLock should be available
        assert aim.trauma_lock is not None
        assert hasattr(aim.trauma_lock, 'check_and_lock')

    def test_emotional_consistency(self):
        """Test that emotional patterns remain consistent across interactions."""
        aim = AdvancedIdentityManager()

        # Two similar positive inputs should produce similar vectors
        input1 = {"text": "I am happy and excited"}
        input2 = {"text": "I feel great and excited"}

        vector1 = aim.emotional_memory.extract_vector(input1)
        vector2 = aim.emotional_memory.extract_vector(input2)

        # Should have similar positive valence
        assert vector1["valence"] > 0
        assert vector2["valence"] > 0
        assert abs(vector1["valence"] - vector2["valence"]) < 0.5

    def test_system_resilience(self):
        """Test system handles edge cases gracefully."""
        aim = AdvancedIdentityManager()

        # Empty input
        empty_vector = aim.emotional_memory.extract_vector({})
        assert empty_vector is not None

        # No text input
        no_text_vector = aim.emotional_memory.extract_vector({"other": "data"})
        assert no_text_vector is not None

    @pytest.mark.asyncio
    async def test_guardian_integration_disabled_by_default(self):
        """Test that Guardian integration handles missing dependency gracefully."""
        with patch('core.identity.manager.GUARDIAN_AVAILABLE', False):
            aim = AdvancedIdentityManager()

            assert aim._guardian_integration_enabled is False
            assert aim._guardian_instance is None


# Test configuration for pytest
pytest_plugins = ["pytest_asyncio"]
