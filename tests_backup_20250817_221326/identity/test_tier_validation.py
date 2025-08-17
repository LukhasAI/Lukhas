"""
🔒 Tier Validation System Test Suite
===================================

Comprehensive unit tests for LUKHAS tier validation system (Tiers 0-5).
Tests the tier-based access control, permissions, and Trinity Framework compliance.

Trinity Framework: ⚛️ (Identity), 🧠 (Consciousness), 🛡️ (Guardian)
"""

import os

# Import system under test
import sys
import time
from unittest.mock import patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'identity'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'governance', 'identity', 'core', 'tier'))

try:
    from identity_core import AccessTier, IdentityCore
except ImportError:
    pytest.skip("IdentityCore not available", allow_module_level=True)


class TestTierValidationSystem:
    """Test suite for tier validation system (Tiers 0-5)"""

    @pytest.fixture
    def identity_core(self):
        """Create identity core instance for testing"""
        return IdentityCore()

    @pytest.fixture
    def tier_test_metadata(self):
        """Sample metadata for different tiers"""
        return {
            'T1': {
                'user_id': 'observer_user_12345678',
                'tier': 'T1',
                'consent': True,
                'trinity_score': 0.3,
                'drift_score': 0.1
            },
            'T2': {
                'user_id': 'participant_user_12345678',
                'tier': 'T2',
                'consent': True,
                'trinity_score': 0.5,
                'drift_score': 0.2
            },
            'T3': {
                'user_id': 'contributor_user_12345678',
                'tier': 'T3',
                'consent': True,
                'trinity_score': 0.7,
                'drift_score': 0.3
            },
            'T4': {
                'user_id': 'architect_user_12345678',
                'tier': 'T4',
                'consent': True,
                'trinity_score': 0.9,
                'drift_score': 0.1
            },
            'T5': {
                'user_id': 'guardian_user_12345678',
                'tier': 'T5',
                'consent': True,
                'trinity_score': 1.0,
                'drift_score': 0.0
            }
        }

    def test_access_tier_enum_values(self):
        """Test AccessTier enum has correct values"""
        assert AccessTier.T1.value == "T1"
        assert AccessTier.T2.value == "T2"
        assert AccessTier.T3.value == "T3"
        assert AccessTier.T4.value == "T4"
        assert AccessTier.T5.value == "T5"

        # Test all tiers are present
        tier_values = {tier.value for tier in AccessTier}
        expected_tiers = {"T1", "T2", "T3", "T4", "T5"}
        assert tier_values == expected_tiers

    def test_tier_glyph_mappings(self, identity_core):
        """Test tier-specific glyph mappings"""
        tier_glyphs = identity_core.TIER_GLYPHS

        # T1 - Observer (Identity only)
        assert AccessTier.T1 in tier_glyphs
        assert "⚛️" in tier_glyphs[AccessTier.T1]
        assert len(tier_glyphs[AccessTier.T1]) == 1

        # T2 - Participant (Identity + Creation)
        assert AccessTier.T2 in tier_glyphs
        assert "⚛️" in tier_glyphs[AccessTier.T2]
        assert "✨" in tier_glyphs[AccessTier.T2]
        assert len(tier_glyphs[AccessTier.T2]) == 2

        # T3 - Contributor (Identity + Consciousness + Dream)
        assert AccessTier.T3 in tier_glyphs
        assert "⚛️" in tier_glyphs[AccessTier.T3]
        assert "🧠" in tier_glyphs[AccessTier.T3]
        assert "💭" in tier_glyphs[AccessTier.T3]
        assert len(tier_glyphs[AccessTier.T3]) == 3

        # T4 - Architect (+ Quantum)
        assert AccessTier.T4 in tier_glyphs
        assert "⚛️" in tier_glyphs[AccessTier.T4]
        assert "🧠" in tier_glyphs[AccessTier.T4]
        assert "💭" in tier_glyphs[AccessTier.T4]
        assert "🔮" in tier_glyphs[AccessTier.T4]
        assert len(tier_glyphs[AccessTier.T4]) == 4

        # T5 - Guardian (+ Guardian)
        assert AccessTier.T5 in tier_glyphs
        assert "⚛️" in tier_glyphs[AccessTier.T5]
        assert "🧠" in tier_glyphs[AccessTier.T5]
        assert "💭" in tier_glyphs[AccessTier.T5]
        assert "🔮" in tier_glyphs[AccessTier.T5]
        assert "🛡️" in tier_glyphs[AccessTier.T5]
        assert len(tier_glyphs[AccessTier.T5]) == 5

    def test_tier_permissions_matrix(self, identity_core):
        """Test tier permissions matrix is correctly configured"""
        permissions = identity_core.TIER_PERMISSIONS

        # Test all tiers have permission entries
        for tier in AccessTier:
            assert tier in permissions
            tier_perms = permissions[tier]

            # All tiers should have these base permissions defined
            required_permissions = [
                'can_view_public',
                'can_create_content',
                'can_access_api',
                'can_use_consciousness',
                'can_use_emotion',
                'can_use_dream',
                'can_use_quantum',
                'can_access_guardian',
                'can_admin'
            ]

            for perm in required_permissions:
                assert perm in tier_perms

        # Test hierarchical permission structure
        # T1 - Basic viewing only
        t1_perms = permissions[AccessTier.T1]
        assert t1_perms['can_view_public'] is True
        assert t1_perms['can_create_content'] is False
        assert t1_perms['can_access_api'] is False
        assert t1_perms['can_use_consciousness'] is False
        assert t1_perms['can_admin'] is False

        # T2 - Can create content and use API
        t2_perms = permissions[AccessTier.T2]
        assert t2_perms['can_view_public'] is True
        assert t2_perms['can_create_content'] is True
        assert t2_perms['can_access_api'] is True
        assert t2_perms['can_use_consciousness'] is False
        assert t2_perms['can_admin'] is False

        # T3 - Can use consciousness features
        t3_perms = permissions[AccessTier.T3]
        assert t3_perms['can_use_consciousness'] is True
        assert t3_perms['can_use_emotion'] is True
        assert t3_perms['can_use_dream'] is True
        assert t3_perms['can_use_quantum'] is False
        assert t3_perms['can_admin'] is False

        # T4 - Can use quantum features
        t4_perms = permissions[AccessTier.T4]
        assert t4_perms['can_use_quantum'] is True
        assert t4_perms['can_access_guardian'] is False
        assert t4_perms['can_admin'] is False

        # T5 - Full admin access
        t5_perms = permissions[AccessTier.T5]
        assert t5_perms['can_access_guardian'] is True
        assert t5_perms['can_admin'] is True

        # Verify inherited permissions (higher tiers inherit lower tier permissions)
        for higher_tier in [AccessTier.T2, AccessTier.T3, AccessTier.T4, AccessTier.T5]:
            higher_perms = permissions[higher_tier]
            assert higher_perms['can_view_public'] is True  # All tiers can view public

        for higher_tier in [AccessTier.T3, AccessTier.T4, AccessTier.T5]:
            higher_perms = permissions[higher_tier]
            assert higher_perms['can_create_content'] is True  # T2+ can create
            assert higher_perms['can_access_api'] is True  # T2+ can use API

    def test_resolve_access_tier_basic(self, identity_core, tier_test_metadata):
        """Test basic tier resolution from metadata"""
        for tier_str, metadata in tier_test_metadata.items():
            tier, permissions = identity_core.resolve_access_tier(metadata)

            # Verify correct tier resolution
            assert tier.value == tier_str
            assert isinstance(permissions, dict)

            # Verify permissions are returned
            assert 'can_view_public' in permissions
            assert len(permissions) >= 9  # Should have all permission keys

    def test_resolve_access_tier_invalid_tier(self, identity_core):
        """Test tier resolution with invalid tier string"""
        metadata = {
            'user_id': 'test_user_12345678',
            'tier': 'INVALID_TIER',
            'consent': True
        }

        tier, permissions = identity_core.resolve_access_tier(metadata)

        # Should default to T1
        assert tier == AccessTier.T1
        assert permissions == identity_core.TIER_PERMISSIONS[AccessTier.T1]

    def test_resolve_access_tier_missing_tier(self, identity_core):
        """Test tier resolution with missing tier field"""
        metadata = {
            'user_id': 'test_user_12345678',
            'consent': True
        }

        tier, permissions = identity_core.resolve_access_tier(metadata)

        # Should default to T1
        assert tier == AccessTier.T1
        assert permissions == identity_core.TIER_PERMISSIONS[AccessTier.T1]

    def test_resolve_access_tier_consent_restrictions(self, identity_core):
        """Test tier resolution with consent restrictions"""
        metadata = {
            'user_id': 'no_consent_user_12345678',
            'tier': 'T3',
            'consent': False  # No consent given
        }

        tier, permissions = identity_core.resolve_access_tier(metadata)

        # Should get T3 tier but restricted permissions
        assert tier == AccessTier.T3

        # These permissions should be restricted due to lack of consent
        assert permissions['can_create_content'] is False
        assert permissions['can_use_consciousness'] is False
        assert permissions['can_use_emotion'] is False
        assert permissions['can_use_dream'] is False

        # Basic viewing should still be allowed
        assert permissions['can_view_public'] is True

    def test_resolve_access_tier_drift_score_monitoring(self, identity_core):
        """Test tier resolution with drift score monitoring"""
        # High drift score should be logged but not restrict permissions yet
        metadata = {
            'user_id': 'high_drift_user_12345678',
            'tier': 'T4',
            'consent': True,
            'drift_score': 0.8  # High drift score
        }

        with patch('logging.Logger.warning') as mock_warning:
            tier, permissions = identity_core.resolve_access_tier(metadata)

            # Should resolve normally but log warning
            assert tier == AccessTier.T4
            mock_warning.assert_called_once()
            assert 'High drift score detected' in str(mock_warning.call_args)

    def test_resolve_access_tier_trinity_score_elevation(self, identity_core):
        """Test tier elevation based on Trinity score"""
        # High Trinity score should be noted but not auto-elevate (needs Guardian approval)
        metadata = {
            'user_id': 'high_trinity_user_12345678',
            'tier': 'T2',
            'consent': True,
            'trinity_score': 0.95  # Very high Trinity score
        }

        with patch('logging.Logger.info') as mock_info:
            tier, permissions = identity_core.resolve_access_tier(metadata)

            # Should not auto-elevate without Guardian approval
            assert tier == AccessTier.T2

            # Should log the potential elevation
            mock_info.assert_called()
            assert 'Elevating tier based on trinity score' in str(mock_info.call_args)

    def test_resolve_access_tier_cultural_profile(self, identity_core):
        """Test tier resolution with cultural profile considerations"""
        metadata = {
            'user_id': 'cultural_user_12345678',
            'tier': 'T3',
            'consent': True,
            'cultural_profile': 'eu_privacy'  # Non-universal profile
        }

        tier, permissions = identity_core.resolve_access_tier(metadata)

        # Should resolve normally (cultural modifiers not implemented yet)
        assert tier == AccessTier.T3
        # TODO: Implement cultural permission modifiers

    def test_tier_validation_performance(self, identity_core, tier_test_metadata):
        """Test tier validation performance requirements"""
        num_iterations = 100
        total_time = 0

        for i in range(num_iterations):
            # Use different tiers for testing
            tier_key = f'T{(i % 5) + 1}'
            metadata = tier_test_metadata[tier_key].copy()
            metadata['user_id'] = f'perf_test_user_{i:08d}'

            start_time = time.time()
            tier, permissions = identity_core.resolve_access_tier(metadata)
            end_time = time.time()

            total_time += (end_time - start_time)

            # Verify results are valid
            assert isinstance(tier, AccessTier)
            assert isinstance(permissions, dict)

        # Average time per operation should be well under 1ms
        avg_time_ms = (total_time / num_iterations) * 1000
        assert avg_time_ms < 10, f"Average tier resolution time {avg_time_ms:.3f}ms too high"

        # P95 should be even better
        assert avg_time_ms < 5, "Tier resolution should be under 5ms on average"

    def test_tier_based_token_creation(self, identity_core):
        """Test token creation with different tiers"""
        user_id = "tier_token_test_user_12345678"

        for tier in AccessTier:
            metadata = {
                'consent': True,
                'trinity_score': 0.8,
                'cultural_profile': 'universal'
            }

            token = identity_core.create_token(user_id, tier, metadata)

            # Verify token format includes tier
            assert token.startswith(f"LUKHAS-{tier.value}-")

            # Verify token can be validated
            is_valid, token_metadata = identity_core.validate_symbolic_token(token)
            assert is_valid is True
            assert token_metadata['tier'] == tier.value
            assert token_metadata['user_id'] == user_id

    def test_tier_glyph_generation(self, identity_core):
        """Test glyph generation respects tier requirements"""
        user_seed = "test_user_glyph_generation"

        for tier in AccessTier:
            # Generate glyphs
            glyphs = identity_core.generate_identity_glyph(user_seed + tier.value)

            assert isinstance(glyphs, list)
            assert len(glyphs) >= 3  # Minimum glyph count
            assert len(glyphs) <= 6  # Maximum reasonable glyph count

            # Should always include at least one Trinity glyph
            trinity_glyphs = ["⚛️", "🧠", "🛡️"]
            has_trinity_glyph = any(glyph in trinity_glyphs for glyph in glyphs)
            assert has_trinity_glyph, f"Glyphs {glyphs} should contain at least one Trinity glyph"

    def test_tier_symbolic_integrity_validation(self, identity_core):
        """Test symbolic integrity validation for different tiers"""
        for tier in AccessTier:
            # Create valid metadata for each tier
            metadata = {
                'user_id': f'integrity_test_{tier.value}_12345678',
                'tier': tier.value,
                'glyphs': identity_core.TIER_GLYPHS[tier].copy()
            }

            # Should pass validation
            is_valid = identity_core._validate_symbolic_integrity(metadata)
            assert is_valid is True

            # Test with missing required fields
            incomplete_metadata = metadata.copy()
            del incomplete_metadata['tier']

            is_valid = identity_core._validate_symbolic_integrity(incomplete_metadata)
            assert is_valid is False

    def test_tier_permission_hierarchy(self, identity_core):
        """Test that tier permissions follow hierarchical inheritance"""
        permissions_by_tier = {}

        # Get permissions for each tier
        for tier in AccessTier:
            metadata = {
                'user_id': f'hierarchy_test_{tier.value}_12345678',
                'tier': tier.value,
                'consent': True
            }
            _, permissions = identity_core.resolve_access_tier(metadata)
            permissions_by_tier[tier] = permissions

        # Test hierarchical inheritance patterns
        # All tiers should allow public viewing
        for tier in AccessTier:
            assert permissions_by_tier[tier]['can_view_public'] is True

        # T2+ should inherit T1 permissions plus additional
        for tier in [AccessTier.T2, AccessTier.T3, AccessTier.T4, AccessTier.T5]:
            tier_perms = permissions_by_tier[tier]
            t1_perms = permissions_by_tier[AccessTier.T1]

            # Should have all T1 permissions that are True
            for perm, value in t1_perms.items():
                if value is True:
                    assert tier_perms[perm] is True, f"Tier {tier.value} should inherit {perm} from T1"

        # T3+ should inherit T2 permissions plus additional
        for tier in [AccessTier.T3, AccessTier.T4, AccessTier.T5]:
            tier_perms = permissions_by_tier[tier]
            t2_perms = permissions_by_tier[AccessTier.T2]

            for perm, value in t2_perms.items():
                if value is True:
                    assert tier_perms[perm] is True, f"Tier {tier.value} should inherit {perm} from T2"

        # T4+ should inherit T3 permissions plus additional
        for tier in [AccessTier.T4, AccessTier.T5]:
            tier_perms = permissions_by_tier[tier]
            t3_perms = permissions_by_tier[AccessTier.T3]

            for perm, value in t3_perms.items():
                if value is True:
                    assert tier_perms[perm] is True, f"Tier {tier.value} should inherit {perm} from T3"

        # T5 should inherit T4 permissions plus additional
        t5_perms = permissions_by_tier[AccessTier.T5]
        t4_perms = permissions_by_tier[AccessTier.T4]

        for perm, value in t4_perms.items():
            if value is True:
                assert t5_perms[perm] is True, f"T5 should inherit {perm} from T4"

    def test_error_handling_in_tier_resolution(self, identity_core):
        """Test error handling in tier resolution"""
        # Test with None metadata
        tier, permissions = identity_core.resolve_access_tier(None)
        assert tier == AccessTier.T1  # Should default to T1

        # Test with empty metadata
        tier, permissions = identity_core.resolve_access_tier({})
        assert tier == AccessTier.T1

        # Test with malformed metadata
        malformed_metadata = {
            'user_id': None,
            'tier': 123,  # Invalid type
            'consent': 'maybe'  # Invalid type
        }

        tier, permissions = identity_core.resolve_access_tier(malformed_metadata)
        assert tier == AccessTier.T1  # Should fallback safely

    def test_trinity_framework_compliance(self, identity_core, tier_test_metadata):
        """Test Trinity Framework compliance across all tiers (⚛️🧠🛡️)"""
        for tier_str, metadata in tier_test_metadata.items():
            tier, permissions = identity_core.resolve_access_tier(metadata)

            # ⚛️ Identity - All tiers should maintain identity integrity
            assert isinstance(tier, AccessTier)
            assert tier.value == tier_str

            # 🧠 Consciousness - Metadata should be processed intelligently
            assert isinstance(permissions, dict)
            assert len(permissions) >= 9  # Full permission set

            # 🛡️ Guardian - Security validations should be applied
            if 'consent' in metadata and not metadata['consent']:
                # Guardian should restrict permissions without consent
                assert permissions['can_create_content'] is False
                assert permissions['can_use_consciousness'] is False

            # High drift scores should be logged (Guardian awareness)
            if metadata.get('drift_score', 0) > 0.5:
                with patch('logging.Logger.warning') as mock_warning:
                    identity_core.resolve_access_tier(metadata)
                    mock_warning.assert_called()

    def test_tier_based_feature_flags(self, identity_core):
        """Test tier-based feature flag behavior"""
        # This would integrate with a feature flag system
        # For now, test the permission-based feature access

        feature_requirements = {
            'basic_api': 'can_access_api',
            'content_creation': 'can_create_content',
            'consciousness_features': 'can_use_consciousness',
            'emotion_processing': 'can_use_emotion',
            'dream_analysis': 'can_use_dream',
            'quantum_processing': 'can_use_quantum',
            'guardian_access': 'can_access_guardian',
            'admin_panel': 'can_admin'
        }

        for tier in AccessTier:
            metadata = {
                'user_id': f'feature_test_{tier.value}_12345678',
                'tier': tier.value,
                'consent': True
            }

            _, permissions = identity_core.resolve_access_tier(metadata)

            for feature, required_perm in feature_requirements.items():
                feature_available = permissions.get(required_perm, False)

                # Log feature availability for this tier
                if feature_available:
                    print(f"Tier {tier.value}: {feature} AVAILABLE")
                else:
                    print(f"Tier {tier.value}: {feature} NOT AVAILABLE")

                # Basic features should follow expected tier patterns
                if feature == 'basic_api':
                    expected = tier.value in ['T2', 'T3', 'T4', 'T5']
                    assert feature_available == expected
                elif feature == 'quantum_processing':
                    expected = tier.value in ['T4', 'T5']
                    assert feature_available == expected
                elif feature == 'admin_panel':
                    expected = tier.value == 'T5'
                    assert feature_available == expected
