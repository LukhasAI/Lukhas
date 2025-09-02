#!/usr/bin/env python3
"""
Test Suite: LUKHAS ΛiD Naming Standardization
=============================================

🎯 **CRITICAL**: Λ = LUKHAS, not Lambda!

This test suite validates the complete naming standardization that corrects
the fundamental misunderstanding where Λ was interpreted as Lambda instead
of representing LUKHAS.

Test Coverage:
- Correct LUKHAS ID generation (lukhas_id_generator.py)
- Legacy compatibility (lambda_id/lambd_id wrappers)
- Universal ID normalization functions
- Authentication flow standardization
"""

import pytest
from unittest.mock import patch
import warnings


def test_lukhas_id_generator():
    """Test the correct LUKHAS ID generator implementation"""
    from candidate.governance.identity.core.id_service.lukhas_id_generator import (
        LukhasIDGenerator, TierLevel
    )
    
    generator = LukhasIDGenerator()
    
    # Test correct LUKHAS ID generation
    lukhas_id = generator.generate_lukhas_id(TierLevel.TRUSTED)
    assert lukhas_id.startswith("T2-"), f"Expected T2- prefix for TRUSTED tier, got: {lukhas_id}"
    assert lukhas_id.count("-") == 3, f"Expected 4 parts separated by hyphens, got: {lukhas_id}"
    
    # Test Founder tier uses Λ symbol (LUKHAS symbol, not Lambda!)
    founder_id = generator.generate_lukhas_id(TierLevel.FOUNDER)
    assert "T5-Λ-" in founder_id, f"Founder tier should use Λ (LUKHAS symbol), got: {founder_id}"
    
    # Test validation
    validation = generator.validate_lukhas_id_format(lukhas_id)
    assert validation["valid"], f"Generated ID should be valid: {validation}"
    

def test_legacy_compatibility_with_deprecation_warnings():
    """Test that legacy imports work but show deprecation warnings"""
    
    # Test lambda_id import (wrong interpretation of Λ)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        from candidate.governance.identity.core.id_service.lambda_id_generator import LambdaIDGenerator
        
        # Should have deprecation warning (may be multiple due to import cascading)
        assert len(w) >= 1
        lambda_warnings = [warning for warning in w if "Λ=LUKHAS, not Lambda!" in str(warning.message)]
        assert len(lambda_warnings) >= 1
        assert issubclass(lambda_warnings[0].category, DeprecationWarning)
    
    # Test lambd_id import (typo of wrong interpretation)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always") 
        from candidate.governance.identity.core.id_service.lambd_id_generator import LambdIDGenerator
        
        # Should have deprecation warning
        assert len(w) == 1
        assert "Λ=LUKHAS, not Lambda!" in str(w[0].message)
        

def test_universal_id_normalization():
    """Test the universal ID normalization functions"""
    from lukhas.identity.compat import (
        normalize_user_identifier, 
        canonicalize_id_from_kwargs,
        normalize_output_ids,
        get_display_name,
        is_valid_lukhas_id_format
    )
    
    # Test preference order: correct names first
    lid = normalize_user_identifier(
        lambda_id="wrong-interpretation", 
        lid="correct-canonical",
        user_id="generic-fallback"
    )
    assert lid == "correct-canonical", "Should prioritize 'lid' over legacy variants"
    
    # Test lukhas_id preference over lambda_id
    lid2 = normalize_user_identifier(
        lambda_id="wrong-interpretation",
        lukhas_id="correct-full-name"
    )
    assert lid2 == "correct-full-name", "Should prioritize 'lukhas_id' over 'lambda_id'"
    
    # Test database variant
    lid3 = normalize_user_identifier(user_lid="db-style-id")
    assert lid3 == "db-style-id", "Should handle user_lid database variant"
    
    # Test comprehensive output normalization
    response = {"lambda_id": "legacy-id"}
    normalize_output_ids(response)
    
    assert response["lid"] == "legacy-id", "Should populate canonical 'lid'"
    assert response["lukhas_id"] == "legacy-id", "Should populate 'lukhas_id'"
    assert response["user_lid"] == "legacy-id", "Should populate 'user_lid'"
    
    # Test display name formatting (customer-facing ΛiD)
    display = get_display_name("T3-★-abc12345-xyz789")
    assert "ΛiD" in display, "Display should show Λ (LUKHAS symbol)"
    assert "T3-★-abc" in display, "Display should show ID preview"
    
    # Test format validation
    valid_id = "T3-★-abc12345-xyz789"
    assert is_valid_lukhas_id_format(valid_id), "Should validate correct LUKHAS ID format"
    
    invalid_id = "bad"  # Too short, no structure
    assert not is_valid_lukhas_id_format(invalid_id), "Should reject malformed IDs"
    

