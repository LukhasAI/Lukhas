"""Compatibility helpers for LUKHAS ΛiD naming across the codebase.

🎯 **CRITICAL UNDERSTANDING**: Λ = LUKHAS, not Lambda!

The confusion in this codebase came from misinterpreting the Λ symbol:
- ❌ WRONG: "lambda_id" (misunderstood Λ as mathematical lambda)
- ❌ WRONG: "lambd_id" (typo of the wrong interpretation)
- ✅ CORRECT: "lukhas_id" or "lid" (Λ represents LUKHAS)

This compatibility layer handles ALL naming variants during the migration
to the correct LUKHAS identity system naming.

MIGRATION PRIORITIES:
1. Internal code: Use 'lid' (clean, short)
2. Database fields: Use 'user_lid' (descriptive)
3. API responses: Include both 'lid' and legacy keys for compatibility
4. Customer-facing: Display as 'ΛiD' (Λ = LUKHAS symbol)
"""

from collections.abc import Mapping
from typing import Any, Optional


def canonicalize_id_from_kwargs(kwargs: Mapping[str, Any]) -> Optional[str]:
    """Return canonical `lid` value from ANY naming variant.

    🎯 COMPREHENSIVE MIGRATION SUPPORT: Handles ALL discovered naming patterns
    
    Preference order (most correct → legacy variants):
    1. `lid` - CORRECT: Short form of LUKHAS ID
    2. `lukhas_id` - CORRECT: Full descriptive name  
    3. `user_lid` - CORRECT: Database/API variant
    4. `l_id` - Acceptable: Short alternative
    5. Legacy variants (will be deprecated):
       - `lambda_id` - WRONG: Misunderstood Λ as Lambda
       - `lambd_id` - WRONG: Typo of wrong interpretation
       - `user_id` - Generic: Ambiguous fallback
    """
    if not kwargs:
        return None

    # Preference order: Correct names first, then legacy/wrong names for compatibility
    for key in (
        # CORRECT NAMING (preferred)
        "lid",                    # ✅ Canonical short form
        "lukhas_id",              # ✅ Full LUKHAS ID name  
        "user_lid",               # ✅ Database/API variant
        "l_id",                   # ✅ Alternative short form
        "_l_id",                  # ✅ Private variant
        
        # LEGACY/WRONG NAMING (deprecated, for compatibility only)
        "lambda_id",              # ❌ Wrong interpretation of Λ
        "_lambda_id",             # ❌ Private wrong variant
        "lambd_id",               # ❌ Typo of wrong interpretation  
        "lambd",                  # ❌ Shorter typo variant
        "_lambd",                 # ❌ Private typo variant
        
        # GENERIC FALLBACK
        "user_id",                # ⚠️ Generic, ambiguous
    ):
        value = kwargs.get(key)
        if value:
            return value

    return None


def ensure_both_id_keys(obj: dict[str, Any], lid: Optional[str]) -> None:
    """Ensure the mapping `obj` contains both `lid` and `lambda_id` keys.

    This is useful when returning data to callers that may expect the
    historical JSON key `lambda_id` while internal logic uses `lid`.
    """
    if lid is None:
        return

    # Canonical short name
    obj.setdefault("lid", lid)

    # Backwards-compatible historical key
    obj.setdefault("lambda_id", lid)


def normalize_output_ids(obj: dict[str, Any]) -> None:
    """Normalize an output mapping so it contains all expected ID keys.

    🎯 COMPREHENSIVE COMPATIBILITY: Ensures API responses include both
    correct naming (lid) and legacy naming for smooth client migration.
    
    Use this before returning JSON responses so callers receive all keys
    and clients can migrate at their own pace.
    """
    if not obj:
        return

    # Extract the canonical ID from any variant
    canonical_lid = canonicalize_id_from_kwargs(obj)
    if not canonical_lid:
        return
        
    # Ensure ALL expected keys are populated for maximum compatibility
    obj.setdefault("lid", canonical_lid)              # ✅ Canonical
    obj.setdefault("lukhas_id", canonical_lid)        # ✅ Full name
    obj.setdefault("user_lid", canonical_lid)         # ✅ Database variant
    
    # Legacy compatibility (will be deprecated)
    obj.setdefault("lambda_id", canonical_lid)        # ❌ Legacy wrong name
    obj.setdefault("user_id", canonical_lid)          # ⚠️ Generic fallback


def normalize_user_identifier(**kwargs) -> Optional[str]:
    """
    Universal LUKHAS ID normalization function.
    
    🎯 ONE FUNCTION TO HANDLE ALL VARIANTS
    
    Accepts any combination of naming variants and returns the canonical `lid`.
    Use this in function signatures to accept maximum flexibility:
    
    Example:
        def authenticate_user(lid=None, user_id=None, lambda_id=None, **kwargs):
            canonical_lid = normalize_user_identifier(
                lid=lid, user_id=user_id, lambda_id=lambda_id, **kwargs
            )
            if not canonical_lid:
                raise ValueError("No valid LUKHAS ID provided")
            return canonical_lid
    """
    return canonicalize_id_from_kwargs(kwargs)


def get_display_name(lid: str) -> str:
    """
    Get customer-facing display name for a LUKHAS ID.
    
    Returns the proper ΛiD format where Λ represents LUKHAS.
    Use this for UI displays, customer communications, etc.
    """
    if not lid:
        return ""
        
    # For now, just return "ΛiD" - could be enhanced to show tier, etc.
    return f"ΛiD ({lid[:8]}...)"  # Show first 8 chars for identification


def is_valid_lukhas_id_format(identifier: str) -> bool:
    """
    Basic format validation for LUKHAS IDs.
    
    🎯 FORMAT VALIDATION: Checks if identifier follows LUKHAS ID patterns
    
    Valid patterns:
    - T{0-5}-{symbol}-{hash}-{random} (new format)
    - Legacy formats (for compatibility)
    """
    if not isinstance(identifier, str) or not identifier:
        return False
        
    # Check for new LUKHAS ID format: T{tier}-{symbol}-{hash}-{random}
    parts = identifier.split("-")
    if len(parts) == 4:
        tier_part, symbolic_part, hash_part, random_part = parts
        
        # Validate tier part
        if (tier_part.startswith("T") and 
            len(tier_part) == 2 and 
            tier_part[1:].isdigit() and 
            0 <= int(tier_part[1:]) <= 5):
            return True
    
    # For legacy format during migration, be more restrictive
    # Must have some structure (contains hyphens or underscores) and reasonable length
    return (len(identifier) >= 8 and 
            ("-" in identifier or "_" in identifier or identifier.isalnum()))

