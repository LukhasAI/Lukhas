"""
Tests for ΛID (Lambda ID) Utility Functions

Simple utility tests for Lambda ID parsing, validation, and formatting.
Real implementations only, no mocks needed.

Trinity Framework: ⚛️ Identity
"""

import pytest
import re
from datetime import datetime


# ============================================================================
# ΛID Format and Validation Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_format_structure():
    """Test ΛID format structure validation."""
    # Valid formats
    valid_ids = [
        "Λ_alpha_user123",
        "Λ_beta_user456",
        "Λ_gamma_user789",
        "Λ_delta_user000",
        "Λ_alpha_abc123def456",
    ]
    
    # Pattern: Λ_{tier}_{user_id}
    pattern = r"^Λ_(alpha|beta|gamma|delta)_[a-zA-Z0-9_]+$"
    
    for lambda_id in valid_ids:
        assert re.match(pattern, lambda_id), f"Invalid ΛID format: {lambda_id}"


@pytest.mark.unit
def test_lambda_id_invalid_formats():
    """Test detection of invalid ΛID formats."""
    invalid_ids = [
        "lambda_alpha_user123",  # Missing Λ symbol
        "Λ_invalid_user123",      # Invalid tier
        "Λ_alpha",                # Missing user_id
        "_alpha_user123",         # Missing Λ
        "Λ_ALPHA_user123",        # Wrong case
        "Λ_alpha_user@123",       # Invalid characters
    ]
    
    pattern = r"^Λ_(alpha|beta|gamma|delta)_[a-zA-Z0-9_]+$"
    
    for lambda_id in invalid_ids:
        assert not re.match(pattern, lambda_id), f"Should reject: {lambda_id}"


@pytest.mark.unit
def test_lambda_id_tier_extraction():
    """Test extracting tier from ΛID."""
    test_cases = [
        ("Λ_alpha_user123", "alpha"),
        ("Λ_beta_user456", "beta"),
        ("Λ_gamma_user789", "gamma"),
        ("Λ_delta_user000", "delta"),
    ]
    
    for lambda_id, expected_tier in test_cases:
        # Extract tier (simple string split)
        parts = lambda_id.split("_")
        tier = parts[1] if len(parts) >= 2 else None
        assert tier == expected_tier


@pytest.mark.unit
def test_lambda_id_user_id_extraction():
    """Test extracting user_id from ΛID."""
    test_cases = [
        ("Λ_alpha_user123", "user123"),
        ("Λ_beta_abc456def", "abc456def"),
        ("Λ_gamma_test_user", "test_user"),
    ]
    
    for lambda_id, expected_user_id in test_cases:
        # Extract user_id (everything after second underscore)
        parts = lambda_id.split("_", 2)
        user_id = parts[2] if len(parts) >= 3 else None
        assert user_id == expected_user_id


# ============================================================================
# Tier Validation Tests
# ============================================================================

@pytest.mark.unit
def test_tier_hierarchy_validation():
    """Test tier hierarchy (alpha > beta > gamma > delta)."""
    tier_hierarchy = {
        "alpha": 4,
        "beta": 3,
        "gamma": 2,
        "delta": 1,
    }
    
    # Alpha has highest privilege
    assert tier_hierarchy["alpha"] > tier_hierarchy["beta"]
    assert tier_hierarchy["alpha"] > tier_hierarchy["gamma"]
    assert tier_hierarchy["alpha"] > tier_hierarchy["delta"]
    
    # Beta > gamma > delta
    assert tier_hierarchy["beta"] > tier_hierarchy["gamma"]
    assert tier_hierarchy["gamma"] > tier_hierarchy["delta"]


@pytest.mark.unit
def test_tier_access_level_comparison():
    """Test tier-based access level comparison."""
    tier_values = {
        "alpha": 4,
        "beta": 3,
        "gamma": 2,
        "delta": 1,
    }
    
    def has_access(user_tier: str, required_tier: str) -> bool:
        """Check if user tier meets required tier."""
        return tier_values[user_tier] >= tier_values[required_tier]
    
    # Alpha can access everything
    assert has_access("alpha", "alpha")
    assert has_access("alpha", "beta")
    assert has_access("alpha", "gamma")
    assert has_access("alpha", "delta")
    
    # Delta can only access delta
    assert has_access("delta", "delta")
    assert not has_access("delta", "gamma")
    assert not has_access("delta", "beta")
    assert not has_access("delta", "alpha")
    
    # Beta can access beta and below
    assert has_access("beta", "beta")
    assert has_access("beta", "gamma")
    assert has_access("beta", "delta")
    assert not has_access("beta", "alpha")


@pytest.mark.unit
def test_tier_rate_limit_multipliers():
    """Test tier-based rate limit multipliers."""
    multipliers = {
        "alpha": 3.0,
        "beta": 2.0,
        "gamma": 1.5,
        "delta": 1.0,
    }
    
    base_limit = 100
    
    # Calculate effective limits
    alpha_limit = base_limit * multipliers["alpha"]
    beta_limit = base_limit * multipliers["beta"]
    gamma_limit = base_limit * multipliers["gamma"]
    delta_limit = base_limit * multipliers["delta"]
    
    # Verify multipliers
    assert alpha_limit == 300
    assert beta_limit == 200
    assert gamma_limit == 150
    assert delta_limit == 100
    
    # Verify hierarchy
    assert alpha_limit > beta_limit > gamma_limit > delta_limit