def test_authentication_flow_standardization():
    """Test that authentication flows use correct lid parameter"""
    from candidate.governance.identity.auth_integrations.wallet_bridge import create_wallet_bridge
    
    bridge = create_wallet_bridge()
    
    # Test async authentication method signature uses 'lid' parameter
    import inspect
    sig = inspect.signature(bridge.authenticate_with_wallet)
    assert 'lid' in sig.parameters, "Auth functions should use 'lid' parameter, not 'user_id'"
    
    # Function should not have 'user_id' parameter anymore
    assert 'user_id' not in sig.parameters, "Auth functions should not use deprecated 'user_id'"


def test_no_circular_imports():
    """Test that circular import issue is resolved"""
    
    # These should all import without circular dependency errors
    # Suppress expected deprecation warnings for this test
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            from candidate.governance.identity.core.id_service.lukhas_id_generator import LukhasIDGenerator
            from candidate.governance.identity.core.id_service.lambda_id_generator import LambdaIDGenerator  
            from candidate.governance.identity.core.id_service.lambd_id_generator import LambdIDGenerator
            
            # All should reference the same real implementation
            lukhas_gen = LukhasIDGenerator()
            lambda_gen = LambdaIDGenerator()  # Legacy alias
            lambd_gen = LambdIDGenerator()    # Legacy typo alias
            
            # Generate IDs to verify they all work
            id1 = lukhas_gen.generate_lukhas_id()
            id2 = lambda_gen.generate_lukhas_id()  # Should work via alias
            id3 = lambd_gen.generate_lukhas_id()   # Should work via alias
            
            # All should generate valid LUKHAS IDs
            assert lukhas_gen.validate_lukhas_id_format(id1)["valid"]
            assert lukhas_gen.validate_lukhas_id_format(id2)["valid"]
            assert lukhas_gen.validate_lukhas_id_format(id3)["valid"]
            
        except ImportError as e:
            pytest.fail(f"Circular import detected: {e}")


def test_comprehensive_migration_scenario():
    """Test a complete migration scenario from old to new naming"""
    from lukhas.identity.compat import normalize_user_identifier, normalize_output_ids
    
    # Simulate old API call with wrong naming
    old_api_data = {
        "lambda_id": "legacy-misunderstood-id",  # Wrong interpretation of Λ
        "user_data": {"email": "user@lukhas.ai"}
    }
    
    # Extract and normalize the ID
    canonical_lid = normalize_user_identifier(**old_api_data)
    assert canonical_lid == "legacy-misunderstood-id"
    
    # Prepare response with all naming variants for compatibility  
    response = {"user_data": old_api_data["user_data"], "lid": canonical_lid}
    normalize_output_ids(response)
    
    # Response should include all expected keys
    assert response["lid"] == canonical_lid             # Canonical
    assert response["lukhas_id"] == canonical_lid       # Full name
    assert response["user_lid"] == canonical_lid        # Database variant
    assert response["lambda_id"] == canonical_lid       # Legacy (wrong)
    assert response["user_id"] == canonical_lid         # Generic fallback
    
    # This allows clients to migrate at their own pace while we standardize internally


if __name__ == "__main__":
    print("🌟 LUKHAS ΛiD Naming Standardization Test Suite")
    print("=" * 55)
    print("🎯 Testing the correction: Λ = LUKHAS, not Lambda!")
    print()
    
    # Run the tests
    test_lukhas_id_generator()
    print("✅ LUKHAS ID Generator: Working correctly")
    
    test_legacy_compatibility_with_deprecation_warnings()
    print("✅ Legacy Compatibility: Warns about wrong interpretation")
    
    test_universal_id_normalization()
    print("✅ Universal Normalization: Handles all naming variants")
    
    test_authentication_flow_standardization()
    print("✅ Auth Standardization: Using canonical 'lid' parameter")
    
    test_no_circular_imports()
    print("✅ Import Resolution: No circular dependency issues")
    
    test_comprehensive_migration_scenario()
    print("✅ Migration Support: Smooth transition from legacy naming")
    
    print()
    print("🎉 ALL TESTS PASSED!")
    print("🌟 LUKHAS Identity System: Properly standardized")
    print("💡 Λ = LUKHAS (not Lambda) - naming crisis resolved!")