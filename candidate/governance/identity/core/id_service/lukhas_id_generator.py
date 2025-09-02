"""
LUKHAS ΛiD Generator - Core Implementation
==========================================

🎯 **CRITICAL**: Λ = LUKHAS, not Lambda!

Core ΛiD generation logic with tier management, format handling, and hash generation.
Generates unique, symbolic, and tier-appropriate LUKHAS identities.

Features:
- Tier-based ID generation (0-5)
- Symbolic character integration
- Hash-based uniqueness
- Collision prevention
- Entropy scoring
- Format validation

This is the REAL implementation - previous lambda_id/lambd_id naming was incorrect.

Author: LUKHAS AI Systems
Created: 2025-09-02 (Corrected Naming)
"""

import hashlib
import json
import secrets
import time
from datetime import datetime
from enum import Enum
from typing import Optional


class UserContext:
    """User context for LUKHAS ID generation."""

    def __init__(self, user_id=None, metadata=None):
        self.user_id = user_id
        self.metadata = metadata or {}

    def to_dict(self):
        return {"user_id": self.user_id, "metadata": self.metadata}


class TierLevel(Enum):
    """LUKHAS Identity Access Tiers"""
    
    GUEST = 0        # Temporary access
    FRIEND = 1       # Basic authenticated
    TRUSTED = 2      # Verified identity  
    PREMIUM = 3      # Enhanced features
    ENTERPRISE = 4   # Business accounts
    FOUNDER = 5      # Special access


class LukhasIDGenerator:
    """
    LUKHAS ΛiD Generator - The Real Implementation
    
    🎯 **CORRECT NAMING**: This replaces the confused lambda_id/lambd_id implementations
    """
    
    def __init__(self):
        """Initialize LUKHAS ID generator with secure defaults"""
        self.generation_stats = {
            "total_generated": 0,
            "by_tier": {tier: 0 for tier in TierLevel},
            "collisions_prevented": 0,
            "entropy_scores": []
        }
        self.used_ids = set()
        
    def generate_lukhas_id(
        self, 
        tier: TierLevel = TierLevel.FRIEND,
        user_context: Optional[dict] = None,
        symbolic_preference: Optional[str] = None
    ) -> str:
        """
        Generate a unique LUKHAS ΛiD
        
        Args:
            tier: Access tier level (T0-T5)
            user_context: User metadata for personalization
            symbolic_preference: Preferred symbolic character
            
        Returns:
            Unique LUKHAS ΛiD string
        """
        attempt = 0
        max_attempts = 100
        
        while attempt < max_attempts:
            # Generate base components
            timestamp = int(time.time() * 1000000)  # Microsecond precision
            random_component = secrets.token_hex(8)
            
            # Add tier prefix
            tier_prefix = f"T{tier.value}"
            
            # Generate symbolic component
            symbolic = self._get_symbolic_character(symbolic_preference, tier)
            
            # Create unique hash from context
            context_hash = self._hash_context(user_context, timestamp, random_component)
            
            # Construct the LUKHAS ID
            lukhas_id = f"{tier_prefix}-{symbolic}-{context_hash[:8]}-{random_component[:6]}"
            
            # Check for uniqueness
            if lukhas_id not in self.used_ids:
                self.used_ids.add(lukhas_id)
                self._update_stats(tier, lukhas_id)
                return lukhas_id
                
            attempt += 1
            self.generation_stats["collisions_prevented"] += 1
            
        raise RuntimeError(f"Failed to generate unique LUKHAS ID after {max_attempts} attempts")
    
    def _get_symbolic_character(self, preference: Optional[str], tier: TierLevel) -> str:
        """Get appropriate symbolic character for tier"""
        if preference and len(preference) == 1:
            return preference
            
        # Default symbolic characters by tier
        tier_symbols = {
            TierLevel.GUEST: "◦",      # Open circle - temporary
            TierLevel.FRIEND: "●",     # Filled circle - established  
            TierLevel.TRUSTED: "◆",    # Diamond - verified
            TierLevel.PREMIUM: "★",    # Star - enhanced
            TierLevel.ENTERPRISE: "⬢", # Hexagon - business
            TierLevel.FOUNDER: "Λ"     # Lambda - LUKHAS symbol
        }
        
        return tier_symbols.get(tier, "●")
    
    def _hash_context(self, user_context: Optional[dict], timestamp: int, random_component: str) -> str:
        """Create secure hash from user context"""
        context_data = {
            "timestamp": timestamp,
            "random": random_component,
            "context": user_context or {},
            "generator_version": "lukhas_v1.0"
        }
        
        context_json = json.dumps(context_data, sort_keys=True)
        return hashlib.sha256(context_json.encode()).hexdigest()
    
    def _update_stats(self, tier: TierLevel, lukhas_id: str) -> None:
        """Update generation statistics"""
        self.generation_stats["total_generated"] += 1
        self.generation_stats["by_tier"][tier] += 1
        
        # Calculate basic entropy score
        entropy = len(set(lukhas_id)) / len(lukhas_id)
        self.generation_stats["entropy_scores"].append(entropy)
    
    def validate_lukhas_id_format(self, lukhas_id: str) -> dict:
        """Validate LUKHAS ID format"""
        if not isinstance(lukhas_id, str):
            return {"valid": False, "reason": "ID must be string"}
            
        parts = lukhas_id.split("-")
        if len(parts) != 4:
            return {"valid": False, "reason": "ID must have 4 parts separated by hyphens"}
            
        tier_part, symbolic_part, hash_part, random_part = parts
        
        # Validate tier
        if not tier_part.startswith("T") or not tier_part[1:].isdigit():
            return {"valid": False, "reason": "Invalid tier format"}
            
        tier_num = int(tier_part[1:])
        if tier_num < 0 or tier_num > 5:
            return {"valid": False, "reason": "Tier must be 0-5"}
            
        # Validate lengths
        if len(symbolic_part) != 1:
            return {"valid": False, "reason": "Symbolic part must be 1 character"}
            
        if len(hash_part) != 8:
            return {"valid": False, "reason": "Hash part must be 8 characters"}
            
        if len(random_part) != 6:
            return {"valid": False, "reason": "Random part must be 6 characters"}
            
        return {
            "valid": True,
            "tier": tier_num,
            "symbolic": symbolic_part,
            "hash": hash_part,
            "random": random_part
        }
    
    def get_generation_stats(self) -> dict:
        """Get generation statistics"""
        stats = self.generation_stats.copy()
        if stats["entropy_scores"]:
            stats["average_entropy"] = sum(stats["entropy_scores"]) / len(stats["entropy_scores"])
        else:
            stats["average_entropy"] = 0.0
            
        return stats