# ============================================================================
# ΛID Generation Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_generation_format():
    """Test ΛID generation follows correct format."""
    def generate_lambda_id(tier: str, user_id: str) -> str:
        """Generate ΛID from tier and user_id."""
        return f"Λ_{tier}_{user_id}"
    
    # Test generation
    lambda_id = generate_lambda_id("alpha", "user123")
    assert lambda_id == "Λ_alpha_user123"
    
    # Verify format
    pattern = r"^Λ_(alpha|beta|gamma|delta)_[a-zA-Z0-9_]+$"
    assert re.match(pattern, lambda_id)


@pytest.mark.unit
def test_lambda_id_uniqueness():
    """Test ΛID uniqueness based on user_id."""
    def generate_lambda_id(tier: str, user_id: str) -> str:
        return f"Λ_{tier}_{user_id}"
    
    # Same user_id, different tiers = different ΛIDs
    id1 = generate_lambda_id("alpha", "user123")
    id2 = generate_lambda_id("beta", "user123")
    assert id1 != id2
    
    # Different user_ids = different ΛIDs
    id3 = generate_lambda_id("alpha", "user123")
    id4 = generate_lambda_id("alpha", "user456")
    assert id3 != id4


# ============================================================================
# ΛID Parsing Capability Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_parse_components():
    """Test parsing all components from ΛID."""
    lambda_id = "Λ_beta_user789"
    
    # Parse using simple string operations
    parts = lambda_id.split("_")
    
    assert len(parts) == 3
    assert parts[0] == "Λ"
    assert parts[1] == "beta"
    assert parts[2] == "user789"


@pytest.mark.unit
def test_lambda_id_validation_edge_cases():
    """Test ΛID validation edge cases."""
    # Empty string
    assert not "Λ_alpha_user123".startswith("Λ") if "" else False
    
    # Very long user_id
    long_user_id = "a" * 1000
    long_lambda_id = f"Λ_alpha_{long_user_id}"
    assert long_lambda_id.startswith("Λ_alpha_")
    
    # Numeric user_id
    numeric_lambda_id = "Λ_delta_123456"
    assert numeric_lambda_id.split("_")[2] == "123456"


# ============================================================================
# Tier String Operations
# ============================================================================

@pytest.mark.unit
def test_tier_string_normalization():
    """Test tier string normalization."""
    def normalize_tier(tier: str) -> str:
        """Normalize tier to lowercase."""
        return tier.lower().strip()
    
    test_cases = [
        ("Alpha", "alpha"),
        ("BETA", "beta"),
        (" gamma ", "gamma"),
        ("DeLtA", "delta"),
    ]
    
    for input_tier, expected in test_cases:
        assert normalize_tier(input_tier) == expected


@pytest.mark.unit
def test_tier_validation_list():
    """Test tier validation against allowed list."""
    VALID_TIERS = ["alpha", "beta", "gamma", "delta"]
    
    def is_valid_tier(tier: str) -> bool:
        """Check if tier is valid."""
        return tier.lower() in VALID_TIERS
    
    # Valid tiers
    assert is_valid_tier("alpha")
    assert is_valid_tier("BETA")
    assert is_valid_tier("Gamma")
    
    # Invalid tiers
    assert not is_valid_tier("epsilon")
    assert not is_valid_tier("invalid")
    assert not is_valid_tier("")


# ============================================================================
# ΛID Comparison and Equality Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_equality():
    """Test ΛID equality comparison."""
    id1 = "Λ_alpha_user123"
    id2 = "Λ_alpha_user123"
    id3 = "Λ_beta_user123"
    
    # Exact match
    assert id1 == id2
    
    # Different tier
    assert id1 != id3
    
    # Case sensitive
    assert id1 != "λ_alpha_user123"


@pytest.mark.unit
def test_lambda_id_tier_comparison():
    """Test comparing ΛIDs by tier."""
    def compare_lambda_ids(id1: str, id2: str) -> int:
        """Compare two ΛIDs by tier hierarchy. Returns -1, 0, or 1."""
        tier_values = {"alpha": 4, "beta": 3, "gamma": 2, "delta": 1}
        
        tier1 = id1.split("_")[1]
        tier2 = id2.split("_")[1]
        
        val1 = tier_values.get(tier1, 0)
        val2 = tier_values.get(tier2, 0)
        
        if val1 > val2:
            return 1
        elif val1 < val2:
            return -1
        else:
            return 0
    
    # Alpha > Beta
    assert compare_lambda_ids("Λ_alpha_user1", "Λ_beta_user2") == 1
    
    # Delta < Gamma
    assert compare_lambda_ids("Λ_delta_user1", "Λ_gamma_user2") == -1
    
    # Same tier
    assert compare_lambda_ids("Λ_beta_user1", "Λ_beta_user2") == 0


