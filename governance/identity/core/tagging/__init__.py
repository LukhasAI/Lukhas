"""
Identity Tagging System

Trust network-based tagging with consensus mechanisms and
tier-aware permission resolution.
"""

from .identity_tag_resolver import (
    IdentityTagResolver,
    IdentityTagType,
    TrustLevel,
    TrustRelationship,
    IdentityTag
)

__all__ = [
    'IdentityTagResolver',
    'IdentityTagType',
    'TrustLevel',
    'TrustRelationship',
    'IdentityTag'
]