# Backward compatibility aliases (will be phased out)
LambdaIDGenerator = LukhasIDGenerator  # Legacy alias
LambdIDGenerator = LukhasIDGenerator   # Legacy typo alias


# Export main classes
__all__ = [
    "LukhasIDGenerator",    # CORRECT: New standard name
    "TierLevel", 
    "UserContext",
    # Legacy aliases (deprecated)
    "LambdaIDGenerator",    # DEPRECATED: Was wrong interpretation
    "LambdIDGenerator",     # DEPRECATED: Was typo of wrong interpretation
]


# Example usage and testing
if __name__ == "__main__":
    generator = LukhasIDGenerator()

    # Generate ΛiDs for different tiers
    print("🌟 LUKHAS ΛiD Generator - Corrected Implementation")
    print("=" * 55)
    
    for tier in TierLevel:
        lukhas_id = generator.generate_lukhas_id(tier)
        validation = generator.validate_lukhas_id_format(lukhas_id)
        print(f"Tier {tier.value} ({tier.name:10}): {lukhas_id} ✓" if validation["valid"] else f"Tier {tier.value}: INVALID")

    # Generate with user context
    user_context = {
        "email": "user@lukhas.ai",
        "registration_time": time.time(),
        "preferences": {"symbolic_style": "mystical"},
    }

    personalized_id = generator.generate_lukhas_id(TierLevel.TRUSTED, user_context, symbolic_preference="🌀")
    print(f"\nPersonalized ΛiD: {personalized_id}")
    
    stats = generator.get_generation_stats()
    print(f"\nGeneration Stats:")
    print(f"  Total Generated: {stats['total_generated']}")
    print(f"  Average Entropy: {stats['average_entropy']:.3f}")
    print(f"  Collisions Prevented: {stats['collisions_prevented']}")