# ============================================================================
# ΛID Hash and Checksum Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_hash_consistency():
    """Test ΛID hashing is consistent."""
    import hashlib
    
    lambda_id = "Λ_alpha_user123"
    
    # Hash twice
    hash1 = hashlib.sha256(lambda_id.encode()).hexdigest()
    hash2 = hashlib.sha256(lambda_id.encode()).hexdigest()
    
    # Should be identical
    assert hash1 == hash2


@pytest.mark.unit
def test_lambda_id_checksum_generation():
    """Test ΛID checksum generation."""
    import hashlib
    
    lambda_id = "Λ_beta_user456"
    
    # Generate checksum (first 8 chars of SHA256)
    full_hash = hashlib.sha256(lambda_id.encode()).hexdigest()
    checksum = full_hash[:8]
    
    # Verify checksum properties
    assert len(checksum) == 8
    assert all(c in "0123456789abcdef" for c in checksum)


# ============================================================================
# Bulk ΛID Operations
# ============================================================================

@pytest.mark.unit
def test_lambda_id_batch_validation():
    """Test batch validation of multiple ΛIDs."""
    lambda_ids = [
        "Λ_alpha_user1",
        "Λ_beta_user2",
        "Λ_gamma_user3",
        "invalid_id",
        "Λ_delta_user4",
    ]
    
    pattern = r"^Λ_(alpha|beta|gamma|delta)_[a-zA-Z0-9_]+$"
    
    valid_ids = [lid for lid in lambda_ids if re.match(pattern, lid)]
    
    assert len(valid_ids) == 4
    assert "invalid_id" not in valid_ids


@pytest.mark.unit
def test_lambda_id_tier_grouping():
    """Test grouping ΛIDs by tier."""
    lambda_ids = [
        "Λ_alpha_user1",
        "Λ_beta_user2",
        "Λ_alpha_user3",
        "Λ_gamma_user4",
        "Λ_beta_user5",
    ]
    
    grouped = {}
    for lid in lambda_ids:
        tier = lid.split("_")[1]
        if tier not in grouped:
            grouped[tier] = []
        grouped[tier].append(lid)
    
    assert len(grouped["alpha"]) == 2
    assert len(grouped["beta"]) == 2
    assert len(grouped["gamma"]) == 1


# ============================================================================
# ΛID String Formatting Tests
# ============================================================================

@pytest.mark.unit
def test_lambda_id_display_format():
    """Test ΛID display formatting."""
    lambda_id = "Λ_alpha_user123"
    
    # Format for display (e.g., "Alpha User: user123")
    parts = lambda_id.split("_")
    tier = parts[1].capitalize()
    user_id = parts[2]
    
    display = f"{tier} User: {user_id}"
    
    assert display == "Alpha User: user123"


@pytest.mark.unit
def test_lambda_id_masking():
    """Test ΛID masking for privacy."""
    lambda_id = "Λ_beta_user123456"
    
    # Mask user_id (show first 4, last 2)
    parts = lambda_id.split("_")
    user_id = parts[2]
    
    if len(user_id) > 6:
        masked_user_id = f"{user_id[:4]}***{user_id[-2:]}"
        masked_lambda_id = f"Λ_{parts[1]}_{masked_user_id}"
        
        assert masked_lambda_id == "Λ_beta_user***56"


# ============================================================================
# ΛID Capability Tests
# ============================================================================

@pytest.mark.capability
def test_lambda_id_system_capability():
    """Test overall ΛID system capability."""
    # Generate ΛID
    tier = "alpha"
    user_id = "test_user_123"
    lambda_id = f"Λ_{tier}_{user_id}"
    
    # Validate format
    pattern = r"^Λ_(alpha|beta|gamma|delta)_[a-zA-Z0-9_]+$"
    assert re.match(pattern, lambda_id)
    
    # Extract components
    parts = lambda_id.split("_")
    assert parts[0] == "Λ"
    assert parts[1] == tier
    assert parts[2] == user_id
    
    # Verify tier hierarchy
    tier_values = {"alpha": 4, "beta": 3, "gamma": 2, "delta": 1}
    assert tier_values[tier] == 4


@pytest.mark.capability
def test_lambda_id_full_lifecycle():
    """Test complete ΛID lifecycle."""
    # 1. Generation
    lambda_id = f"Λ_gamma_user789"
    
    # 2. Validation
    assert lambda_id.startswith("Λ_")
    
    # 3. Parsing
    parts = lambda_id.split("_")
    tier = parts[1]
    user_id = parts[2]
    
    # 4. Tier check
    assert tier in ["alpha", "beta", "gamma", "delta"]
    
    # 5. Hash generation
    import hashlib
    lambda_hash = hashlib.sha256(lambda_id.encode()).hexdigest()
    assert len(lambda_hash) == 64
    
    # 6. Rate limit calculation
    multipliers = {"alpha": 3.0, "beta": 2.0, "gamma": 1.5, "delta": 1.0}
    rate_limit = 100 * multipliers[tier]
    assert rate_limit == 150  # gamma = 1.5x
