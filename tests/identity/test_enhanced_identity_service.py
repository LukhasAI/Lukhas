#!/usr/bin/env python3
"""
Enhanced Identity Service Integration Tests

Tests the enhanced identity service with multiple backends, fallback logic,
external service integration, and realistic user profile generation.

# ΛTAG: identity_tests, service_integration, external_backends
"""

import asyncio
import os
from unittest.mock import AsyncMock, Mock, patch

import pytest

try:
    from core.identity.vault.lukhas_id import (
        IdentityManager,
        IdentityProfile,
        IdentityVerificationError,
        TierLevel,
    )

    IDENTITY_AVAILABLE = True
except ImportError:
    # Fallback for testing without full identity system
    IDENTITY_AVAILABLE = False
    IdentityManager = None
    IdentityProfile = None
    TierLevel = None
    IdentityVerificationError = Exception


@pytest.mark.skipif(not IDENTITY_AVAILABLE, reason="Identity system not available")
class TestEnhancedIdentityService:
    """Test enhanced identity service functionality."""

    @pytest.fixture
    def identity_manager(self):
        """Create identity manager instance."""
        return IdentityManager()

    @pytest.mark.asyncio
    async def test_primary_service_integration(self, identity_manager):
        """Test primary identity service integration."""

        # Mock environment variable for primary service
        with patch.dict(os.environ, {"LUKHAS_IDENTITY_SERVICE_URL": "https://identity.lukhas.ai"}):

            # Test identity lookup
            profile = await identity_manager._load_identity("test_user_123")

            # Verify profile structure
            assert profile.user_id == "test_user_123"
            assert profile.tier_level >= TierLevel.PUBLIC.value
            assert "source" in profile.attributes
            assert profile.attributes["source"] == "primary_service"
            assert "email" in profile.attributes
            assert profile.attributes["email"] == "test_user_123@lukhas.ai"

    @pytest.mark.asyncio
    async def test_backup_service_fallback(self, identity_manager):
        """Test fallback to backup identity service."""

        # Mock primary service failure and backup service success
        with patch.object(
            identity_manager, "_fetch_from_primary_identity_service", side_effect=Exception("Primary service down")
        ):

            profile = await identity_manager._load_identity("backup_user")

            # Verify fallback profile
            assert profile.user_id == "backup_user"
            assert profile.tier_level == TierLevel.AUTHENTICATED.value
            assert profile.attributes["source"] == "backup_service"
            assert "core:read" in profile.scopes

    @pytest.mark.asyncio
    async def test_inferred_identity_final_fallback(self, identity_manager):
        """Test final fallback to inferred identity."""

        # Mock all services failing
        with (
            patch.object(
                identity_manager, "_fetch_from_primary_identity_service", side_effect=Exception("Primary failed")
            ),
            patch.object(
                identity_manager, "_fetch_from_backup_identity_service", side_effect=Exception("Backup failed")
            ),
        ):

            profile = await identity_manager._load_identity("fallback_user")

            # Verify inferred profile
            assert profile.user_id == "fallback_user"
            assert profile.tier_level == TierLevel.AUTHENTICATED.value
            assert profile.attributes["source"] == "inferred"
            assert "core:read" in profile.scopes

    @pytest.mark.asyncio
    async def test_anonymous_user_handling(self, identity_manager):
        """Test handling of anonymous users."""

        profile = await identity_manager._load_identity("anonymous")

        # Verify anonymous profile
        assert profile.user_id == "anonymous"
        assert profile.tier_level == TierLevel.PUBLIC.value
        assert len(profile.scopes) == 0  # No scopes for public users

    @pytest.mark.asyncio
    async def test_tier_based_scope_assignment(self, identity_manager):
        """Test that scopes are correctly assigned based on tier level."""

        # Mock different tier levels
        test_cases = [
            ("public_user", TierLevel.PUBLIC.value, set()),
            ("auth_user", TierLevel.AUTHENTICATED.value, {"core:read"}),
            ("elevated_user", TierLevel.ELEVATED.value, {"core:read", "core:write", "memory:read"}),
            (
                "privileged_user",
                TierLevel.PRIVILEGED.value,
                {"core:read", "core:write", "memory:read", "memory:write", "admin:read"},
            ),
        ]

        with patch.dict(os.environ, {"LUKHAS_IDENTITY_SERVICE_URL": "https://identity.lukhas.ai"}):

            for user_id, expected_tier, expected_scopes in test_cases:
                # Mock deterministic tier assignment
                with patch("hashlib.sha256") as mock_hash:
                    # Create predictable hash for tier assignment
                    tier_index = expected_tier if expected_tier <= 3 else 3
                    mock_hash.return_value.hexdigest.return_value = f"{tier_index:08x}" + "0" * 56

                    profile = await identity_manager._load_identity(user_id)

                    assert profile.tier_level == expected_tier, f"Incorrect tier for {user_id}"
                    assert profile.scopes >= expected_scopes, f"Missing scopes for {user_id}"

    @pytest.mark.asyncio
    async def test_profile_caching(self, identity_manager):
        """Test that identity profiles are properly cached."""

        user_id = "cached_user"

        # First call should fetch from service
        with patch.object(identity_manager, "_fetch_from_identity_service") as mock_fetch:
            mock_profile = IdentityProfile(
                user_id=user_id, tier_level=TierLevel.AUTHENTICATED.value, attributes={"source": "test"}
            )
            mock_fetch.return_value = mock_profile

            profile1 = await identity_manager._load_identity(user_id)
            assert mock_fetch.call_count == 1

            # Second call should use cache
            profile2 = await identity_manager._load_identity(user_id)
            assert mock_fetch.call_count == 1  # No additional call

            # Verify same profile returned
            assert profile1.user_id == profile2.user_id
            assert id(profile1) == id(profile2)  # Same object instance

    @pytest.mark.asyncio
    async def test_concurrent_identity_loading(self, identity_manager):
        """Test concurrent identity loading safety."""

        user_id = "concurrent_user"

        # Mock slow identity service
        async def slow_fetch(*args):
            await asyncio.sleep(0.1)
            return IdentityProfile(
                user_id=user_id, tier_level=TierLevel.AUTHENTICATED.value, attributes={"source": "concurrent_test"}
            )

        with patch.object(identity_manager, "_fetch_from_identity_service", side_effect=slow_fetch) as mock_fetch:

            # Start multiple concurrent loads
            tasks = [identity_manager._load_identity(user_id) for _ in range(5)]

            profiles = await asyncio.gather(*tasks)

            # Verify all profiles are consistent
            for profile in profiles:
                assert profile.user_id == user_id
                assert profile.attributes["source"] == "concurrent_test"

            # Verify service was called only once due to caching
            assert mock_fetch.call_count == 1

    @pytest.mark.asyncio
    async def test_service_timeout_handling(self, identity_manager):
        """Test timeout handling for slow identity services."""

        user_id = "timeout_user"

        # Mock very slow primary service
        async def timeout_fetch(*args):
            await asyncio.sleep(10)  # Longer than reasonable timeout
            return None

        with patch.object(identity_manager, "_fetch_from_primary_identity_service", side_effect=timeout_fetch):

            # Should fallback to backup service
            start_time = asyncio.get_event_loop().time()
            profile = await identity_manager._load_identity(user_id)
            end_time = asyncio.get_event_loop().time()

            # Verify reasonable response time (backup service should be fast)
            assert (end_time - start_time) < 1.0, "Should fallback quickly"
            assert profile.user_id == user_id
            assert profile.attributes["source"] == "backup_service"

    @pytest.mark.asyncio
    async def test_malformed_user_id_handling(self, identity_manager):
        """Test handling of malformed or invalid user IDs."""

        malformed_ids = [
            "",  # Empty string
            " ",  # Whitespace only
            "user@with@multiple@symbols",  # Multiple @ symbols
            "user\nwith\nnewlines",  # Newlines in ID
            "user_with_very_long_id_" + "x" * 1000,  # Extremely long ID
        ]

        for user_id in malformed_ids:
            try:
                profile = await identity_manager._load_identity(user_id)

                # If successful, verify safe handling
                assert profile is not None
                assert profile.user_id == user_id or profile.user_id == "anonymous"
                assert profile.tier_level >= TierLevel.PUBLIC.value

            except Exception as e:
                # If failed, ensure it's a controlled failure
                assert isinstance(e, (ValueError, IdentityVerificationError))

    @pytest.mark.asyncio
    async def test_service_error_logging(self, identity_manager):
        """Test that service errors are properly logged."""

        user_id = "error_logging_user"

        # Mock service with specific error
        with (
            patch.object(
                identity_manager,
                "_fetch_from_primary_identity_service",
                side_effect=ConnectionError("Service unavailable"),
            ),
            patch("structlog.get_logger") as mock_logger,
        ):

            logger_instance = Mock()
            mock_logger.return_value = logger_instance

            # Attempt identity load
            profile = await identity_manager._load_identity(user_id)

            # Verify error was logged
            logger_instance.warning.assert_called()
            warning_calls = logger_instance.warning.call_args_list

            # Check that error details were logged
            assert any("identity_backend_failed" in str(call) for call in warning_calls)

    def test_deterministic_profile_generation(self, identity_manager):
        """Test that profile generation is deterministic for the same user ID."""

        user_id = "deterministic_user"

        # Generate profile multiple times
        profiles = []
        for _ in range(3):
            with patch.dict(os.environ, {"LUKHAS_IDENTITY_SERVICE_URL": "https://identity.lukhas.ai"}):
                # Use asyncio.run to handle async method in sync test
                profile = asyncio.run(identity_manager._fetch_from_primary_identity_service(user_id))
                profiles.append(profile)

        # Verify all profiles are identical
        for i in range(1, len(profiles)):
            assert profiles[i].user_id == profiles[0].user_id
            assert profiles[i].tier_level == profiles[0].tier_level
            assert profiles[i].attributes["email"] == profiles[0].attributes["email"]
            assert profiles[i].scopes == profiles[0].scopes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
